from flask import Flask, request, send_file, jsonify
import requests
import io

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "model": "MMS TTS English",
        "endpoint": "/tts"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Text too long'}), 400
        
        print(f"Generating: {text[:50]}...")
        
        response = requests.post(
            HF_API_URL,
            json={"inputs": text},
            timeout=60
        )
        
        if response.status_code == 200:
            buffer = io.BytesIO(response.content)
            return send_file(
                buffer,
                mimetype='audio/flac',
                as_attachment=True,
                download_name='speech.flac'
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
