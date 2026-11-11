import time
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "http://localhost:11434/api/embed"
MODEL = "nomic-embed-text"

sample = [
    "CISA KEV: Known exploited vulnerability. Apple iOS, macOS, and iPadOS contain an out-of-bounds write vulnerability that may lead to arbitrary code execution.",
    "NVD: The device encrypts data using AES-CBC with static zero-filled initialization vectors, making it susceptible to replay attacks.",
    "CSTI: STIX indicator pattern identifies a malicious domain associated with threat intelligence.",
]

for batch_size in [32, 64, 128, 256]:
    texts = [sample[i % len(sample)] for i in range(batch_size)]

    try:
        start = time.perf_counter()

        response = requests.post(
            URL,
            json={"model": MODEL, "input": texts},
            timeout=300
        )
        response.raise_for_status()

        embeddings = response.json()["embeddings"]
        elapsed = time.perf_counter() - start

        print(
            f"Batch: {batch_size:3} | "
            f"Time: {elapsed:7.2f}s | "
            f"Records/sec: {batch_size / elapsed:7.2f} | "
            f"Dimensions: {len(embeddings[0])}"
        )

    except Exception as error:
        print(f"Batch {batch_size} failed: {error}")
