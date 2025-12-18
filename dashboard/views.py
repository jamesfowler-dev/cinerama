
# Create your views here.

"""Dashboard views."""

import os
from datetime import datetime, timedelta
import logging

import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from booking.models import Film, Showtime, RATING_CHOICES, Showtime
from dashboard.services.ai_rating import classify_rating_with_ai
from .utils import build_embed_url
from datetime import datetime
from dashboard.services.tmdb_reviews import get_tmdb_reviews


logger = logging.getLogger(__name__)


# Views


def dashboard_view(request):
    """Render the main dashboard with carousels and upcoming showtimes."""
    new_releases = Film.objects.filter(is_new_release=True, is_active=True)[:6]
    classic_films = Film.objects.filter(is_classic=True, is_active=True)[:6]

    today = timezone.now().date()
    date_filter = request.GET.get("date", "today")
    genre_filter = request.GET.get("genre")

    # Search query
    query = request.GET.get("q")

    start_date = today
    end_date = None

    if date_filter == "today":
        start_date = today
        end_date = today

    elif date_filter == "tomorrow":
        start_date = today + timedelta(days=1)
        end_date = start_date

    elif date_filter == "this-week":
        start_date = today
        end_date = today + timedelta(days=6)

    elif date_filter == "next-week":
        start_date = today + timedelta(days=7)
        end_date = today + timedelta(days=13)

    elif date_filter:
        # Custom date (YYYY-MM-DD)
        try:
            start_date = end_date = timezone.datetime.strptime(
                date_filter, "%Y-%m-%d"
            ).date()
        except ValueError:
            pass

    showtime_filter = {
        "date__gte": start_date,
        "is_available": True,
        "film__is_active": True,
    }

    if end_date:
        showtime_filter["date__lte"] = end_date

    if genre_filter:
        showtime_filter["film__genre"] = genre_filter

    upcoming_showtimes = (
        Showtime.objects.filter(**showtime_filter)
        .select_related("film", "screen")
        .order_by("date", "time")
    )

    # If query for search
    if query:
        upcoming_showtimes = upcoming_showtimes.filter(
            film__title__icontains=query
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

    films_with_reviews = {}

    for film in films_with_showtimes.keys():
        films_with_reviews[film.id] = get_tmdb_reviews(film.tmdb_id)

    context = {
        "new_releases": new_releases,
        "classic_films": classic_films,
        "film_strip": Film.objects.filter(is_active=True).order_by('-is_new_release','title')[:12],
        "films_with_showtimes": films_with_showtimes,
        "films_with_reviews": films_with_reviews,
        "selected_date": date_filter,
        "selected_genre": genre_filter or "",
        "query": query, 
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
                film.trailer_url = f"https://www.youtube.com/embed/{video_id}"
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

    # Always store the proper embed URL
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

def movie_details(request, tmdb_id):
    film = Film.objects.get(tmdb_id=tmdb_id)

    # Build safe YouTube embed URL
    embed_url = build_embed_url(request, film.trailer_url)

    # Server-side: try to resolve the video via the YouTube Data API and
    # retrieve the API-provided embed HTML (safer to render the provider's
    # canonical embed snippet). If the stored URL is missing, fall back to a
    # search for the top trailer result for the film title.
    api_embed_html = None
    api_embeddable = None
    api_video_id = None
    api_error = None

    yt_key = os.environ.get('YOUTUBE_API_KEY')
    try:
        # Extract video id from stored trailer_url if possible
        trailer = film.trailer_url or ""
        vid = None
        if trailer:
            if '/embed/' in trailer:
                vid = trailer.split('/embed/')[-1].split('?')[0]
            elif 'v=' in trailer:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(trailer)
                vid = parse_qs(parsed.query).get('v', [None])[0]
            elif 'youtu.be' in trailer:
                from urllib.parse import urlparse
                parsed = urlparse(trailer)
                vid = parsed.path.lstrip('/')

        # If we have an id, fetch the video's details
        if not yt_key:
            api_error = 'YOUTUBE_API_KEY not set'
        else:
            if vid:
                api_url = (
                    'https://www.googleapis.com/youtube/v3/videos'
                    f'?part=player,status,snippet&id={vid}'
                    f'&key={yt_key}'
                )
                resp = requests.get(api_url, timeout=8).json()
                items = resp.get('items', [])
                if items:
                    item = items[0]
                    api_embed_html = item.get('player', {}).get('embedHtml')
                    api_embeddable = item.get('status', {}).get('embeddable')
                    api_video_id = item.get('id')
                else:
                    # No item for that id; try searching by title
                    search_q = f"{film.title} official trailer"
                    search_url = (
                        'https://www.googleapis.com/youtube/v3/search'
                        f'?part=snippet&type=video&maxResults=1&q={search_q}'
                        f'&key={yt_key}'
                    )
                    sresp = requests.get(search_url, timeout=8).json()
                    sitems = sresp.get('items', [])
                    if sitems:
                        found_id = sitems[0].get('id', {}).get('videoId')
                        if found_id:
                            api_video_id = found_id
                            api_url = (
                                'https://www.googleapis.com/youtube/v3/videos'
                                f'?part=player,status,snippet&id={found_id}'
                                f'&key={yt_key}'
                            )
                            resp2 = requests.get(api_url, timeout=8).json()
                            i2 = resp2.get('items', [])
                            if i2:
                                item2 = i2[0]
                                api_embed_html = (
                                    item2.get('player', {})
                                    .get('embedHtml')
                                )
                                api_embeddable = (
                                    item2.get('status', {})
                                    .get('embeddable')
                                )
                                api_video_id = item2.get('id')
            else:
                # No stored trailer URL -> search by title
                if yt_key:
                    search_q = f"{film.title} official trailer"
                    search_url = (
                        'https://www.googleapis.com/youtube/v3/search'
                        f'?part=snippet&type=video&maxResults=1&q={search_q}'
                        f'&key={yt_key}'
                    )
                    sresp = requests.get(search_url, timeout=8).json()
                    sitems = sresp.get('items', [])
                    if sitems:
                        found_id = sitems[0].get('id', {}).get('videoId')
                        if found_id:
                            api_video_id = found_id
                            api_url = (
                                'https://www.googleapis.com/youtube/v3/videos'
                                f'?part=player,status,snippet&id={found_id}'
                                f'&key={yt_key}'
                            )
                            resp2 = requests.get(api_url, timeout=8).json()
                            i2 = resp2.get('items', [])
                            if i2:
                                item2 = i2[0]
                                api_embed_html = (
                                    item2.get('player', {})
                                    .get('embedHtml')
                                )
                                api_embeddable = (
                                    item2.get('status', {})
                                    .get('embeddable')
                                )
                                api_video_id = item2.get('id')
    except Exception as e:
        logger.exception('YouTube API error when resolving trailer: %s', e)
        api_error = str(e)

    now = timezone.localtime()

    # Build list of upcoming showtimes
    showtimes = []
    for s in film.showtimes.all().order_by("date", "time"):
        naive_dt = datetime.combine(s.date, s.time)
        show_dt = timezone.make_aware(naive_dt)

        if show_dt >= now:
            showtimes.append(s)

    # Group showtimes by date for template display: produce a list of
    # (date, [showtimes]) tuples in chronological order.
    grouped_showtimes_list = []
    if showtimes:
        current_date = None
        current_list = []
        for s in showtimes:
            if current_date is None:
                current_date = s.date
                current_list = [s]
            elif s.date == current_date:
                current_list.append(s)
            else:
                grouped_showtimes_list.append((current_date, current_list))
                current_date = s.date
                current_list = [s]

        if current_date is not None:
            grouped_showtimes_list.append((current_date, current_list))

    # Build seat layout mapping (screen_id → seats)
    screen_seats = {
        s.screen.id: s.screen.seat_layout.all()
        for s in showtimes
    }

    return render(request, "dashboard/movie_details.html", {
        "film": film,
        "embed_url": embed_url,
        "api_embed_html": api_embed_html,
        "api_embeddable": api_embeddable,
        "api_video_id": api_video_id,
        "api_error": api_error,
        "showtimes": showtimes,
        "grouped_showtimes": grouped_showtimes_list,
        "screen_seats": screen_seats,
    })

