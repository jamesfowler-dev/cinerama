import requests
from django.conf import settings

def get_tmdb_reviews(tmdb_id, limit=5):
    """
    Fetch reviews for a movie from TMDB
    """
    if not tmdb_id:
        return []

    url = (
        f"https://api.themoviedb.org/3/movie/{tmdb_id}/reviews"
        f"?api_key={settings.TMDB_API_KEY}&language=en-US"
    )

    response = requests.get(url, timeout=5)

    if response.status_code != 200:
        return []

    return response.json().get("results", [])[:limit]