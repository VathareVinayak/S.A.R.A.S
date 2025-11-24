"""
URL configuration for saras_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    
    path("admin/", admin.site.urls),

    # Core routes (health, run-task)
    path("api/core/", include("core.urls")),
    path("api/rag/", include("rag_api.urls")),
    path("api/non-rag/", include("non_rag_api.urls")),
    path("api/trace/", include("trace_api.urls")),
    path("api/memory/", include("memory_api.urls")),
    path("api/tools/", include("tools_api.urls")),
]
