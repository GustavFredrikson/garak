import logging
import json
import requests
import os
from urllib.parse import urlparse

from garak import _config
from garak.generators.base import Generator

class LangChainServeLLMGenerator(Generator):
    """Class supporting LangChain Serve LLM interfaces via HTTP POST requests.

    This class facilitates communication with LangChain Serve's LLMs through a web API, making it possible
    to utilize external LLMs not directly integrated into the LangChain library. It requires setting up
    an API endpoint using LangChain Serve.

    Utilizes the HTTP POST method to send prompts to the specified LLM and retrieves the generated text
    response. It is necessary to ensure that the API endpoint is correctly set up and accessible.

    Inherits from Garak's base Generator class, extending its capabilities to support web-based LLM services.
    The API endpoint is set through the 'LANGCHAIN_SERVE_URI' environment variable, which should be the base URI 
    of the LangChain Serve deployment. The 'invoke' endpoint is then appended to this URI to form the full API endpoint URL.

    Example of setting up the environment variable:
        export LANGCHAIN_SERVE_URI=http://127.0.0.1:8000/rag-chroma-private
    """

    generator_family_name = "LangChainServe"
    config_hash = "default"

    def __init__(self, name, generations=10):
        self.name = name
        self.fullname = f"LangChain Serve LLM {self.name}"
        self.generations = generations
        api_uri = os.getenv("LANGCHAIN_SERVE_URI")
        if not self._validate_uri(api_uri):
            raise ValueError("Invalid API endpoint URI")
        
        self.api_endpoint = f"{api_uri}/invoke"

        super().__init__(name, generations=generations)

    @staticmethod
    def _validate_uri(uri):
        """Validates the given URI for correctness."""
        try:
            result = urlparse(uri)
            return all([result.scheme, result.netloc])
        except Exception as e:
            logging.error(f"URL parsing error: {e}")
            return False
        
    def _call_model(self, prompt: str) -> str:
        """Makes an HTTP POST request to the LangChain Serve API endpoint to invoke the LLM with a given prompt."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        payload = {"input": prompt, "config": {}, "kwargs": {}}

        try:
            response = requests.post(f"{self.api_endpoint}?config_hash={self.config_hash}", headers=headers, data=json.dumps(payload))
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if 400 <= response.status_code < 500:
                logging.error(f"Client error for prompt {prompt}: {e}")
                return None
            elif 500 <= response.status_code < 600:
                logging.error(f"Server error for prompt {prompt}: {e}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

        try:
            response_data = response.json()
            if "output" not in response_data or response_data["output"] is None:
                logging.error(f"No output found in response: {response_data}")
                return "No output generated"
            return response_data.get("output")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from response: {response.text}, error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error processing response: {e}")
            return None

default_class = "LangChainServeLLMGenerator"