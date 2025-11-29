from flask import Flask, request, send_file, jsonify
import requests
import io
import os

app = Flask(__name__)

# Get API keys from environment variables
def get_api_keys():
    keys = {}
    for i in range(1, 8):  # Support up to 7 keys
        key = os.environ.get(f'ELEVENLABS_KEY_{i}')
        if key:
            keys[f'account_{i}'] = key
    return keys

ELEVENLABS_KEYS = get_api_keys()

if not ELEVENLABS_KEYS:
    print("⚠️ WARNING: No API keys found in environment variables!")
    print("Add ELEVENLABS_KEY_1, ELEVENLABS_KEY_2, etc. to your Render environment")

# Adam voice ID only
ADAM_VOICE_ID = 'pNInz6obpgDQGcFmaJgB'

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "model": "ElevenLabs TTS - Adam Voice",
        "endpoint": "/tts",
        "voice": "Adam (Deep Male)",
        "available_accounts": list(ELEVENLABS_KEYS.keys()),
        "total_accounts": len(ELEVENLABS_KEYS),
        "pricing": f"Free tier: {len(ELEVENLABS_KEYS) * 10000} chars/month total"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "accounts_available": len(ELEVENLABS_KEYS)
    }), 200

@app.route('/accounts')
def list_accounts():
    """List all available accounts"""
    return jsonify({
        "accounts": list(ELEVENLABS_KEYS.keys()),
        "total": len(ELEVENLABS_KEYS)
    })

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        account = data.get('account', None)  # Optional: which account to use
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 2500:
            return jsonify({'error': 'Text too long (max 2500 chars)'}), 400
        
        if not ELEVENLABS_KEYS:
            return jsonify({'error': 'No API keys configured'}), 500
        
        # Determine which API key to use
        if account and account in ELEVENLABS_KEYS:
            # Use specific account
            api_key = ELEVENLABS_KEYS[account]
            print(f"Using specified account: {account}")
            accounts_to_try = [(account, api_key)]
        else:
            # Try all accounts in order
            print("No account specified, trying all accounts...")
            accounts_to_try = list(ELEVENLABS_KEYS.items())
        
        print(f"Generating speech with Adam voice for: {text[:50]}...")
        
        # Try with selected account(s)
        for account_name, api_key in accounts_to_try:
            print(f"Trying {account_name}...")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{ADAM_VOICE_ID}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                buffer = io.BytesIO(response.content)
                buffer.seek(0)
                print(f"✅ Speech generated successfully with {account_name}!")
                
                # Return audio with account info in header
                return send_file(
                    buffer,
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name='speech.mp3'
                ), 200, {'X-Account-Used': account_name}
                
            elif response.status_code == 401:
                print(f"⚠️ {account_name}: Unauthorized (invalid key)")
                if account:  # If specific account was requested, don't try others
                    return jsonify({'error': f'{account_name} has invalid API key'}), 401
                continue
                
            elif response.status_code == 429:
                print(f"⚠️ {account_name}: Quota exceeded")
                if account:  # If specific account was requested, don't try others
                    return jsonify({'error': f'{account_name} quota exceeded'}), 429
                continue
                
            else:
                print(f"❌ {account_name} Error {response.status_code}: {response.text}")
                if account:
                    return jsonify({'error': f'{account_name} error: {response.status_code}'}), response.status_code
                continue
        
        # All accounts failed
        return jsonify({'error': 'All accounts exhausted or unavailable'}), 429
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
