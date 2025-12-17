from django.utils import timezone

def build_embed_url(request, trailer_url):
    if not trailer_url:
        return None

    origin = request.build_absolute_uri('/')[:-1]  # remove trailing slash

    # If URL already has parameters, append with &
    joiner = "&" if "?" in trailer_url else "?"

    return f"{trailer_url}{joiner}enablejsapi=1&origin={origin}&modestbranding=1"
