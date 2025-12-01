from django.urls import path
from . import views

urlpatterns = [
    path("session/", views.get_session_memory, name="memory-session"),
    path("long-term/", views.get_long_term_memory, name="memory-long-term"),
]
