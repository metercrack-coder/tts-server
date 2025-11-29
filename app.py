from flask import Flask, request, send_file, jsonify
import requests
import io

app = Flask(__name__)

# StreamElements voices - truly free and unlimited
VOICES = {
    'brian': 'Brian',      # Deep male - closest to Adam
    'justin': 'Justin',    # Young male
    'matthew': 'Matthew',  # Professional male
    'joey': 'Joey',        # Casual male
    'russell': 'Russell',  # Australian male
    'emma': 'Emma',        # British female
    'joanna': 'Joanna',    # Natural female
    'salli': 'Salli',      # Friendly female
}

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "model": "StreamElements TTS",
        "endpoint": "/tts",
        "available_voices": list(VOICES.keys()),
        "default_voice": "brian",
        "pricing": "✅ 100% FREE & UNLIMITED"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice = data.get('voice', 'brian')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long'}), 400
        
        voice_name = VOICES.get(voice.lower(), VOICES['brian'])
        
        print(f"Generating speech with voice '{voice_name}' for: {text[:50]}...")
        
        url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice_name}&text={requests.utils.quote(text)}"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            buffer = io.BytesIO(response.content)
            buffer.seek(0)
            
            print("Speech generated successfully!")
            
            return send_file(
                buffer,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='speech.mp3'
            )
        else:
            return jsonify({'error': f'API error: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
