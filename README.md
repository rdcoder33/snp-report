# Gene Report FastAPI Streaming API

## Install dependencies

```bash
pip install -r requirements.txt
```

## create a .env file for these keys:

```bash
OPENAI_API_KEY=<open_ai_key>
PPLX_API_KEY=<perplexity_key>
```

## Run the FastAPI server

```bash
venv/bin/uvicorn api:app  --reload

or

venv/bin/uvicorn api:app 
```

## Usage

POST to `/stream-report` with JSON body:

```json
{
  "file_content": "<file_content>",
  "user_profile": "",
  "file_type": "text_23andme"
}
```

Example using `curl` (with SSE client):

```bash
curl -N -X POST -H "Content-Type: application/json" 
  -d '{  "file_content": "<file_content>",
  "user_profile": "<add a user profile in text>",
  "file_type": "text_23andme"}' 
  http://localhost:8000/stream-report
```

The response will be streamed as Server-Sent Events (SSE) with agent updates. 

# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

---

## What works

- Can only take 23andMe style text file genetic report, uploaded from local storage
- Calls Clinvar, MyVariant and Ensembl REST APIs for grounding data
- Uses perplexity to find citations and articles for the report
- Provide SNP / Category wise report
- Tries to provide Report in Structure and Easy to understand language
- Uses FASTAPI to stream the AI Agent updates
- Have dynamic LLM generated UI shown in Vue Webpage
- Takes around 4-5 minutes to finish

## What doesn’t work yet

- Genetic Reports in other formats: VCF, CSV etc.
- Takes time to generate report
- Report’s structure and quality is not consistent
- The report frontend is not fully dynamic, instead of showing a section as soon as it is finished, it waits for all sections to complete
- Need to make Header and Footer dynamic with patient details and current date
- Source clicking link not working, since UI is in iframe (I am new to Vue JS)

## Things I want to Improve

- More Information in the report: How Common is the Variant, Better flow for getting citations, Explanation Tab for technical words.
- Currently using external API, should build our own Vector DB for Genetic Data, will improve both speed and accuracy.
- Prompts need to be improved, structured and evaluated across different data. Maybe use BAML Framework for prompts.
- Need to build a large domain knowledge to act as a guard-rails and structure for the Report Output.
- Need to add Human-Made Reports Example to do few shots generations.
- Definitely the UI can be lot better
- More Chart, Graphs and Tables.

## Stack

- Python for Backend
- Langgraph for Agent Flow and State
- Langchain for custom Tools
- OpenAI, Perplexity
- Tailwind CSS for Report UI
- Vue JS for Web page
