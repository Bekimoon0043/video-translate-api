import io
import requests
from flask import Flask, request, send_file, render_template, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Google Translate TTS endpoint
GOOGLE_TTS_URL = "https://translate.google.com/translate_tts"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    # Get parameters from JSON or form
    if request.is_json:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('lang', 'am')
    else:
        text = request.form.get('text', '')
        lang = request.form.get('lang', 'am')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Google TTS expects 'tl' (target language) parameter
    params = {
        'ie': 'UTF-8',
        'q': text,
        'tl': lang,
        'client': 'tw-ob'  # This client works without an API key
    }

    try:
        # Make the request to Google TTS
        response = requests.get(GOOGLE_TTS_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes

        # Return the audio (MP3) directly
        return send_file(
            io.BytesIO(response.content),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Google TTS error: {e}")
        return jsonify({'error': f'TTS request failed: {str(e)}'}), 500

@app.route('/debug', methods=['POST'])
def debug():
    """Helper endpoint to inspect received data"""
    data = request.get_json() if request.is_json else request.form.to_dict()
    return jsonify({
        'received': data,
        'headers': dict(request.headers)
    })

if __name__ == '__main__':
    app.run(debug=True)
