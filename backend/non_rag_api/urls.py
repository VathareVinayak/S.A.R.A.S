from django.urls import path
from . import views

urlpatterns = [
    path("run/", views.run_non_rag, name="non-rag-run"),
]
