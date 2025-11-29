from flask import Flask, request, send_file, jsonify
import edge_tts
import asyncio
import io
import os

app = Flask(__name__)

# Popular natural-sounding voices
VOICES = {
    'andrew': 'en-US-AndrewNeural',          # Male, natural, great for content
    'brian': 'en-US-BrianNeural',            # Male, deep voice
    'christopher': 'en-US-ChristopherNeural', # Male, professional
    'eric': 'en-US-EricNeural',              # Male, friendly
    'guy': 'en-US-GuyNeural',                # Male, warm
    'davis': 'en-US-DavisNeural',            # Male, storyteller (HIGHLY RECOMMENDED)
    'tony': 'en-US-TonyNeural',              # Male, authoritative
    'jason': 'en-US-JasonNeural',            # Male, casual
    'jenny': 'en-US-JennyNeural',            # Female, clear
    'aria': 'en-US-AriaNeural',              # Female, natural
    'michelle': 'en-US-MichelleNeural',      # Female, professional
    'sara': 'en-US-SaraNeural',              # Female, soft
}

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "model": "Microsoft Edge TTS",
        "endpoint": "/tts",
        "available_voices": list(VOICES.keys()),
        "pricing": "FREE & UNLIMITED",
        "default_voice": "andrew"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice = data.get('voice', 'andrew')  # Default to Andrew
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        # Get voice ID
        voice_id = VOICES.get(voice.lower(), VOICES['andrew'])
        
        print(f"Generating speech with voice '{voice}' for: {text[:50]}...")
        
        # Generate speech using Edge TTS
        audio_data = asyncio.run(generate_speech(text, voice_id))
        
        if audio_data:
            buffer = io.BytesIO(audio_data)
            buffer.seek(0)
            
            print(f"Speech generated successfully! Size: {len(audio_data)} bytes")
            
            return send_file(
                buffer,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='speech.mp3'
            )
        else:
            return jsonify({'error': 'Failed to generate speech'}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

async def generate_speech(text, voice):
    """Generate speech using Edge TTS"""
    try:
        # Create Edge TTS communicate object
        communicate = edge_tts.Communicate(text, voice)
        
        # Collect audio data chunks
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    except Exception as e:
        print(f"Edge TTS generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
