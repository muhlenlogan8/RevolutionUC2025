from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

@app.route("/upload", methods = ["POST"])
def uploadImage():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    filePath = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    file.save(filePath)
    
    return jsonify({"message": "Image received", "url": "/image/latest.jpg"}), 200

@app.route("/image/latest.jpg")
def getLatestImage():
    return send_from_directory(UPLOAD_FOLDER, "latest.jpg")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000, debug = True)
