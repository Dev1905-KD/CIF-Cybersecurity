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

        for vulnerability in data.get(
            "vulnerabilities",
            []
        ):

            cve_id = vulnerability.get("id")

            if not cve_id:
                continue

            properties = {
                "id": cve_id,
                "description": vulnerability.get(
                    "description",
                    ""
                ),
                "source": "NVD"
            }

            builder.create_node(
                "Vulnerability",
                properties
            )

        print("NVD Knowledge Graph loading completed.")

    finally:
        builder.close()


if __name__ == "__main__":
    load_nvd_data()