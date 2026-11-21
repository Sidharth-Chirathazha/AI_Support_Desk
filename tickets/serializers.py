
from rest_framework import serializers
from .models import Ticket, TicketMessage, AIReplyDraft


class TicketCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket

        fields = [
            "id",
            "title",
            "description",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Ticket title must contain at least 5 characters."
            )

        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide a more detailed description."
            )

        return value.strip()


class TicketListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket

        fields = [
            "id",
            "title",
            "category",
            "priority",
            "sentiment",
            "status",
            "ai_analysis_status",
            "recommended_department",
            "created_at",
        ]


class TicketMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketMessage

        fields = [
            "id",
            "sender",
            "sender_type",
            "message",
            "is_ai_generated",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "sender",
            "sender_type",
            "is_ai_generated",
            "created_at",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):

    messages = TicketMessageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Ticket

        fields = [
            "id",
            "title",
            "description",
            "category",
            "priority",
            "sentiment",
            "status",
            "ai_summary",
            "recommended_department",
            "ai_analysis_status",
            "created_by",
            "messages",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields



class TicketStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket

        fields = ["status"]


class TicketMessageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketMessage

        fields = ["message"]

    def validate_message(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        return value


class AIReplyDraftSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIReplyDraft

        fields = [
            "id",
            "ticket",
            "content",
            "status",
            "created_at",
            "reviewed_at",
        ]

        read_only_fields = fields
