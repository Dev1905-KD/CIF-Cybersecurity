from pathlib import Path

from utils import load_json, save_json


BASE_DIR = Path(__file__).resolve().parents[2]


MITRE_FILE = BASE_DIR / "data/processed/mitre_entities.json"
NVD_FILE = BASE_DIR / "data/processed/nvd_vulnerabilities.json"
KEV_FILE = BASE_DIR / "data/processed/kev_vulnerabilities.json"

OUTPUT_FILE = BASE_DIR / "data/processed/cybersecurity_data.json"


def integrate_data():

    mitre = load_json(MITRE_FILE)
    nvd = load_json(NVD_FILE)
    kev = load_json(KEV_FILE)

    integrated_data = {
        "sources": [
            "MITRE ATT&CK",
            "NVD",
            "CISA KEV"
        ],
        "mitre": mitre,
        "nvd": nvd,
        "kev": kev
    }

    save_json(integrated_data, OUTPUT_FILE)

    print("Data integration completed.")
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    integrate_data()