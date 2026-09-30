def grade_retrieval(context):

    if not context:
        return {
            "score": 0,
            "status": "irrelevant",
            "reason": "No context retrieved."
        }

    score = 0
    reasons = []

    if context.get("cve"):
        score += 1
        reasons.append("CVE identified")

    if context.get("description"):
        score += 1
        reasons.append("Description available")

    if context.get("products"):
        valid_products = [
            p for p in context["products"]
            if p.get("product")
        ]

        if valid_products:
            score += 1
            reasons.append("Affected product found")

    if context.get("evidence"):
        valid_evidence = [
            e for e in context["evidence"]
            if e.get("source")
        ]

        if valid_evidence:
            score += 1
            reasons.append("Evidence source found")

    if score >= 3:
        status = "relevant"

    elif score >= 1:
        status = "weak"

    else:
        status = "irrelevant"

    return {
        "score": score,
        "status": status,
        "reason": reasons
    }