import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SPOTIFY_CLIENT_ID = "ad0720ec13024b85b3843b39cf06ee16"
SPOTIFY_CLIENT_SECRET = "f1469bb0f25d40959b903dd5618ea179"

def get_spotify_token():
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    return res.json().get("access_token")

def get_track_id(url):
    try:
        return url.split("track/")[1].split("?")[0]
    except:
        return None

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    track_id = get_track_id(url)

    if not track_id:
        return jsonify({"error": "Invalid URL"}), 400

    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)
    if res.status_code != 200:
        return jsonify({"error": "Spotify API error"}), 500

    track = res.json()
    return jsonify({
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "thumbnail": track["album"]["images"][0]["url"]
    })
