from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import json
import base64

from brainrot_generation_justin_version import video_generator

app = Flask(__name__)
CORS(app)  # Enable CORS so Next.js can access the Flask API

@app.route('/api/upload_data', methods=['POST', 'GET'])
def upload_data():
    try:
        snippets = request.json
        if not snippets:
            return jsonify({"error": "Invalid data"}), 400

        videos_byte_data = []
        for key in snippets:
            video_data = video_generator.get_video(snippets[key])
            base64_video = base64.b64encode(video_data.read()).decode('utf-8')  # Encode the video to base64
            videos_byte_data.append(base64_video)

        return jsonify({"videos": videos_byte_data}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs the full traceback in the server logs
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)