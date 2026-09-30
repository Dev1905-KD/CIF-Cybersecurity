def build_context(result):

    if not result:
        return "No relevant evidence was retrieved."

    context = []

    if result.get("cve"):
        context.append(
            f"CVE: {result['cve']}"
        )

    if result.get("description"):
        context.append(
            f"Description: {result['description']}"
        )

    if result.get("products"):

        context.append(
            "\nAffected Products:"
        )

        for product in result["products"]:

            vendor = product.get(
                "vendor",
                ""
            )

            name = product.get(
                "product",
                ""
            )

            if vendor or name:

                context.append(
                    f"- {vendor} {name}"
                )

    if result.get("evidence"):

        context.append(
            "\nEvidence:"
        )

        for evidence in result["evidence"]:

            source = evidence.get(
                "source",
                ""
            )

            claim = evidence.get(
                "claim",
                ""
            )

            context.append(
                f"- Source: {source}; "
                f"Claim: {claim}"
            )

    if result.get("connections"):

        context.append(
            "\nConnected Graph Entities:"
        )

        for connection in result[
            "connections"
        ]:

            context.append(
                f"- "
                f"{connection.get('relationship')}: "
                f"{connection.get('name') or connection.get('id')}"
            )

    return "\n".join(context)