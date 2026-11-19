from rest_framework import serializers


class TicketAnalysisRequestSerializer(serializers.Serializer):

    message = serializers.CharField(
        min_length=10,
        max_length=5000,
        trim_whitespace=True
    )