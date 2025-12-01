from django.urls import path
from . import views

urlpatterns = [
    path("<str:task_id>/", views.get_trace, name="trace-get"),
]
