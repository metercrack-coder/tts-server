from flask import Flask, request, send_file, jsonify
from gtts import gTTS
import io

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "model": "Google TTS",
        "endpoint": "/tts",
        "message": "Send POST request to /tts with JSON body: {\"text\": \"your text here\"}"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        # Get JSON data from request
        data = request.get_json()
        text = data.get('text', '').strip()
        
        # Validate input
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        print(f"Generating speech for: {text[:50]}...")
        
        # Generate speech using Google TTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to memory buffer (not to disk)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        
        print("Speech generated successfully!")
        
        # Return MP3 file
        return send_file(
            buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
