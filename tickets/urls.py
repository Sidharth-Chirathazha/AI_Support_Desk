from django.urls import path

from .views import (
    RejectAIReplyView,
    TicketListCreateView,
    TicketDetailView,
    TicketMessageListCreateView,
    GenerateAIReplyView,
    ApproveAIReplyView,
)


urlpatterns = [
    path(
        "",
        TicketListCreateView.as_view(),
        name="ticket-list-create"
    ),

    path(
        "<int:pk>/",
        TicketDetailView.as_view(),
        name="ticket-detail"
    ),

    path(
        "<int:ticket_id>/messages/",
        TicketMessageListCreateView.as_view(),
        name="ticket-messages"
    ),

    path(
        "<int:ticket_id>/generate-reply/",
        GenerateAIReplyView.as_view(),
        name="generate-ai-reply"
    ),

    path(
        "<int:ticket_id>/drafts/<int:draft_id>/approve/",
        ApproveAIReplyView.as_view(),
        name="approve-ai-reply"
    ),

    path(
        "<int:ticket_id>/drafts/<int:draft_id>/reject/",
        RejectAIReplyView.as_view(),
        name="reject-ai-reply"
    ),
]