
# Create your views here.

"""Dashboard views."""

import os
from datetime import datetime
import logging

"""Dashboard views."""

import os
from datetime import datetime
import logging

import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from booking.models import Film, Showtime, RATING_CHOICES
from dashboard.services.ai_rating import classify_rating_with_ai

logger = logging.getLogger(__name__)


# Views


def dashboard_view(request):
    """Render the main dashboard with carousels and upcoming showtimes."""
    new_releases = Film.objects.filter(is_new_release=True, is_active=True)[:6]
    classic_films = Film.objects.filter(is_classic=True, is_active=True)[:6]

    today = timezone.now().date()
    upcoming_showtimes = (
        Showtime.objects.filter(
            date__gte=today, is_available=True, film__is_active=True
        )
        .select_related("film", "screen")
        .order_by("date", "time")
    )

    films_with_showtimes = {}
    for showtime in upcoming_showtimes:
        films_with_showtimes.setdefault(showtime.film, []).append(
            {
                "id": showtime.id,
                "time": showtime.time.strftime("%H:%M"),
                "date": showtime.date,
                "price": showtime.price,
                "screen": showtime.screen,
                "available_seats": showtime.available_seats,
            }
        )

    context = {
        "new_releases": new_releases,
        "classic_films": classic_films,
        "films_with_showtimes": films_with_showtimes,
    }
    return render(request, "dashboard/dashboard.html", context)


def test_tmdb(request):
    """Small view to verify TMDb responses during development."""
    api_key = settings.TMDB_API_KEY
    movie_id = 27205  # Inception

    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={api_key}&language=en-US"
    )
    config_url = (
        "https://api.themoviedb.org/3/configuration"
        f"?api_key={api_key}"
    )

    movie = requests.get(url).json()
    config = requests.get(config_url).json()

    base = config["images"]["secure_base_url"]
    size = config["images"]["poster_sizes"][3]
    poster_url = f"{base}{size}{movie['poster_path']}"
    backdrop_path = movie.get("backdrop_path")
    if backdrop_path:
        backdrop_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
    else:
        backdrop_url = None

    return render(
        request,
        "dashboard/test_tmdb.html",
        {"movie": movie, "poster": poster_url, "backdrop": backdrop_url},
    )


@login_required
def add_movie(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Admins only")

    query = request.GET.get("q")
    results = []
    if query:
        url = (
            f"https://api.themoviedb.org/3/search/movie"
            f"?api_key={settings.TMDB_API_KEY}&query={query}"
        )
        results = requests.get(url).json().get("results", [])

    return render(request, "dashboard/add_movie.html", {"results": results})


@login_required
def select_tmdb_movie(request, tmdb_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Admins only")

    api_key = settings.TMDB_API_KEY

    details = (
        requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            f"?api_key={api_key}&language=en-US"
        )
        .json()
    )

    credits = (
        requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
            f"?api_key={api_key}"
        )
        .json()
    )

    director = ""
    for c in credits.get("crew", []):
        if c.get("job") == "Director":
            director = c.get("name")
            break

    cast = ", ".join([c.get("name") for c in credits.get("cast", [])[:5]])

    release_date_str = details.get("release_date")
    release_date_val = None
    is_classic = False
    is_new_release = False
    if release_date_str:
        try:
            parsed = datetime.strptime(release_date_str, "%Y-%m-%d")
            release_date_val = parsed.date()
            if release_date_val.year < 2025:
                is_classic = True
            else:
                is_new_release = True
        except ValueError:
            logger.debug("Could not parse release_date: %s", release_date_str)
            is_new_release = True
    else:
        is_new_release = True

    poster_path = details.get("poster_path")
    backdrop_path = details.get("backdrop_path")

    film, _ = Film.objects.update_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "title": details.get("title"),
            "synopsis": details.get("overview"),
            "duration": details.get("runtime"),
            "year": release_date_val,
            "director": director,
            "cast": cast,
            "poster_url": (
                f"https://image.tmdb.org/t/p/w342{poster_path}"
                if poster_path
                else None
            ),
            "backdrop_url": (
                f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
                if backdrop_path
                else None
            ),
            "is_classic": is_classic,
            "is_new_release": is_new_release,
        },
    )

    return render(request, "dashboard/confirm_tmdb.html", {"film": film})


@login_required
def choose_trailer(request, tmdb_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Admins only")

    film = Film.objects.get(tmdb_id=tmdb_id)
    query = f"{film.title} official trailer"
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults=5&q={query}"
        f"&key={os.environ.get('YOUTUBE_API_KEY')}"
    )

    response = requests.get(url).json()
    items = response.get("items", [])
    logger.debug("YouTube items: %s", items)

    if request.method == "POST":
        video_id = request.POST.get("video_id")
        if video_id:
            film.trailer_url = f"https://www.youtube.com/watch?v={video_id}"
            film.save()
            return redirect("ai_rating", tmdb_id=tmdb_id)

    return render(
        request,
        "dashboard/choose_trailer.html",
        {"film": film, "trailers": items},
    )


@login_required
def select_trailer(request, tmdb_id, video_id):
    film = Film.objects.get(tmdb_id=tmdb_id)
    film.trailer_url = f"https://www.youtube.com/embed/{video_id}"
    film.save()
    return redirect("ai_rating", tmdb_id=tmdb_id)


@login_required
def ai_rating(request, tmdb_id):
    film = Film.objects.get(tmdb_id=tmdb_id)
    ai_rating = classify_rating_with_ai(
        title=film.title,
        synopsis=film.synopsis,
        genres=film.genre,
        cast=film.cast,
    )
    logger.debug("AI returned: %s", ai_rating)
    if ai_rating:
        ai_rating = ai_rating.strip().upper()
    return render(
        request,
        "dashboard/ai_rating.html",
        {"film": film, "ai_rating": ai_rating, "choices": RATING_CHOICES},
    )


@login_required
def finalize_film(request, tmdb_id):
    film = Film.objects.get(tmdb_id=tmdb_id)
    if request.method == "POST":
        rating = request.POST.get("rating")
        if not rating:
            return redirect("ai_rating", tmdb_id=tmdb_id)
        film.rating = rating
        film.is_active = True
        film.save()
        return redirect("finalize_film", tmdb_id=tmdb_id)

    return render(request, "dashboard/finalize_film.html", {"film": film})

