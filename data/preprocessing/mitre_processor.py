from pathlib import Path

from utils import load_json, save_json, clean_text


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data/raw/mittre/enterprise-attack-19.2.json"
OUTPUT_FILE = BASE_DIR / "data/processed/mitre_entities.json"


def process_mitre():
    data = load_json(INPUT_FILE)

    entities = []
    relationships = []

    for obj in data.get("objects", []):

        obj_type = obj.get("type")

        # Ignore STIX objects that are not useful for our first KG version
        if obj_type in {
            "attack-pattern",
            "intrusion-set",
            "malware",
            "tool",
            "campaign"
        }:

            entity = {
                "id": obj.get("id"),
                "type": obj_type,
                "name": obj.get("name", ""),
                "description": clean_text(
                    obj.get("description", "")
                )
            }

            entities.append(entity)

        elif obj_type == "relationship":

            relationship = {
                "id": obj.get("id"),
                "source_ref": obj.get("source_ref"),
                "target_ref": obj.get("target_ref"),
                "relationship": obj.get("relationship_type")
            }

            relationships.append(relationship)

    result = {
        "source": "MITRE ATT&CK",
        "entities": entities,
        "relationships": relationships
    }

    save_json(result, OUTPUT_FILE)

    print("MITRE processing completed.")
    print("Entities:", len(entities))
    print("Relationships:", len(relationships))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    process_mitre()