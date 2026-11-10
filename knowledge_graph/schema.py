
NODE_LABELS = {
    # Existing CIF entity types
    "ThreatActor",
    "Technique",
    "Tactic",
    "Malware",
    "Tool",
    "Campaign",
    "Vulnerability",
    "Product",
    "CWE",
    "NetworkEvent",

    # CTI / STIX entity types
    "Indicator",
    "Identity",
    "File",
    "Domain",
    "URL",
    "Hostname",
    "Location",
    "EmailAddress",
    "IPAddress",
    "CryptoWallet",

    # Evidence nodes
    "Evidence",
}


RELATIONSHIPS = {
    # Existing CIF relationships
    "USES",
    "TARGETS",
    "EXPLOITS",
    "AFFECTS",
    "HAS_CWE",
    "HAS_CVSS",
    "BELONGS_TO",
    "ASSOCIATED_WITH",
    "SUPPORTED_BY",
    "MITIGATES",
    "DETECTS",
    "SUBTECHNIQUE_OF",

    # CTI / STIX relationships
    "INDICATES",
    "BASED_ON",
}


DATA_SOURCES = {
    "MITRE": "MITRE ATT&CK",
    "NVD": "National Vulnerability Database",
    "KEV": "CISA Known Exploited Vulnerabilities",
    "CTI": "CTI Dataset (STIX 2.1)",
}
