from flask import Flask, request, send_file, jsonify
import requests
import io
import os

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
# Add your Hugging Face API token here if you have one
HF_TOKEN = os.environ.get('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', '')

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
        
        headers = {"Content-Type": "application/json"}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text},
            timeout=60
        )
        
        print(f"HF Response Status: {response.status_code}")
        
        if response.status_code == 200:
            buffer = io.BytesIO(response.content)
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='audio/flac',
                as_attachment=True,
                download_name='speech.flac'
            )
        elif response.status_code == 503:
            return jsonify({'error': 'Model is loading, please try again in 20 seconds'}), 503
        else:
            error_msg = response.text[:200]
            print(f"HF Error: {error_msg}")
            return jsonify({'error': f'API error: {response.status_code}', 'details': error_msg}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
