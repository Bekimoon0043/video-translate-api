import io
from flask import Flask, request, send_file, render_template, jsonify
from gtts import gTTS
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n and other cross-origin requests

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    # Get parameters from either JSON or form data
    if request.is_json:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('lang', 'am')
    else:
        text = request.form.get('text', '')
        lang = request.form.get('lang', 'am')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to in-memory bytes buffer
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        # Return the audio file
        return send_file(
            mp3_fp,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
