import re
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from enum import Enum
import time

from llm_client import strict_llm, chat_perplexity, creative_llm

from prompts import perplexity_search_prompt, select_file_type_prompt, generate_category_prompt, report_section_prompt, report_ui_prompt

from app_tools import ParseVCFTool, Parse23andMeTool, VariantAPITool, ClinvarAPITool, VEPAPITool

import json

import asyncio

import functools
import random


class GenomeFileType(Enum):
    VCF = "type_vcf"
    TXT23ANDME = "type_23andme"

    @classmethod
    def type_values(cls):
        return [e.value for e in cls]


class GenomeFileTypeModel(BaseModel):
    file_type: str


class ConfidenceModel(BaseModel):
    confidence: int = Field(
        None, description="Create a confidence score between 0 and 10 based on the confidence in the data")
    risk_level: str = Field(
        None, description="How much risk does this variant pose to the user's health, score between 0 and 10")


class SNPDataModel(BaseModel):
    variant_description: str = Field(
        None, description="Description of the variants, Known variants data, must include ClinVar, SNPedia, gnomAD data, commanality and difference in them, the test and what does these vairants do.")

    known_effect: str = Field(
        None, description="What is the known effects of the variants, if any")
    takeaways: str = Field(
        None, description="Are there practical takeaways or actions the user might consider")
    confidence: ConfidenceModel = Field(
        None, description="Give a confidence score and risk level for the variants")
    citations: List[str] = Field(
        None, description="List of citations for the variants")


class ReportResponse(BaseModel):
    template_html_css: str = Field(
        None, description="HTML and Tailwind CSS")


class AgentState(BaseModel):
    file_content: str = Field(None, description="Path to the genetic data file.")
    file_type: str = Field(
        "type_23andme", description=f"Data type of the genetic data file: {GenomeFileType.type_values()}.")
    raw_data: Dict[str, Any] = Field(
        None, description="Parsed raw data from the genetic file.")
    extracted_target_snps: Dict[str, Any] = Field(
        default_factory=dict, description="Subset of high-signal SNPs extracted from raw data.")
    current_action: str = Field(
        None, description="Current action being performed by the agent.")
    snp_data: Dict[str, List[SNPDataModel]] = Field(
        None, description="Detailed data for each SNP.")
    report_sections_ui: List[str] = Field(
        [], description="Different sections of the report, with HTML and Tailwind CSS UI")
    final_report_ui: str = Field(
        None, description="Final report with all sections of the report, with HTML and Tailwind CSS UI")
    user_profile: str = Field(
        None, description="Background information about the user, their family history, and their health goals.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_content": self.file_content,
            "file_type": self.file_type,
            "raw_data": self.raw_data,
            "current_action": self.current_action,
            "snp_data": self.snp_data,
            "extracted_target_snps": self.extracted_target_snps,
            "report_sections_ui": self.report_sections_ui,
            "final_report_ui": self.final_report_ui,
            "user_profile": self.user_profile
        }


def parse_data_node(state: AgentState):
    """Select and Read the genetic data file (VCF or 23andMe) and loads into state.raw_data ."""

    if state.file_type == GenomeFileType.VCF.value:
        state.raw_data = ParseVCFTool().invoke({"file_content": state.file_content})

    elif state.file_type == GenomeFileType.TXT23ANDME.value:
        state.raw_data = Parse23andMeTool().invoke(
            {"file_content": state.file_content})

    state.current_action = "Parsing genetic data file..."
    return state


