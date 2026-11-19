
from django.conf import settings
from django.db import models


class Ticket(models.Model):

    class Category(models.TextChoices):
        BILLING = "Billing", "Billing"
        TECHNICAL = "Technical", "Technical"
        ACCOUNT = "Account", "Account"
        GENERAL = "General", "General"

    class Priority(models.TextChoices):
        LOW = "Low", "Low"
        MEDIUM = "Medium", "Medium"
        HIGH = "High", "High"
        CRITICAL = "Critical", "Critical"

    class Sentiment(models.TextChoices):
        POSITIVE = "Positive", "Positive"
        NEUTRAL = "Neutral", "Neutral"
        NEGATIVE = "Negative", "Negative"

    class Status(models.TextChoices):
        OPEN = "Open", "Open"
        IN_PROGRESS = "In Progress", "In Progress"
        RESOLVED = "Resolved", "Resolved"
        CLOSED = "Closed", "Closed"

    class Department(models.TextChoices):
        BILLING = "Billing Support", "Billing Support"
        TECHNICAL = "Technical Support", "Technical Support"
        ACCOUNT = "Account Support", "Account Support"
        GENERAL = "General Support", "General Support"

    class AIAnalysisStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    sentiment = models.CharField(
        max_length=20,
        choices=Sentiment.choices,
        default=Sentiment.NEUTRAL
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    ai_summary = models.TextField(blank=True)

    recommended_department = models.CharField(
        max_length=30,
        choices=Department.choices,
        default=Department.GENERAL
    )

    ai_analysis_status = models.CharField(
        max_length=20,
        choices=AIAnalysisStatus.choices,
        default=AIAnalysisStatus.PENDING
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title



class TicketMessage(models.Model):

    class SenderType(models.TextChoices):
        CUSTOMER = "Customer", "Customer"
        AGENT = "Agent", "Agent"
        AI = "AI", "AI"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_messages"
    )

    sender_type = models.CharField(
        max_length=20,
        choices=SenderType.choices
    )

    message = models.TextField()

    is_ai_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
        ]

    def __str__(self):
        return f"Message for Ticket #{self.ticket_id}"