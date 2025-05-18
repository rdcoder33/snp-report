import requests

def fetch_vep_by_rsid(rsid_list):
    """
    Fetch VEP prediction data for a list of rsIDs from Ensembl REST API.
    Args:
        rsid_list (list): List of rsID strings (e.g., ['rs56116432', ...]).
    Returns:
        list: List of dicts (parsed JSON data) for each rsID, or None if not found.
    """
    server = "https://rest.ensembl.org"
    headers = {"Content-Type": "application/json"}
    results = []
    for rsid in rsid_list:
        ext = f"/vep/human/id/{rsid}?"
        response = requests.get(server + ext, headers=headers)
        if response.ok:
            results.append(response.json())
        else:
            results.append(None)
    return results
