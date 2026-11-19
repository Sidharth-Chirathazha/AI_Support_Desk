from typing import Literal
from pydantic import BaseModel, Field


class TicketAnalysis(BaseModel):

    category: Literal[
        "Billing",
        "Technical",
        "Account",
        "General"
    ]

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    sentiment: Literal[
        "Positive",
        "Neutral",
        "Negative"
    ]

    summary: str = Field(
        min_length=10,
        max_length=300
    )

    department: Literal[
        "Billing Support",
        "Technical Support",
        "Account Support",
        "General Support"
    ]