from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from google import genai
from google.cloud import texttospeech
from PIL import Image
import cv2
import numpy as np
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

AI_TEXT_FILE = "aitext.txt"
AUDIO_FILE = "output.mp3"

def process_fix_image_colors():
    file_path = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    img = cv2.imread(file_path)
    (B, G, R) = cv2.split(img)
    threshold = 0
    attenuation_factor = 0.25
    R[R > threshold] = R[R > threshold] - (R[R > threshold] - threshold) * attenuation_factor
    R = np.clip(R, 0, 255)
    attenuated_image = cv2.merge([B, G, R])
    cv2.imwrite(file_path, attenuated_image)

def generate_ai_text_and_audio(image_path):
    """Generates AI text and converts it to speech."""
    try:
        image = Image.open(image_path)

        # Generate AI description
        gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Describe the contents of this image as if you are explaining it to someone who is blind. Start your response with: \"Here's what you are looking at: ...\" Focus on identifying objects, people, actions, and any meaningful details that help someone understand what is in front of them. If there is any text in the image, mention that text is present but do not attempt to read or interpret it. Ignore any blur, image tint, strange coloration, or other visual distortions—do not mention them. Structure your response by first describing the main subject, then the background elements, and finally noting the presence of any text. Keep the response concise but informative, avoiding unnecessary details, while providing as much useful information as possible, including object colors, relative positions, and any actions taking place.", image])
        ai_text = response.text
        print("AI Response:", ai_text)

        # Save AI text to a file
        with open(AI_TEXT_FILE, "w") as text_file:
            text_file.write(ai_text)

        # Convert text to speech
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=ai_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        speech_response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(AUDIO_FILE, "wb") as out:
            out.write(speech_response.audio_content)

    except Exception as e:
        print(f"AI processing failed: {str(e)}")

@app.route("/upload", methods=["POST"])
def upload_image():
    file_path = os.path.join(UPLOAD_FOLDER, "latest.jpg")

    try:
        img_data = request.data
        if not img_data:
            return jsonify({"error": "No image data received"}), 400
        
        with open(file_path, "wb") as f:
            f.write(img_data)
            
        process_fix_image_colors()
        generate_ai_text_and_audio(file_path)  # AI processing now happens here

        return jsonify({"message": "Image processed", "url": "/image/latest.jpg"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

@app.route("/aitext", methods=["GET"])
def get_ai_text():
    if os.path.exists(AI_TEXT_FILE):
        with open(AI_TEXT_FILE, "r") as text_file:
            ai_text = text_file.read()
        return jsonify({"text": ai_text})
    return jsonify({"error": "No AI text available"}), 404

@app.route("/image/latest.jpg")
def get_latest_image():
    image_path = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    if os.path.exists(image_path):
        return send_from_directory(UPLOAD_FOLDER, "latest.jpg")
    return jsonify({"error": "No image available"}), 404

@app.route("/audio/output.mp3")
def get_audio():
    if os.path.exists(AUDIO_FILE):
        return send_file(AUDIO_FILE, mimetype="audio/mp3")
    return jsonify({"error": "No audio available"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)