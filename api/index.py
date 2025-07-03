import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SPOTIFY_CLIENT_ID = os.environ.get("ad0720ec13024b85b3843b39cf06ee16")
SPOTIFY_CLIENT_SECRET = os.environ.get("f1469bb0f25d40959b903dd5618ea179")

def get_spotify_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    return response.json().get("access_token")

def get_song_query(spotify_url):
    spotify_id = spotify_url.split("/")[-1].split("?")[0]
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"https://api.spotify.com/v1/tracks/{spotify_id}", headers=headers).json()
    title = res.get("name", "Unknown Title")
    artist = res.get("artists", [{}])[0].get("name", "Unknown Artist")
    return f"{title} {artist}"

@app.route("/", methods=["GET"])
def home():
    return "✅ SpotTool Vercel Backend is Running!"

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        spotify_url = data.get("url")
        if not spotify_url:
            return jsonify({"error": "Missing Spotify URL"}), 400

        query = get_song_query(spotify_url)

        # Use an external service like spotifydown or yt1s
        # We're just passing back the song name & artist
        return jsonify({
            "query": query,
            "suggested_youtube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