def extract_variants_node(state: AgentState):
    """Extract a subset of high-signal SNPs from raw_data, merge with target info, and categorize them."""

    import json

    # Load target SNPs
    with open('data/small_target.json', 'r') as file:
        target_snps = json.load(file)
        
    # target_snps = state.file_content # This line was causing the TypeError

    # Filter and merge matching SNPs
    merged_snps = []
    for snp in state.raw_data:
        rsid = snp['rsid']
        if rsid in target_snps:
            merged_entry = {
                **snp,
                **target_snps[rsid]
            }
            merged_snps.append(merged_entry)

    # Reorganize merged_snps by category
    categorized_snps = {}
    for snp_item in merged_snps:
        category = snp_item.get('category')
        if category:
            if category not in categorized_snps:
                categorized_snps[category] = []
            categorized_snps[category].append(snp_item)

    # Store the categorized SNPs in the state
    state.extracted_target_snps = categorized_snps
    state.current_action = f"Extracted {len(categorized_snps)} Categories of {len(merged_snps)} High Signal Variants"

    print(state.current_action)
    return state


# Replace [n] with corresponding citation URL


def replace_citations(text, citations):
    def citation_replacer(match):
        index = int(match.group(1)) - 1  # Convert 1-based to 0-based index
        if 0 <= index < len(citations):
            return f"[{citations[index]}]"
        return match.group(0)  # Return original if out of range

    return re.sub(r'\[(\d+)\]', citation_replacer, text)


# Retry helper for async functions
async def async_retry(func, *args, retries=3, initial_delay=1, backoff=2, **kwargs):
    delay = initial_delay
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"[Retry {attempt+1}/{retries}] Error: {e}")
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay + random.uniform(0, 0.5))
            delay *= backoff


# Retry helper for sync functions

def sync_retry(func, *args, retries=3, initial_delay=1, backoff=2, **kwargs):
    delay = initial_delay
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[Retry {attempt+1}/{retries}] Error: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(delay + random.uniform(0, 0.5))
            delay *= backoff


async def process_category_async(data: any, user_profile: str):
    """Helper coroutine to process a single category asynchronously."""
    start_time = time.time()
    llm_tool = creative_llm.bind_tools(
        [VariantAPITool(), ClinvarAPITool(), VEPAPITool()])

    report_llm = creative_llm.with_structured_output(SNPDataModel)

    # Use ainvoke for asynchronous calls with retry
    try:
        llm_tool_response, citations = await asyncio.gather(
            async_retry(llm_tool.ainvoke, perplexity_search_prompt.invoke({"data": data})),
            async_retry(get_citations, data)
        )
    except Exception as e:
        print(f"Failed to get LLM tool response or citations after retries: {e}")
        return "<div class='text-red-500'>Error generating report section.</div>"

    tool_results = []
    for tool_call in llm_tool_response.tool_calls:
        try:
            if tool_call["name"] == "variant_api_tool":
                result = sync_retry(VariantAPITool().invoke, tool_call["args"])
            elif tool_call["name"] == "clinvar_api_tool":
                result = sync_retry(ClinvarAPITool().invoke, tool_call["args"])
            elif tool_call["name"] == "vep_api_tool":
                result = sync_retry(VEPAPITool().invoke, tool_call["args"])
            else:
                result = None
        except Exception as e:
            print(f"Error in tool call {tool_call['name']}: {e}")
            result = {"error": str(e)}
        tool_results.append({
            "tool_name": tool_call["name"],
            "result": result
        })

    # This depends on your framework. In LangChain, you might do:
    try:
        final_response = sync_retry(report_llm.invoke, report_section_prompt.invoke(
            {"data": tool_results,
             "user_profile": user_profile,
             "citations": citations}))
    except Exception as e:
        print(f"Error in report_llm.invoke: {e}")
        return "<div class='text-red-500'>Error generating report section.</div>"

    ui_llm = creative_llm.with_structured_output(ReportResponse)
    try:
        html_ui = sync_retry(ui_llm.invoke, report_ui_prompt.invoke(
            {"data": final_response}))
    except Exception as e:
        print(f"Error in ui_llm.invoke: {e}")
        return "<div class='text-red-500'>Error generating report UI.</div>"
  
    return html_ui.template_html_css


