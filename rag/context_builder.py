def build_context(result):

    if not result:
        return "No relevant evidence was retrieved."

    context = []

    if result.get("cve"):
        context.append(f"CVE: {result['cve']}")

    if result.get("description"):
        context.append(f"Description: {result['description']}")

    if result.get("products"):
        context.append("\nAffected Products:")
        for product in result["products"]:
            vendor = product.get("vendor", "")
            name = product.get("product", "")
            if vendor or name:
                context.append(f"- {vendor} {name}".strip())

    if result.get("evidence"):
        context.append("\nGraph Evidence:")
        for evidence in result["evidence"]:
            context.append(
                f"- Source: {evidence.get('source', 'Unknown')}; "
                f"Claim: {evidence.get('claim', '')}"
            )

    if result.get("semantic_evidence"):
        context.append("\nSemantic Evidence (vector search):")
        for item in result["semantic_evidence"]:
            entities = item.get("entities") or []
            entity_names = [
                entity.get("name") or entity.get("id")
                for entity in entities
                if entity.get("name") or entity.get("id")
            ]
            context.append(
                f"- Similarity: {item.get('similarity', 0):.4f}; "
                f"Source: {item.get('source') or 'Unknown'}; "
                f"STIX type: {item.get('stix_type') or 'Unknown'}; "
                f"Source type: {item.get('source_type') or 'Unknown'}; "
                f"Confidence: {item.get('confidence')}; "
                f"Claim: {item.get('claim') or ''}; "
                f"Reference: {item.get('reference') or 'N/A'}; "
                f"Related entities: {', '.join(entity_names)}"
            )

    if result.get("connections"):
        context.append("\nConnected Graph Entities:")
        for connection in result["connections"]:
            context.append(
                f"- {connection.get('relationship')}: "
                f"{connection.get('name') or connection.get('id')}"
            )

    return "\n".join(context)
