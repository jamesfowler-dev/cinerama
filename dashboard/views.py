from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.conf import settings
from booking.models import Film, Showtime  # Add this import
from django.utils import timezone

def dashboard_view(request):
    # Get films for different categories
    new_releases = Film.objects.filter(
        is_new_release=True, 
        is_active=True
    )[:6]  # Limit to 6 for carousel
    
    classic_films = Film.objects.filter(
        is_classic=True, 
        is_active=True
    )[:6]  # Limit to 6 for carousel
    
    # Get today's and upcoming showtimes
    today = timezone.now().date()
    upcoming_showtimes = Showtime.objects.filter(
        date__gte=today,
        is_available=True,
        film__is_active=True
    ).select_related('film', 'screen').order_by('date', 'time')
    
    # Group showtimes by film for the "What's On" section
    films_with_showtimes = {}
    for showtime in upcoming_showtimes:
        if showtime.film not in films_with_showtimes:
            films_with_showtimes[showtime.film] = []
        films_with_showtimes[showtime.film].append({
            'id': showtime.id,
            'time': showtime.time.strftime('%H:%M'),
            'date': showtime.date,
            'price': showtime.price,
            'screen': showtime.screen,
            'available_seats': showtime.available_seats
        })
    
    context = {
        'new_releases': new_releases,
        'classic_films': classic_films,
        'films_with_showtimes': films_with_showtimes,
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

    return render(request, "dashboard/test_tmdb.html", {"movie": movie, "poster": poster_url})