async def get_citations(data: any):
    try:
        perplexity_resp = await async_retry(chat_perplexity.ainvoke, perplexity_search_prompt.invoke({"data": data}))
        perplexity_answer = replace_citations(
            str(perplexity_resp), perplexity_resp.additional_kwargs.get("citations", []))
        return perplexity_answer
    except Exception as e:
        print(f"Error in get_citations: {e}")
        return []


async def snp_data_node_async(state: AgentState):
    """Use LLM to annotate each variant asynchronously, updating state as each finishes."""
    print("Data extraction started (async)")
    start_time = time.time()

    tasks = []
    categories = list(state.extracted_target_snps.items())
    for category, snp in categories:
        tasks.append(process_category_async(snp, state.user_profile))

    for coro in asyncio.as_completed(tasks):
        result = await coro
        state.report_sections_ui.append(result)
        yield {"report_sections_ui": state.report_sections_ui}

    state.current_action = "Researched backed, genetic data extracted and annotated"
    end_time = time.time()
    print(f"Total time taken for snp_data_node (async): {end_time - start_time:.2f} seconds")
    # yield the final state as the last update
    yield state


async def snp_data_node(state: AgentState):
    final_state = None
    async for update in snp_data_node_async(state):
        final_state = update
    return final_state


def snp_data_node_sync(state: AgentState):
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Already in an event loop: schedule as a task and wait
        # This will return a coroutine/future, so caller must await
        return asyncio.ensure_future(snp_data_node(state))
    else:
        return asyncio.run(snp_data_node(state))

    


def generate_report_ui_node(state: AgentState):
    """Use LLM to generate a report for each category."""
    print("Generating report UI")
    ui_llm = creative_llm.with_structured_output(ReportResponse)
    try:
        resp = sync_retry(ui_llm.invoke, report_ui_prompt.invoke(
            {"data": state.snp_data}))
        state.final_report_ui = resp.template_html_css
        state.current_action = "Report Generated"
        print("Report UI generated")
    except Exception as e:
        print(f"Error in generate_report_ui_node: {e}")
        state.final_report_ui = "<div class='text-red-500'>Error generating final report UI.</div>"
        state.current_action = "Report Generation Failed"
    return state


memory = MemorySaver()

graph = StateGraph(AgentState)

PARSE_NODE="parse_input_node"
EXTRACT_VARIANTS_NODE="extract_variants_node"
SNPS_DATA_NODE="snp_data_node"
GENERATE_REPORT_UI_NODE="generate_report_ui"

graph.add_node(PARSE_NODE, parse_data_node)
graph.add_node(EXTRACT_VARIANTS_NODE, extract_variants_node)
graph.add_node(SNPS_DATA_NODE, snp_data_node_sync)
graph.add_node(GENERATE_REPORT_UI_NODE, generate_report_ui_node)

graph.add_edge(START, PARSE_NODE)
graph.add_edge(PARSE_NODE, EXTRACT_VARIANTS_NODE)
graph.add_edge(EXTRACT_VARIANTS_NODE, SNPS_DATA_NODE)
graph.add_edge(SNPS_DATA_NODE, GENERATE_REPORT_UI_NODE)
graph.add_edge(GENERATE_REPORT_UI_NODE, END)
# graph.add_edge("assemble_report", END)


def get_agent_and_state(file_content: str, user_profile: str = None, file_type: str = None):
    agent = graph.compile(checkpointer=memory)

    state = AgentState(file_content=file_content,user_profile=user_profile, file_type=file_type)
    return agent, state


if __name__ == "__main__":
    agent, state = get_agent_and_state(
        file_content="data/genome_Joshua_Yoakem_v5_Full_20250129211749.txt",
        file_type=str(GenomeFileType.TXT23ANDME.value)
    )
    config = {"configurable": {"thread_id": str(
        int(time.time() * 1000 + (time.time() % 1) * 1000))}}
    result = agent.invoke(state, config)
    print(result['report_sections_ui'])

    # Wrap your async code in a function
    async def debug_async_node():
        async for update in snp_data_node_async(state):
            print(update)

    # Run the async function
    asyncio.run(debug_async_node())