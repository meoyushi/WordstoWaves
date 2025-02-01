from flask import send_from_directory
from flask import Flask, render_template
from flask import Flask, request, jsonify, send_file
import os
from pdf2image import convert_from_path
import pytesseract
from gtts import gTTS
from werkzeug.utils import secure_filename

app = Flask(__name__) 
@app.route('/')
def home():
    return render_template('index.html')





UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to process PDFs: Extract text and convert to speech
def process_file(file_path):
    images = convert_from_path(file_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    extracted_text = process_file(file_path)
    if not extracted_text.strip():
        return jsonify({"error": "No text found"}), 400

    tts = gTTS(extracted_text, lang="en")
    audio_filename = filename.replace(".pdf", ".mp3")
    audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
    tts.save(audio_path)

    return jsonify({"audio_url": f"/download/{audio_filename}"})

@app.route("/download/<filename>", methods=["GET"])
def download_audio(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
