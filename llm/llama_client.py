import requests


class LlamaClient:

    def __init__(
        self,
        model="llama3.2:3b",
        base_url="http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt):

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            ""
        )