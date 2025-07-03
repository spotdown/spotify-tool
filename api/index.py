import os
import tempfile
import yt_dlp
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SPOTIFY_CLIENT_ID = os.environ.get("ad0720ec13024b85b3843b39cf06ee16")
SPOTIFY_CLIENT_SECRET = os.environ.get("f1469bb0f25d40959b903dd5618ea179")

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    return response.json().get("access_token")

def get_song_query(spotify_url):
    spotify_id = spotify_url.split("/")[-1].split("?")[0]
    access_token = get_spotify_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(f"https://api.spotify.com/v1/tracks/{spotify_id}", headers=headers).json()
    title = res.get("name", "unknown title")
    artist = res.get("artists", [{}])[0].get("name", "unknown artist")
    return f"{title} {artist}"

def download_mp3_from_youtube(query):
    output_dir = tempfile.gettempdir()
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
