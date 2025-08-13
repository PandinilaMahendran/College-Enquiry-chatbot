import os
import json
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv
from eligibility_checker import check_admission_eligibility_from_text
from langdetect import detect

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Google AI Model Setup ---
API_KEY = os.getenv("GOOGLE_API_KEY")
model = None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Google AI Model configured successfully.")
    except Exception as e:
        print(f"🔴 Could not configure Google API. Error: {e}")
else:
    print("🔴 GOOGLE_API_KEY not found in .env file.")

# --- Knowledge Base ---
try:
    with open('knowledge_base.json', 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)
    knowledge_base_string = json.dumps(knowledge_base['intents'], indent=2, ensure_ascii=False)
    print("✅ Knowledge Base loaded successfully.")
except FileNotFoundError:
    print("🔴 knowledge_base.json not found.")
    knowledge_base = {"intents": []}
    knowledge_base_string = "[]"

# Ensure audio folder exists
os.makedirs('static/audio', exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    response_data = {
        'response': "Sorry, I couldn't process your request.",
        'audio_url': None,
        'image_url': None,
        'suggestions': []
    }

    try:
        user_message = request.json.get('message', '').strip()
        detected_lang = detect(user_message)
        print(f"📝 Detected language: {detected_lang}")

        # --- 1. Eligibility check ---
        if "%" in user_message:
            eligibility_result = check_admission_eligibility_from_text(user_message)
            if "Please mention both" not in eligibility_result:
                return create_tts_response(eligibility_result, lang_code=detected_lang)

        # --- 2. Direct KB match ---
        matched_intent = None
        for intent in knowledge_base['intents']:
            if any(pattern.lower() in user_message.lower() for pattern in intent['patterns']):
                matched_intent = intent
                break

        if matched_intent:
            response_text = matched_intent['responses'][0]
            response_data['image_url'] = matched_intent.get('image_url')
        else:
            # --- 3. AI Fallback ---
            if not model:
                return jsonify({"response": "AI Model is not configured.", "audio_url": None}), 500

            system_prompt = (
                "You are 'Erode Sengunthar College Bot', a helpful AI assistant for Erode Sengunthar Engineering College. "
                "Strictly use the provided JSON knowledge base for answers.\n\n"
                f"KNOWLEDGE BASE:\n{knowledge_base_string}\n\n"
            )

            full_prompt = f"{system_prompt}USER QUESTION: {user_message}"
            ai_response = model.generate_content(full_prompt)
            response_text = ai_response.text

        return create_tts_response(response_text, image_url=response_data.get('image_url'), lang_code=detected_lang)

    except Exception as e:
        print(f"🔴 Error in /chat: {e}")
        return jsonify({"response": "Internal error", "audio_url": None}), 500


def create_tts_response(text, image_url=None, lang_code='en'):
    """Generates TTS audio and returns structured JSON."""
    # Force Malayalam if detected
    if lang_code == "ml":
        print("🔊 Generating Malayalam audio...")
        tts = gTTS(text=text, lang='ml', tld='co.in')
    else:
        tts = gTTS(text=text, lang='en', tld='co.in')

    audio_filename = f'{hash(text)}_{lang_code}.mp3'
    audio_path = os.path.join('static', 'audio', audio_filename)
    tts.save(audio_path)

    return jsonify({
        'response': text,
        'audio_url': f'/static/audio/{audio_filename}',
        'image_url': image_url
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
