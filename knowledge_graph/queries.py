GET_THREAT_ACTORS = """
MATCH (a:ThreatActor)
RETURN a.id, a.name
LIMIT 20
"""


GET_ACTOR_TECHNIQUES = """
MATCH (a:ThreatActor)-[:USES]->(t:Technique)
RETURN a.name, t.name
LIMIT 50
"""


GET_MALWARE_TECHNIQUES = """
MATCH (m:Malware)-[:USES]->(t:Technique)
RETURN m.name, t.name
LIMIT 50
"""


GET_GRAPH_STATS = """
MATCH (n)
RETURN labels(n) AS label, count(n) AS count
ORDER BY count DESC
"""

GET_EVIDENCE_FOR_CVE = """
MATCH (v:Vulnerability {id: $cve})
OPTIONAL MATCH (v)-[:SUPPORTED_BY]->(e:Evidence)
OPTIONAL MATCH (v)-[:AFFECTS]->(p:Product)

RETURN
    v.id AS cve,
    v.description AS description,
    collect(DISTINCT {
        source: e.source,
        type: e.evidence_type,
        claim: e.claim,
        date_added: e.date_added
    }) AS evidence,
    collect(DISTINCT {
        vendor: p.vendor,
        product: p.name
    }) AS products
"""