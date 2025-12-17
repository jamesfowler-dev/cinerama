import logging
import os
import requests

logger = logging.getLogger(__name__)
ALLOWED_RATINGS = {"G", "PG", "PG-13", "15", "18", "R"}


def classify_rating_with_ai(title, synopsis, genres, cast):
    """
    Calls GitHub Models (gpt-4.1-mini) to classify a film rating.
    Returns one of: G, PG, PG-13, 15, 18, R
    """
    logger.debug("AI FUNCTION CALLED")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")

    prompt_lines = [
        "You are a film classification assistant.",
        "Assign a rating from this list ONLY:",
        ", ".join(sorted(ALLOWED_RATINGS)),
        "",
        f"Film title: {title}",
        f"Synopsis: {synopsis}",
        f"Genres: {genres}",
        f"Cast: {cast}",
        "",
        "Respond with ONLY one rating from the list.",
    ]
    prompt = "\n".join(prompt_lines)

    url = "https://models.inference.ai.azure.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": "You classify films into age ratings.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 10,
        "temperature": 0.0
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    resp = response.json()
    ai_text = resp["choices"][0]["message"]["content"].strip()

    # Safety: enforce allowed values
    if ai_text not in ALLOWED_RATINGS:
        logger.warning("AI returned unexpected rating: %s", ai_text)
        return "PG"

    return ai_text
