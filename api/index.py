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
    title = res.get("name", "unknown title")
    artist = res.get("artists", [{}])[0].get("name", "unknown artist")
    return f"{title} {artist}"

def download_mp3_from_youtube(query):
    output_dir = tempfile.gettempdir()
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        entry = info["entries"][0] if "entries" in info else info
        title = entry.get("title", "track")
        filename = os.path.join(output_dir, f"{title}.mp3")
        return filename if os.path.exists(filename) else None

@app.route("/", methods=["GET"])
def home():
    return "✅ SpotTool Backend is running on Vercel!"

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        spotify_url = data.get("url")
        if not spotify_url:
            return jsonify({"error": "Missing Spotify URL"}), 400

        query = get_song_query(spotify_url)
        mp3_file = download_mp3_from_youtube(query)

        if not mp3_file or not os.path.exists(mp3_file):
            return jsonify({"error": "Failed to download MP3"}), 500

        return send_file(mp3_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
