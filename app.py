from flask import Flask, request, send_file, jsonify
from transformers import pipeline
import io
import soundfile as sf
import os

app = Flask(__name__)

# Global variable for the model
tts_pipe = None

def load_model():
    global tts_pipe
    if tts_pipe is None:
        print("Loading VCTK European English Males model...")
        tts_pipe = pipeline("text-to-speech", model="voices/VCTK_European_English_Males")
        print("Model loaded successfully!")
    return tts_pipe

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "model": "VCTK European English Males",
        "endpoint": "/tts",
        "method": "POST",
        "example": {
            "text": "Hello, this is a test."
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        # Get text from request
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        print(f"Generating speech for: {text[:50]}...")
        
        # Load model (lazy loading)
        pipe = load_model()
        
        # Generate speech
        result = pipe(text)
        
        # Extract audio data
        audio_data = result['audio']
        sample_rate = result['sampling_rate']
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='FLAC')
        buffer.seek(0)
        
        print("Speech generated successfully!")
        
        return send_file(
            buffer,
            mimetype='audio/flac',
            as_attachment=True,
            download_name='speech.flac'
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
