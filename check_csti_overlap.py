import json
from knowledge_graph.schema import NODE_LABELS

with open("data/processed/csti_entities.json", encoding="utf-8") as f:
    data = json.load(f)

dataset_types = {
    item["type"]
    for item in data["entities"]
}

unsupported = dataset_types - NODE_LABELS

print("Entity types in dataset:", sorted(dataset_types))
print("Unsupported entity types:", sorted(unsupported))

if not unsupported:
    print("\nPASS: All entity types are supported.")