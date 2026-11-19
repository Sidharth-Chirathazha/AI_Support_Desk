from pydantic import ValidationError

from ai_engine.schemas import TicketAnalysis
from ai_engine.services.ollama_service import (
    ollama_service,
    AIServiceError
)
from ai_engine.prompts.ticket_analysis import (
    SYSTEM_PROMPT,
    build_ticket_prompt
)


class AIOutputError(Exception):
    """Raised when the model returns invalid structured output."""


def analyze_ticket(message: str) -> TicketAnalysis:

    raw_response = ollama_service.generate(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_ticket_prompt(message),
        temperature=0.1,
        response_format=TicketAnalysis.model_json_schema()
    )

    try:
        analysis = TicketAnalysis.model_validate_json(
            raw_response
        )

        return analysis

    except ValidationError as exc:
        raise AIOutputError(
            "The AI returned an invalid ticket analysis."
        ) from exc