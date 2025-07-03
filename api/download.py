from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    spotify_url = data.get('url')

    if not spotify_url:
        return jsonify({'error': 'No Spotify URL provided'}), 400

    try:
        # Extract Spotify info
        res = requests.get(f"https://open.spotify.com/oembed?url={spotify_url}")
        embed = res.json()

        title = embed.get("title", "Unknown")
        thumbnail = embed.get("thumbnail_url", "")
        artist = "Unknown"

        if " - " in title:
            title, artist = title.split(" - ", 1)

        return jsonify({
            "title": title.strip(),
            "artist": artist.strip(),
            "thumbnail": thumbnail
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
