from llm.llama_client import LlamaClient


client = LlamaClient()

prompt = """
Explain what a CVE is in two sentences.
"""

response = client.generate(
    prompt
)

print("\nLlama Response:\n")
print(response)