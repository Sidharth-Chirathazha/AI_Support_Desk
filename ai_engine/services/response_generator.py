
from ai_engine.services.ollama_service import (
    ollama_service,
    AIServiceError
)

from ai_engine.prompts.response_generation import (
    SYSTEM_PROMPT,
    build_response_prompt
)


class AIReplyGenerationError(Exception):
    """Raised when AI reply generation fails."""


def generate_ticket_reply(ticket):

    # Retrieve the latest 10 messages.
    recent_messages = list(
        ticket.messages.order_by("-created_at")[:10]
    )

    # Reverse them to maintain chronological order.
    recent_messages.reverse()

    conversation = "\n".join([
        f"{message.sender_type}: {message.message}"
        for message in recent_messages
    ])

    response = ollama_service.generate(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_response_prompt(
            ticket,
            conversation
        ),
        temperature=0.4
    )

    response = response.strip()

    if not response:
        raise AIReplyGenerationError(
            "AI generated an empty response."
        )

    return response
