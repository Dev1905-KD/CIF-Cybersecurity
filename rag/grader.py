def grade_retrieval(context):

    if not context:
        return {
            "score": 0,
            "status": "irrelevant",
            "reason": ["No context retrieved."]
        }

    score = 0
    reasons = []

    if context.get("cve"):
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

    strong_matches = [
        item for item in semantic_evidence
        if item["similarity"] >= 0.75
    ]
    usable_matches = [
        item for item in semantic_evidence
        if item["similarity"] >= 0.60
    ]

    if len(strong_matches) >= 3:
        score += 3
        reasons.append(
            f"{len(strong_matches)} strong semantic evidence matches"
        )
    elif usable_matches:
        score += 1
        reasons.append(
            f"{len(usable_matches)} usable semantic evidence matches"
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
        "average_similarity": round(average_similarity, 4)
    }
