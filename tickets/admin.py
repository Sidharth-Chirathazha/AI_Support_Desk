from django.contrib import admin
from .models import Ticket, TicketMessage, AIReplyDraft


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "category",
        "priority",
        "status",
        "ai_analysis_status",
        "created_by",
        "created_at",
    )

    list_filter = (
        "category",
        "priority",
        "status",
        "sentiment",
        "ai_analysis_status",
    )

    search_fields = (
        "title",
        "description",
        "ai_summary",
    )


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "ticket",
        "sender",
        "is_ai_generated",
        "created_at",
    )

    list_filter = ("is_ai_generated",)

admin.site.register(AIReplyDraft)