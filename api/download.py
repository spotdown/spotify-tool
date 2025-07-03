import json
import requests

def handler(request, response):
    if request.method != "POST":
        return response.status(405, "Method Not Allowed")

    try:
        body = request.json()
        spotify_url = body.get("url")

        if not spotify_url:
            return response.status(400, "Missing Spotify URL")

        # Extract info from Spotify
        r = requests.get(f"https://open.spotify.com/oembed?url={spotify_url}")
        data = r.json()

        title = data.get("title", "Unknown")
        thumbnail = data.get("thumbnail_url", "")
        artist = "Unknown"

        if " - " in title:
            title, artist = title.split(" - ", 1)

        return response.json({
            "title": title.strip(),
            "artist": artist.strip(),
            "thumbnail": thumbnail
        })

    except Exception as e:
        return response.status(500, f"Error: {str(e)}")
