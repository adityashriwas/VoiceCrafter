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
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process voice cloning
        model_path = process_voice_clone(filepath)

        return jsonify({
            'message': 'Voice profile created successfully',
            'model_path': model_path
        })
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': 'Error processing audio file'}), 500

@app.route('/generate', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        text = data.get('text')
        model_path = data.get('model_path', 'default_voice')

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