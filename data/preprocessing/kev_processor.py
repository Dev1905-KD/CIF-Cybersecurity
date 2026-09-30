from pathlib import Path

from utils import load_json, save_json, clean_text


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR /
    "data/raw/kev/known_exploited_vulnerabilities.json"
)

OUTPUT_FILE = (
    BASE_DIR /
    "data/processed/kev_vulnerabilities.json"
)


def process_kev():

    data = load_json(INPUT_FILE)

    vulnerabilities = []

    for item in data.get("vulnerabilities", []):

        vulnerabilities.append({
            "id": item.get("cveID"),
            "type": "known_exploited_vulnerability",
            "vendor": clean_text(
                item.get("vendorProject", "")
            ),
            "product": clean_text(
                item.get("product", "")
            ),
            "vulnerability_name": clean_text(
                item.get("vulnerabilityName", "")
            ),
            "description": clean_text(
                item.get("shortDescription", "")
            ),
            "date_added": item.get("dateAdded"),
            "required_action": clean_text(
                item.get("requiredAction", "")
            ),
            "due_date": item.get("dueDate"),
            "known_ransomware_use": item.get(
                "knownRansomwareCampaignUse"
            ),
            "source": "CISA KEV"
        })

    result = {
        "source": "CISA KEV",
        "vulnerabilities": vulnerabilities
    }

    save_json(result, OUTPUT_FILE)

    print("KEV processing completed.")
    print("Vulnerabilities:", len(vulnerabilities))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    process_kev()