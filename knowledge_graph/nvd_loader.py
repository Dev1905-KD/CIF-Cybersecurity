import json
from pathlib import Path

from knowledge_graph.graph_builder import GraphBuilder


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR /
    "data/processed/nvd_vulnerabilities.json"
)


def load_nvd_data():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    builder = GraphBuilder()

    try:

        vulnerabilities = data.get(
            "vulnerabilities",
            []
        )

        for vulnerability in vulnerabilities:

            # -------------------------
            # Basic vulnerability data
            # -------------------------

            cve_id = vulnerability.get("id")

            if not cve_id:
                continue

            description = vulnerability.get(
                "description",
                ""
            )

            # -------------------------
            # Create / update
            # Vulnerability node
            # -------------------------

            builder.create_node(
                "Vulnerability",
                {
                    "id": cve_id,
                    "description": description,
                    "source": "NVD"
                }
            )

            # -------------------------
            # Create NVD Evidence node
            # -------------------------

            evidence_id = f"NVD-{cve_id}"

            evidence_properties = {
                "id": evidence_id,
                "source": "NVD",
                "claim": description,
                "evidence_type": "vulnerability_record"
            }

            builder.create_node(
                "Evidence",
                evidence_properties
            )

            # -------------------------
            # Vulnerability
            # → NVD Evidence
            # -------------------------

            builder.create_relationship(
                cve_id,
                "Vulnerability",
                "SUPPORTED_BY",
                evidence_id,
                "Evidence"
            )

        print(
            "NVD Knowledge Graph loading completed successfully."
        )

        print(
            f"Processed vulnerabilities: "
            f"{len(vulnerabilities)}"
        )

    finally:
        builder.close()


if __name__ == "__main__":
    load_nvd_data()