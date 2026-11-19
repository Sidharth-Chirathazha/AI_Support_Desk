from django.urls import path
from .views import AnalyzeTicketView


urlpatterns = [
    path(
        "analyze-ticket/",
        AnalyzeTicketView.as_view(),
        name="analyze-ticket"
    ),
]