from django.urls import path
from . import views
from .views import (
    add_movie,
    select_tmdb_movie,
    choose_trailer,
    select_trailer,
    ai_rating,
    finalize_film,
)

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path("add-movie/", add_movie, name="add_movie"),
    path("add-movie/tmdb/<int:tmdb_id>/", select_tmdb_movie, name="select_tmdb_movie"),
    path("add-movie/trailer/<int:tmdb_id>/", choose_trailer, name="choose_trailer"),
    path("add-movie/trailer/select/<int:tmdb_id>/<str:video_id>/", select_trailer, name="select_trailer"),
    path("add-movie/ai-rating/<int:tmdb_id>/", ai_rating, name="ai_rating"),
    path("add-movie/finalize/<int:tmdb_id>/", finalize_film, name="finalize_film"),
]
