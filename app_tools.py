from langchain.tools import BaseTool
from pydantic import BaseModel
from typing import Any
from cyvcf2 import VCF
import pandas as pd
from tools.variant_api_tool import fetch_variants_by_rsid
from tools.clinvar_api_tool import fetch_clinvar_xml_by_rsids
from tools.vep_api_tool import fetch_vep_by_rsid
from time import sleep
import logging



# Input schema for VCF parsing
default_vcf_path = '/Users/winkltechnologies/Desktop/gene-report/data/genome_Joshua_Yoakem_v5_Full_20250129211749.txt'


class ParseVCFTool(BaseTool):
    name: str = "parse_vcf_file"
    description: str = "Parses a VCF file content (string) and returns a pandas DataFrame with variant information."
     

    def _run(self, file_content: str) -> Any:
        """Parse a VCF file content (string) and return a pandas DataFrame with variant information."""
        from io import StringIO
        max_retries = 3
        for attempt in range(max_retries):
            try:
                vcf = VCF(StringIO(file_content))
                records = []
                for variant in vcf:
                    rec = {
                        'chrom': variant.CHROM,
                        'pos': variant.POS,
                        'id': variant.ID,
                        'ref': variant.REF,
                        'alt': ','.join(variant.ALT),
                        'qual': variant.QUAL,
                        'filter': variant.FILTER,
                        'gt': variant.genotypes[0]  # e.g. [0,1,True]
                    }
                    records.append(rec)
                return {'variants': records}
            except Exception as e:
                logging.error(f"ParseVCFTool attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(1)
                else:
                    return {"error": f"Failed to parse VCF file after {max_retries} attempts: {str(e)}"}

 

class Parse23andMeTool(BaseTool):
    name: str = "parse_23andme_file"
    description: str = "Parses a 23andMe raw data file content (string) and returns a pandas DataFrame."
    

    def _run(self, file_content: str) -> Any:
        """Parse a 23andMe raw data file content (string) and return a pandas DataFrame."""
        from io import StringIO
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df_23 = pd.read_csv(
                    StringIO(file_content),
                    sep='\t',
                    comment='#',
                    header=None,
                    names=['rsid', 'chromosome', 'position', 'genotype']
                )
                return df_23.to_dict(orient="records")
            except Exception as e:
                logging.error(f"Parse23andMeTool attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(1)
                else:
                    return {"error": f"Failed to parse 23andMe file after {max_retries} attempts: {str(e)}"}


class VariantAPITool(BaseTool):
    name: str = "variant_api_tool"
    description: str = "Fetches variant information for a list of rsIDs using myvariant.info. Input: list of rsID strings. Output: list of variant info dicts."

    def _run(self, rs_ids: list) -> Any:
        """Fetch variant information for a list of rsIDs using myvariant.info."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return fetch_variants_by_rsid(rs_ids)
            except Exception as e:
                logging.error(f"VariantAPITool attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(1)
                else:
                    return {"error": f"Failed to fetch variant info after {max_retries} attempts: {str(e)}"}


class ClinvarAPITool(BaseTool):
    name: str = "clinvar_api_tool"
    description: str = "Fetches ClinVar XML data for a list of rsIDs using NCBI E-utilities. Input: list of rsID strings. Output: dict mapping rsID to XML response strings."

    def _run(self, rsid_list: list) -> Any:
        """Fetch ClinVar XML data for a list of rsIDs using NCBI E-utilities."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return fetch_clinvar_xml_by_rsids(rsid_list)
            except Exception as e:
                logging.error(f"ClinvarAPITool attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(1)
                else:
                    return {"error": f"Failed to fetch ClinVar XML after {max_retries} attempts: {str(e)}"}


class VEPAPITool(BaseTool):
    name: str = "vep_api_tool"
    description: str = "Fetches VEP prediction data for a list of rsIDs from Ensembl REST API. Input: list of rsID strings. Output: list of dicts (parsed JSON data)."

    def _run(self, rsid_list: list) -> Any:
        """Fetch VEP prediction data for a list of rsIDs from Ensembl REST API."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return fetch_vep_by_rsid(rsid_list)
            except Exception as e:
                logging.error(f"VEPAPITool attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    sleep(1)
                else:
                    return {"error": f"Failed to fetch VEP data after {max_retries} attempts: {str(e)}"}

