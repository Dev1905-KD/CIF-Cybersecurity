import json
from pathlib import Path

from knowledge_graph.graph_builder import GraphBuilder


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR /
    "data/processed/kev_vulnerabilities.json"
)


def load_kev_data():

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

            vendor = vulnerability.get(
                "vendor",
                ""
            )

            product = vulnerability.get(
                "product",
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
                    "description": vulnerability.get(
                        "description",
                        ""
                    ),
                    "source": "CISA KEV"
                }
            )

            # -------------------------
            # Create Evidence node
            # -------------------------

            evidence_id = f"KEV-{cve_id}"

            evidence_properties = {
                "id": evidence_id,
                "source": "CISA KEV",
                "claim": "Known exploited vulnerability",
                "date_added": vulnerability.get(
                    "date_added",
                    ""
                ),
                "required_action": vulnerability.get(
                    "required_action",
                    ""
                ),
                "known_ransomware_use": vulnerability.get(
                    "known_ransomware_use",
                    ""
                ),
                "evidence_type": "exploitation"
            }

            builder.create_node(
                "Evidence",
                evidence_properties
            )

            # -------------------------
            # Vulnerability
            # → Evidence
            # -------------------------

            builder.create_relationship(
                cve_id,
                "Vulnerability",
                "SUPPORTED_BY",
                evidence_id,
                "Evidence"
            )

            # -------------------------
            # Create Product node
            # -------------------------

            if vendor or product:

                product_id = f"{vendor}:{product}"

                builder.create_node(
                    "Product",
                    {
                        "id": product_id,
                        "vendor": vendor,
                        "name": product
                    }
                )

                # -------------------------
                # Vulnerability
                # → Product
                # -------------------------

                builder.create_relationship(
                    cve_id,
                    "Vulnerability",
                    "AFFECTS",
                    product_id,
                    "Product",
                    source="CISA KEV"
                )

        print(
            "CISA KEV loading completed successfully."
        )

        print(
            f"Processed vulnerabilities: "
            f"{len(vulnerabilities)}"
        )

    finally:
        builder.close()


if __name__ == "__main__":
    load_kev_data()