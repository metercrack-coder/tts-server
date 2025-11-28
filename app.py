from flask import Flask, request, send_file, jsonify
import requests
import io
import os

app = Flask(__name__)

# Updated API endpoint - use the router endpoint instead
HF_API_URL = "https://router.huggingface.co/models/facebook/mms-tts-eng"
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
        
        print(f"Generating speech for: {text[:50]}...")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization header if token is available
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        # Make request to Hugging Face
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text},
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Return the audio file
            buffer = io.BytesIO(response.content)
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='audio/flac',
                as_attachment=True,
                download_name='speech.flac'
            )
        elif response.status_code == 503:
            return jsonify({
                'error': 'Model is loading. Please wait 20 seconds and try again.'
            }), 503
        else:
            error_details = response.text[:300]
            print(f"Error from HF: {error_details}")
            return jsonify({
                'error': f'API error: {response.status_code}',
                'details': error_details
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout. Please try again.'}), 504
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
