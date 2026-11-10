
import json
import zipfile
import hashlib
from pathlib import Path
from collections import Counter

from utils import save_json, clean_text


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data/raw/csti/CTI_Dataset_stix_bundles.zip"
OUTPUT_FILE = BASE_DIR / "data/processed/csti_entities.json"
ERROR_FILE = BASE_DIR / "data/processed/csti_processing_errors.json"



ENTITY_TYPE_MAP = {
    "intrusion-set": "ThreatActor",
    "attack-pattern": "Technique",
    "malware": "Malware",
    "tool": "Tool",
    "campaign": "Campaign",
    "vulnerability": "Vulnerability",
    "indicator": "Indicator",
    "identity": "Identity",

    # STIX cyber observables
    "file": "File",
    "domain-name": "Domain",
    "url": "URL",
    "hostname": "Hostname",
    "location": "Location",
    "email-addr": "EmailAddress",
    "ipv4-addr": "IPAddress",
    "cryptocurrency-wallet": "CryptoWallet"
}


RELATIONSHIP_MAP = {
    "uses": "USES",
    "targets": "TARGETS",
    "exploits": "EXPLOITS",
    "affects": "AFFECTS",
    "attributed-to": "ASSOCIATED_WITH",
    "related-to": "ASSOCIATED_WITH",
}


def make_evidence_id(bundle_name, stix_id):
    value = f"{bundle_name}|{stix_id}"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"evidence--{digest}"


def extract_claim(obj):
    description = clean_text(obj.get("description", ""))

    if description:
        return description

    pattern = clean_text(obj.get("pattern", ""))

    if pattern:
        return f"STIX indicator pattern: {pattern}"

    name = clean_text(obj.get("name", ""))

    if name:
        return f"STIX {obj.get('type', 'object')}: {name}"

    return ""


def process_csti():

    entities = {}
    relationships = []
    evidence = []

    errors = []
    object_counts = Counter()

    valid_bundles = 0
    invalid_bundles = 0

    seen_relationships = set()
    seen_evidence = set()

    with zipfile.ZipFile(INPUT_FILE, "r") as archive:

        for filename in archive.namelist():

            if not filename.endswith(".json"):
                continue

            try:
                bundle = json.loads(archive.read(filename))

                if bundle.get("type") != "bundle":
                    raise ValueError("Invalid STIX bundle")

                valid_bundles += 1

                for obj in bundle.get("objects", []):

                    stix_type = obj.get("type", "unknown")
                    stix_id = obj.get("id")

                    object_counts[stix_type] += 1

                    if not stix_id:
                        continue

                    # Extract supported entities.
                    if stix_type in ENTITY_TYPE_MAP:

                        
                        entity_name = (
                            obj.get("name")
                            or obj.get("value")
                            or obj.get("hashes", {}).get("SHA-256")
                            or stix_id
                        )

                        entity = {
                            "id": stix_id,
                            "type": ENTITY_TYPE_MAP[stix_type],
                            "stix_type": stix_type,
                            "name": clean_text(entity_name),
                            "description": clean_text(
                                obj.get("description", "")
                            ),
                            "created": obj.get("created", ""),
                            "modified": obj.get("modified", "")
                        }


                        if stix_id not in entities:
                            entities[stix_id] = entity

                    # Preserve every STIX relationship.
                    elif stix_type == "relationship":

                        relationship_type = obj.get(
                            "relationship_type", ""
                        )

                        relationship_key = (
                            stix_id,
                            obj.get("source_ref"),
                            obj.get("target_ref"),
                            relationship_type
                        )

                        if relationship_key not in seen_relationships:

                            relationships.append({
                                "id": stix_id,
                                "source_ref": obj.get("source_ref"),
                                "target_ref": obj.get("target_ref"),
                                "relationship": RELATIONSHIP_MAP.get(
                                    relationship_type,
                                    "ASSOCIATED_WITH"
                                ),
                                "stix_relationship": relationship_type,
                                "confidence": obj.get("confidence"),
                                "created": obj.get("created"),
                                "modified": obj.get("modified")
                            })

                            seen_relationships.add(relationship_key)

                    # Extract evidence from supported entities
                    # and indicators, even when they aren't
                    # represented in the final KG yet.
                    if stix_type in ENTITY_TYPE_MAP or stix_type == "indicator":

                        claim = extract_claim(obj)

                        if claim:

                            evidence_id = make_evidence_id(
                                filename,
                                stix_id
                            )

                            if evidence_id not in seen_evidence:

                                references = obj.get(
                                    "external_references", []
                                )

                                urls = [
                                    ref.get("url")
                                    for ref in references
                                    if ref.get("url")
                                ]

                                evidence.append({
                                    "id": evidence_id,
                                    "source": "CTI Dataset (STIX)",
                                    "source_type": "STIX 2.1",
                                    "entity_id": stix_id,
                                    "claim": claim,
                                    "timestamp": (
                                        obj.get("modified")
                                        or obj.get("created")
                                        or ""
                                    ),
                                    "confidence": (
                                        obj.get("confidence", 0) / 100
                                        if obj.get("confidence") is not None
                                        else 0.0
                                    ),
                                    "reference": (
                                        urls[0]
                                        if urls
                                        else filename
                                    ),
                                    "bundle": filename,
                                    "stix_type": stix_type
                                })

                                seen_evidence.add(evidence_id)

            except (
                json.JSONDecodeError,
                UnicodeDecodeError,
                ValueError,
                KeyError
            ) as error:

                invalid_bundles += 1

                errors.append({
                    "file": filename,
                    "error": str(error)
                })

    result = {
        "source": "CTI Dataset (STIX 2.1)",
        "entities": list(entities.values()),
        "relationships": relationships,
        "evidence": evidence,
        "statistics": {
            "valid_bundles": valid_bundles,
            "invalid_bundles": invalid_bundles,
            "entities": len(entities),
            "relationships": len(relationships),
            "evidence": len(evidence),
            "object_types": dict(object_counts)
        }
    }

    save_json(result, OUTPUT_FILE)
    save_json(errors, ERROR_FILE)

    print("CTI processing completed.")
    print("Valid bundles:", valid_bundles)
    print("Invalid bundles:", invalid_bundles)
    print("Entities:", len(entities))
    print("Relationships:", len(relationships))
    print("Evidence records:", len(evidence))
    print("Saved to:", OUTPUT_FILE)
    print("Error report:", ERROR_FILE)


if __name__ == "__main__":
    process_csti()
