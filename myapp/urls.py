from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from .views import (
    InventoreyView,
    HandledErrorView,
    UnHandledErrorView,
    CaptureMessageView, ErrorMasterView,
)

def trigger_error(request):
    division_by_zero = 1 / 0
urlpatterns = [
    path('sentry-debug2/', trigger_error),
    path("checkout", InventoreyView.as_view()),
    path("handled", HandledErrorView.as_view()),
    path("unhandled", UnHandledErrorView.as_view()),
    path("message", CaptureMessageView.as_view()),
    path("sentry-debug", ErrorMasterView.as_view()),
]
