import myvariant

def fetch_variants_by_rsid(rs_ids):
    """
    Fetch variant information for a list of rsIDs using myvariant.
    Args:
        rs_ids (list): List of rsID strings (e.g., ["rs6323"]).
    Returns:
        list: List of variant information dictionaries.
    """
    mv = myvariant.MyVariantInfo()
    variants = mv.getvariants(rs_ids)
    return variants
