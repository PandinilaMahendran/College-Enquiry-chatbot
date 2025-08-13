import speech_recognition as sr
from gtts import gTTS
import os
import pygame  # For playing audio

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Default language for the bot
current_language = 'en'  # Options: 'en' (English), 'ta' (Tamil), 'ml' (Malayalam)

# Mapping from display names to Google Speech Recognition & gTTS codes
LANGUAGE_CODES = {
    'en': 'en',       # English
    'ta': 'ta-IN',    # Tamil (India)
    'ml': 'ml-IN'     # Malayalam (India)
}

TTS_CODES = {
    'en': 'en',
    'ta': 'ta',
    'ml': 'ml'
}

def set_language(lang_code):
    """Set the bot's current language (en, ta, ml)."""
    global current_language
    if lang_code in LANGUAGE_CODES:
        current_language = lang_code
        print(f"Language changed to: {lang_code}")
    else:
        print(f"Unsupported language: {lang_code}")

def listen_to_user():
    """
    Listens to user's speech input from the microphone and converts it to text.
    Uses Google Speech Recognition API (requires internet connection).
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Listening... (Language: {current_language})")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Processing audio...")
            text = recognizer.recognize_google(audio, language=LANGUAGE_CODES[current_language])
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return ""

def speak_response(text):
    """
    Converts text to speech and plays it.
    Uses Google Text-to-Speech (gTTS).
    """
    try:
        tts = gTTS(text=text, lang=TTS_CODES[current_language], slow=False)
        audio_file = "temp_response.mp3"
        tts.save(audio_file)
        
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.unload()
        os.remove(audio_file)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Example usage
if __name__ == "__main__":
    from chatbot_core import Chatbot

    chatbot = Chatbot()
    print("Voice Chatbot ready! Speak 'quit' to exit.")

    # Example: Switching language
    # set_language('ta')  # Tamil
    # set_language('ml')  # Malayalam

    while True:
        user_spoken_input = listen_to_user()
        if user_spoken_input.lower() == 'quit':
            speak_response("Goodbye!")
            break
        elif user_spoken_input.lower() in ['tamil', 'ta']:
            set_language('ta')
            speak_response("நான் இப்போது தமிழில் பேசுகிறேன்.")
        elif user_spoken_input.lower() in ['malayalam', 'ml']:
            set_language('ml')
            speak_response("ഇപ്പോൾ ഞാൻ മലയാളത്തിൽ സംസാരിക്കും.")
        elif user_spoken_input.lower() in ['english', 'en']:
            set_language('en')
            speak_response("I will now speak in English.")
        elif user_spoken_input:
            response = chatbot.get_response(user_spoken_input)
            print(f"Bot: {response}")
            speak_response(response)
        else:
            speak_response("Please say something.")
