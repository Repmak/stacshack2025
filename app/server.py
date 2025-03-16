from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import json
import base64
import random
import os
import io
import subprocess

from gtts import gTTS
import moviepy as mpe
from pydub import AudioSegment
import tempfile


from brainrot_generation_justin_version import video_generator

app = Flask(__name__)
CORS(app)  # Enable CORS so Next.js can access the Flask API

def temp_get_vid():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(repo_dir, "videos")
    print(videos_dir + "/BKRQ1287.mp4")
    final_clip = mpe.VideoFileClip(videos_dir + "\BKRQ1287.mp4")

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as temp_video:
        temp_path = temp_video.name  # Get the file path
        final_clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", threads=4)

        # Read the temp file into BytesIO
        with open(temp_path, "rb") as f:
            video_output = io.BytesIO(f.read())

    return video_output

@app.route('/api/upload_data', methods=['POST', 'GET'])
def upload_data():
    try:
        snippets = request.json
        if not snippets:
            return jsonify({"error": "Invalid data"}), 400

        videos_byte_data = []
        for key in snippets:
            #video_data = video_generator.get_video(snippets[key])
            video_data = temp_get_vid()
            base64_video = base64.b64encode(video_data.read()).decode('utf-8')  # Encode the video to base64
            videos_byte_data.append(base64_video)


        return jsonify({"videos": videos_byte_data}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs the full traceback in the server logs
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
