"""
URL configuration for cinerama project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from dashboard.views import test_tmdb

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
<<<<<<< HEAD
    path('', include('booking.urls')),
    path("test-tmdb/", test_tmdb, name="test_tmdb"),
=======
    path('', include('dashboard.urls')),  # This will make dashboard the homepage
    path('booking/', include('booking.urls')),  # Move booking to /booking/
>>>>>>> origin/main
]
