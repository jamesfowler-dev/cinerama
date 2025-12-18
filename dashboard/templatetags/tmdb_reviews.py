
from django import template
import requests
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_tmdb_reviews(tmdb_id, count=5):
    """
    Fetches the latest TMDb reviews for a given movie (by TMDb ID).
    Returns a list of dictionaries containing 'author' and 'content'.
    Limits results to 'count' reviews.
    """
    if not tmdb_id:
        return []

    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/reviews"
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "en-US",
            "page": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        reviews = [{"author": r.get("author"), "content": r.get("content")} for r in results[:count]]
        return reviews
    except requests.RequestException:
        return []
