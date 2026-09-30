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