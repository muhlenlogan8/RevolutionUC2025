import os
from dotenv import load_dotenv
from google import genai
from google.cloud import texttospeech
from PIL import Image
from playsound import playsound
from AppKit import NSSound

load_dotenv()

image = Image.open('lock.jpg')

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
response = gemini_client.models.generate_content(
    model="gemini-2.0-flash", contents=["What is this image?", image]
)
print(response.text);

client = texttospeech.TextToSpeechClient()

synthesis_input = texttospeech.SynthesisInput(text=response.text)

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

with open("output.mp3", "wb") as out:
    out.write(response.audio_content)

playsound("output.mp3")