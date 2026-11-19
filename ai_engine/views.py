import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ai_engine.serializers import (
    TicketAnalysisRequestSerializer
)

from ai_engine.services.ticket_analyzer import (
    analyze_ticket,
    AIOutputError
)

from ai_engine.services.ollama_service import (
    AIServiceError
)


logger = logging.getLogger(__name__)


class AnalyzeTicketView(APIView):

    def post(self, request):

        serializer = TicketAnalysisRequestSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]

        try:

            analysis = analyze_ticket(message)

            return Response(
                analysis.model_dump(),
                status=status.HTTP_200_OK
            )

        except AIServiceError:

            logger.exception("Ollama service failure")

            return Response(
                {
                    "error": "AI service is currently unavailable."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except AIOutputError:

            logger.exception("Invalid AI output")

            return Response(
                {
                    "error": "AI could not generate a valid analysis."
                },
                status=status.HTTP_502_BAD_GATEWAY
            )