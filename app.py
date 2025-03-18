import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.audio_processor import process_voice_clone, generate_speech
from utils.language_detector import detect_language
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Since we're using gTTS, we'll return a default voice model
        model_path = process_voice_clone(None)

        return jsonify({
            'message': 'Voice settings initialized',
            'model_path': model_path
        })
    except Exception as e:
        logger.error(f"Error initializing voice: {str(e)}")
        return jsonify({'error': 'Error initializing voice settings'}), 500

@app.route('/generate', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        text = data.get('text')
        model_path = data.get('model_path')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Detect language
        language = detect_language(text)
        logger.debug(f"Detected language: {language} for text: {text}")

        # Generate speech
        output_path = generate_speech(text, model_path, language)
        logger.debug(f"Generated audio file at: {output_path}")

        return jsonify({
            'message': 'Audio generated successfully',
            'audio_path': output_path
        })
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return jsonify({'error': 'Error generating audio'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Error downloading file'}), 500