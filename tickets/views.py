
import logging

from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Ticket, TicketMessage, AIReplyDraft
from .serializers import (
    TicketCreateSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    TicketStatusUpdateSerializer,
    TicketMessageCreateSerializer,
    TicketMessageSerializer,
    AIReplyDraftSerializer,
)

from ai_engine.services.ticket_analyzer import (
    analyze_ticket,
    AIOutputError,
)

from ai_engine.services.response_generator import (
    generate_ticket_reply,
    AIReplyGenerationError,
)

from ai_engine.services.ollama_service import AIServiceError
from django.shortcuts import get_object_or_404
from django.utils import timezone



logger = logging.getLogger(__name__)


class TicketListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TicketCreateSerializer

        return TicketListSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 1: Save the ticket first.
        with transaction.atomic():
            ticket = serializer.save(
                created_by=request.user
            )

            # Step 2: Store the original customer message.
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                sender_type=TicketMessage.SenderType.CUSTOMER,
                message=ticket.description,
                is_ai_generated=False,
            )

        # Step 3: Perform AI analysis.
        try:

            analysis = analyze_ticket(ticket.description)

            # Step 4: Update ticket with AI results.
            ticket.category = analysis.category
            ticket.priority = analysis.priority
            ticket.sentiment = analysis.sentiment
            ticket.ai_summary = analysis.summary
            ticket.recommended_department = analysis.department
            ticket.ai_analysis_status = (
                Ticket.AIAnalysisStatus.COMPLETED
            )

            ticket.save(
                update_fields=[
                    "category",
                    "priority",
                    "sentiment",
                    "ai_summary",
                    "recommended_department",
                    "ai_analysis_status",
                    "updated_at",
                ]
            )

        except (AIServiceError, AIOutputError):

            logger.exception(
                "AI analysis failed for ticket %s",
                ticket.id
            )

            ticket.ai_analysis_status = (
                Ticket.AIAnalysisStatus.FAILED
            )

            ticket.save(
                update_fields=[
                    "ai_analysis_status",
                    "updated_at",
                ]
            )

        # Step 5: Return the complete ticket.
        response_serializer = TicketDetailSerializer(ticket)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class TicketDetailView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return TicketStatusUpdateSerializer

        return TicketDetailSerializer



class TicketMessageListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_ticket(self):
        return get_object_or_404(
            Ticket,
            id=self.kwargs["ticket_id"],
            created_by=self.request.user
        )

    def get_queryset(self):
        ticket = self.get_ticket()

        return ticket.messages.select_related(
            "sender"
        ).all()

    def get_serializer_class(self):

        if self.request.method == "POST":
            return TicketMessageCreateSerializer

        return TicketMessageSerializer

    def perform_create(self, serializer):

        ticket = self.get_ticket()

        if ticket.status in [
            Ticket.Status.RESOLVED,
            Ticket.Status.CLOSED
        ]:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "Cannot add messages to a resolved or closed ticket."
            )

        serializer.save(
            ticket=ticket,
            sender=self.request.user,
            sender_type=TicketMessage.SenderType.CUSTOMER,
            is_ai_generated=False
        )


class GenerateAIReplyView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):

        ticket = get_object_or_404(
            Ticket,
            id=ticket_id,
            created_by=request.user
        )

        if ticket.status in [
            Ticket.Status.RESOLVED,
            Ticket.Status.CLOSED
        ]:
            return Response(
                {"error": "Cannot generate replies for a closed ticket."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            reply = generate_ticket_reply(ticket)

            draft = AIReplyDraft.objects.create(
                ticket=ticket,
                content=reply,
                generated_by=request.user
            )

            return Response(
                AIReplyDraftSerializer(draft).data,
                status=status.HTTP_201_CREATED
            )

        except (AIServiceError, AIReplyGenerationError):

            logger.exception(
                "AI reply generation failed for ticket %s",
                ticket.id
            )

            return Response(
                {
                    "error": "Unable to generate an AI reply currently."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class ApproveAIReplyView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id, draft_id):

        with transaction.atomic():

            ticket = get_object_or_404(
                Ticket.objects.select_for_update(),
                id=ticket_id,
                created_by=request.user
            )

            draft = get_object_or_404(
                AIReplyDraft.objects.select_for_update(),
                id=draft_id,
                ticket=ticket
            )

            if draft.status != AIReplyDraft.Status.PENDING:

                return Response(
                    {
                        "error": "This draft has already been reviewed."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if ticket.status in [
                Ticket.Status.RESOLVED,
                Ticket.Status.CLOSED
            ]:
                return Response(
                    {"error": "Cannot approve a reply for a closed ticket."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create an actual conversation message.
            message = TicketMessage.objects.create(
                ticket=ticket,
                sender=None,
                sender_type=TicketMessage.SenderType.AI,
                message=draft.content,
                is_ai_generated=True
            )

            # Update draft status.
            draft.status = AIReplyDraft.Status.APPROVED
            draft.reviewed_by = request.user
            draft.reviewed_at = timezone.now()

            draft.save(
                update_fields=[
                    "status",
                    "approved_by",
                    "reviewed_at"
                ]
            )

        return Response(
            TicketMessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )



class RejectAIReplyView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id, draft_id):

        draft = get_object_or_404(
            AIReplyDraft,
            id=draft_id,
            ticket__id=ticket_id,
            ticket__created_by=request.user
        )

        if draft.status != AIReplyDraft.Status.PENDING:

            return Response(
                {"error": "This draft has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        draft.status = AIReplyDraft.Status.REJECTED
        draft.reviewed_by = request.user
        draft.reviewed_at = timezone.now()

        draft.save(
            update_fields=[
                "status",
                "approved_by",
                "reviewed_at"
            ]
        )

        return Response(
            {"message": "AI reply draft rejected successfully."},
            status=status.HTTP_200_OK
        )