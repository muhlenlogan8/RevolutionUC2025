from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_image():
    file_path = os.path.join(UPLOAD_FOLDER, "latest.jpg")

    try:
        # Read raw binary data from request
        img_data = request.data
        if not img_data:
            return jsonify({"error": "No image data received"}), 400
        
        # Save as JPEG
        with open(file_path, "wb") as f:
            f.write(img_data)

        return jsonify({"message": "Image received", "url": "/image/latest.jpg"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

@app.route("/image/latest.jpg")
def get_latest_image():
    return send_from_directory(UPLOAD_FOLDER, "latest.jpg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
