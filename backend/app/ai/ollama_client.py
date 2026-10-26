import logging
import os
from collections.abc import Iterator
from typing import Any

from ollama import Client

logger = logging.getLogger(__name__)

# Default is only a fallback — the UI can override per request.
DEFAULT_MODEL = "qwen2.5:14b"


class OllamaClient:
    """Client used by Zebio to communicate with the local Ollama server."""

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
    ):
        self.host = host or "http://localhost:11434"
        self.model = model or os.getenv("ZEBIO_LLM_MODEL", DEFAULT_MODEL)
        self.client = Client(host=self.host)

    def list_models(self) -> list[dict[str, Any]]:
        """Return locally installed Ollama models with display metadata."""
        try:
            response = self.client.list()
            
            # Handle both dict and object
            raw_models = []
            if isinstance(response, dict):
                raw_models = response.get("models", [])
            elif hasattr(response, "models"):
                raw_models = response.models
            elif isinstance(response, list):
                raw_models = response

            models: list[dict[str, Any]] = []
            for raw in raw_models:
                # Handle both dict and object in the list
                if isinstance(raw, dict):
                    name = raw.get("model") or raw.get("name")
                    details = raw.get("details", {})
                    size_bytes = raw.get("size")
                else:
                    name = getattr(raw, "model", None) or getattr(raw, "name", None)
                    details = getattr(raw, "details", None)
                    size_bytes = getattr(raw, "size", None)

                if not name:
                    continue

                # Extract details safely
                if isinstance(details, dict):
                    parameter_size = details.get("parameter_size")
                    family = details.get("family")
                    quantization = details.get("quantization_level")
                else:
                    parameter_size = getattr(details, "parameter_size", None) if details else None
                    family = getattr(details, "family", None) if details else None
                    quantization = getattr(details, "quantization_level", None) if details else None

                models.append({
                    "name": name,
                    "parameter_size": parameter_size,
                    "family": family,
                    "quantization": quantization,
                    "size_bytes": size_bytes,
                })

            models.sort(key=lambda m: m["name"])
            return models
            
        except Exception as exc:
            logger.error(f"Ollama Error listing models: {exc}")
            return []

    def chat(
        self,
        messages: list[dict],
        *,
        format: str | dict | None = None,
        options: dict | None = None,
        model: str | None = None,
    ) -> str:
        """Send a conversation to the configured local model.

        Args:
            messages: Conversation messages.
            format: Optional Ollama response format, such as ``"json"``
                or a JSON schema.
            options: Optional Ollama options (e.g. ``{"temperature": 0}``).
            model: Optional model name; overrides ``self.model`` for this call.
        """
        kwargs: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
        }
        if format is not None:
            kwargs["format"] = format
        if options:
            kwargs["options"] = options

        response = self.client.chat(**kwargs)
        return response.message.content or ""

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Generate an embedding vector for a piece of text."""
        try:
            response = self.client.embeddings(model=model, prompt=text)
            
            # Handle both dict and Pydantic object responses safely
            if isinstance(response, dict):
                return response.get("embedding", [])
            elif hasattr(response, "embedding"):
                return response.embedding
                
            return []
        except Exception as exc:
            logger.error(f"Embedding failed: {exc}")
            return []

    def chat_stream(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
    ) -> Iterator[str]:
        response_stream = self.client.chat(
            model=model or self.model,
            messages=messages,
            stream=True,
        )
        for chunk in response_stream:
            content = getattr(
                getattr(chunk, "message", None), "content", None
            )
            if content:
                yield content

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        *,
        model: str | None = None,
    ):
        return self.client.chat(
            model=model or self.model,
            messages=messages,
            tools=tools,
        )