from llm.llama_client import LlamaClient
from llm.prompts import build_prompt


class EvidenceGenerator:

    def __init__(self):

        self.llama = LlamaClient()

    def generate(
        self,
        query,
        context
    ):

        prompt = build_prompt(
            query,
            context
        )

        response = self.llama.generate(
            prompt
        )

        return response