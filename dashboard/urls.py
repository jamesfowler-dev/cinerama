from django.urls import path
from . import views
from .views import add_movie, select_movie

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path("add-movie/", add_movie, name="add_movie"),
    path("add-movie/select/<int:tmdb_id>/", select_movie, name="select_movie"),
]
