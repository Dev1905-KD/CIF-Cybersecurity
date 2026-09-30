from pathlib import Path

from utils import load_json, save_json, clean_text


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data/raw/nvd/nvdcve-2.0-2026.json"
OUTPUT_FILE = BASE_DIR / "data/processed/nvd_vulnerabilities.json"


def process_nvd():
    data = load_json(INPUT_FILE)

    vulnerabilities = []

    for item in data.get("vulnerabilities", []):

        cve = item.get("cve", {})

        cve_id = cve.get("id")

        descriptions = cve.get("descriptions", [])

        description = ""

        if descriptions:
            description = descriptions[0].get("value", "")

        vulnerabilities.append({
            "id": cve_id,
            "type": "vulnerability",
            "description": clean_text(description),
            "source": "NVD"
        })

    result = {
        "source": "NVD",
        "vulnerabilities": vulnerabilities
    }

    save_json(result, OUTPUT_FILE)

    print("NVD processing completed.")
    print("Vulnerabilities:", len(vulnerabilities))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    process_nvd()