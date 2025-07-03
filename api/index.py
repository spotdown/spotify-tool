import os
import tempfile
import yt_dlp
import requests
from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("ad0720ec13024b85b3843b39cf06ee16")
SPOTIFY_CLIENT_SECRET = os.getenv("f1469bb0f25d40959b903dd5618ea179")

app = Flask(__name__)

def get_spotify_access_token():
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    return response.json().get("access_token")

def get_song_info(spotify_url):
    access_token = get_spotify_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    spotify_id = spotify_url.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotify.com/v1/tracks/{spotify_id}", headers=headers)
    data = response.json()
    title = data["name"]
    artist = data["artists"][0]["name"]
    return f"{title} {artist}"

def download_youtube_mp3(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "cookiefile": "cookies.txt"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        file_path = ydl.prepare_filename(info["entries"][0]).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return file_path

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        spotify_url = data.get("url")
        if not spotify_url:
            return jsonify({"error": "No URL provided"}), 400

        query = get_song_info(spotify_url)
        mp3_path = download_youtube_mp3(query)

        return send_file(mp3_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
