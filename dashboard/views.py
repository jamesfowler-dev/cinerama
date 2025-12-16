import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from booking.models import Film

# Create your views here.

def dashboard_view(request):
    # Sample data - replace with actual database queries later
    context = {
        'new_releases': [
            {'title': 'Latest Movie 1', 'poster': 'images/movie1.jpg'},
            {'title': 'Latest Movie 2', 'poster': 'images/movie2.jpg'},
            {'title': 'Latest Movie 3', 'poster': 'images/movie3.jpg'},
        ],
        'classic_films': [
            {'title': 'Classic Film 1', 'poster': 'images/classic1.jpg'},
            {'title': 'Classic Film 2', 'poster': 'images/classic2.jpg'},
            {'title': 'Classic Film 3', 'poster': 'images/classic3.jpg'},
        ],
        'whats_on': [
            {
                'title': 'Movie Title 1',
                'poster': 'images/movie1.jpg',
                'showtimes': ['14:00', '17:30', '20:00', '22:30'],
                'rating': 'PG-13',
                'genre': 'Action, Adventure'
            },
            {
                'title': 'Movie Title 2',
                'poster': 'images/movie2.jpg',
                'showtimes': ['15:00', '18:00', '21:00'],
                'rating': '15',
                'genre': 'Drama, Thriller'
            },
            {
                'title': 'Movie Title 3',
                'poster': 'images/movie3.jpg',
                'showtimes': ['16:00', '19:00', '21:45'],
                'rating': 'PG',
                'genre': 'Comedy, Family'
            },
        ]
    }
    return render(request, 'dashboard/dashboard.html', context)

def test_tmdb(request):
    api_key = settings.TMDB_API_KEY
    movie_id = 27205  # Inception

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    config_url = f"https://api.themoviedb.org/3/configuration?api_key={api_key}"

    movie = requests.get(url).json()
    config = requests.get(config_url).json()

    # Build full poster URL
    base = config["images"]["secure_base_url"]
    size = config["images"]["poster_sizes"][3]  # e.g., w342
    poster_url = f"{base}{size}{movie['poster_path']}"
    backdrop_url = f"https://image.tmdb.org/t/p/w1280{movie.get('backdrop_path')}"

    return render(request, "dashboard/test_tmdb.html", {"movie": movie, "poster": poster_url, "backdrop": backdrop_url})


@login_required
def add_movie(request):
    # Only admins can access this page
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
def select_movie(request, tmdb_id):
    # Only admins can save films
    if not request.user.is_staff:
        return HttpResponseForbidden("Admins only")

    api_key = settings.TMDB_API_KEY

    # Fetch full movie details
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&language=en-US"
    data = requests.get(url).json()

    # Create or update Film entry
    film, created = Film.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "title": data.get("title"),
            "poster_path": data.get("poster_path"),
            "runtime": data.get("runtime"),
            "release_date": data.get("release_date"),
            "overview": data.get("overview"),
            "genres": data.get("genres"),
        }
    )

    return redirect("add_movie")