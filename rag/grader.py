
import re


STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on",
    "to", "for", "with", "from", "by", "about", "using",
    "used", "find", "identify", "investigate", "related",
    "evidence", "available", "details", "their", "its",
    "what", "which", "that", "this", "are", "is"
}


def extract_keywords(text):
    words = re.findall(r"\b[a-z0-9-]+\b", (text or "").lower())

    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def is_semantically_relevant(item, query, cve=None):

    claim = str(item.get("claim") or "").lower()

    entities = item.get("entities") or []

    entity_text = " ".join(
        str(value)
        for entity in entities
        for value in entity.values()
        if value is not None
    ).lower()

    searchable_text = claim + " " + entity_text

    if cve:
        return cve.lower() in searchable_text

    query_keywords = extract_keywords(query)
    evidence_keywords = extract_keywords(searchable_text)

    if len(query_keywords) < 2:
        return False

    matched = query_keywords & evidence_keywords

    return (
        len(matched) >= 2
        and len(matched) / len(query_keywords) >= 0.25
    )


def grade_retrieval(context):

    if not context:
        return {
            "score": 0,
            "status": "irrelevant",
            "reason": ["No context retrieved."]
        }

    query = context.get("query", "")
    cve = context.get("cve")

    score = 0
    reasons = []

    if cve:
        score += 1
        reasons.append("CVE identified")

    if context.get("description"):
        score += 1
        reasons.append("CVE description available")

    valid_products = [
        product for product in context.get("products", [])
        if product.get("product")
    ]

    if valid_products:
        score += 1
        reasons.append("Affected product found")

    graph_evidence = [
        item for item in context.get("evidence", [])
        if item.get("source") and item.get("claim")
    ]

    if graph_evidence:
        score += 1
        reasons.append("Graph evidence found")

    semantic_evidence = [
        item for item in context.get("semantic_evidence", [])
        if item.get("source")
        and item.get("claim")
        and isinstance(item.get("similarity"), (int, float))
    ]

    relevant_evidence = [
        item for item in semantic_evidence
        if is_semantically_relevant(item, query, cve)
    ]

    strong_matches = [
        item for item in relevant_evidence
        if item["similarity"] >= 0.75
    ]

    usable_matches = [
        item for item in relevant_evidence
        if item["similarity"] >= 0.60
    ]

    if len(strong_matches) >= 3:
        score += 2
        reasons.append(
            f"{len(strong_matches)} relevant strong semantic matches"
        )
    elif usable_matches:
        score += 1
        reasons.append(
            f"{len(usable_matches)} relevant semantic matches"
        )

    if semantic_evidence and not relevant_evidence:
        reasons.append(
            "Semantic results retrieved but none passed relevance filtering"
        )

    if score >= 3:
        status = "relevant"
    elif score >= 1:
        status = "weak"
    else:
        status = "irrelevant"

    average_similarity = (
        sum(item["similarity"] for item in usable_matches)
        / len(usable_matches)
        if usable_matches else 0
    )

    return {
        "score": score,
        "status": status,
        "reason": reasons,
        "semantic_match_count": len(usable_matches),
        "semantic_candidate_count": len(semantic_evidence),
        "average_similarity": round(average_similarity, 4)
    }
