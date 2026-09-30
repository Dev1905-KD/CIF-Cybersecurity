import re


def extract_cve(query):
    """
    Extract a CVE identifier from the user query.
    """

    pattern = r"CVE-\d{4}-\d{4,7}"

    match = re.search(
        pattern,
        query,
        re.IGNORECASE
    )

    if match:
        return match.group(0).upper()

    return None


def process_query(query):

    return {
        "original_query": query,
        "cve": extract_cve(query)
    }