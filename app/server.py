from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS so Next.js can access the Flask API

@app.route('/api/upload_data', methods=['GET'])
def get_data():
    try:
        snippets = request.json.get()
        if not snippets:
            return jsonify({"error": "Invalid data"}), 400
        print(snippets)

        return jsonify({"output": "fr"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs the full traceback in the server logs
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)