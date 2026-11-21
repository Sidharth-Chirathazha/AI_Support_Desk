import ollama
import httpx
from django.conf import settings


class AIServiceError(Exception):
    """Raised when communication with the AI service fails."""


class OllamaService:

    def __init__(self):
        self.client = ollama.Client(
            host=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT
        )

        self.model = settings.OLLAMA_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        response_format=None
    ) -> str:

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                format=response_format,
                options={
                    "temperature": temperature
                },
                stream=False
            )

            return response.message.content

        except ollama.ResponseError as exc:
            raise AIServiceError(
                f"Ollama response error: {exc.error}"
            ) from exc

        except ollama.RequestError as exc:
            raise AIServiceError(
                f"Ollama request error: {exc}"
            ) from exc

        except ConnectionError as exc:
            raise AIServiceError(
                "Cannot connect to Ollama. "
                "Check whether Ollama is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise AIServiceError(
                "Ollama request timed out."
            ) from exc


ollama_service = OllamaService()
