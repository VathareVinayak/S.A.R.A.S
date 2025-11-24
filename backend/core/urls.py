from django.urls import path
from . import views

urlpatterns = [
    # Basic health check for deployment/CI to ping
    path("health/", views.health_check, name="core-health"),
    
    # Main entrypoint (router) which decides RAG vs Non-RAG
    path("run-task/", views.run_task, name="core-run-task"),
]
