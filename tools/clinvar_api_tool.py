import requests
import xml.etree.ElementTree as ET

def fetch_clinvar_xml_by_rsids(rsid_list):
    """
    For each rsID in rsid_list, fetch ClinVar VCV XML data using NCBI E-utilities.
    Args:
        rsid_list (list): List of rsID strings (e.g., ["rs6323", ...])
    Returns:
        dict: Mapping of rsID to list of XML response strings (one per ClinVar Variation ID)
    """
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    results = {}
    for rsid in rsid_list:
        esearch_params = {
            "db": "clinvar",
            "term": rsid,
            "retmode": "json"
        }
        esearch_response = requests.get(esearch_url, params=esearch_params)
        esearch_data = esearch_response.json()
        clinvar_ids = esearch_data.get("esearchresult", {}).get("idlist", [])
        xml_list = []
        for clinvar_id in clinvar_ids:
            efetch_params = {
                "db": "clinvar",
                "rettype": "vcv",
                "is_variationid": "true",
                "id": clinvar_id
            }
            efetch_response = requests.get(efetch_url, params=efetch_params)
            if efetch_response.ok:
                xml_list.append(efetch_response.text)
        results[rsid] = xml_list
    return results
