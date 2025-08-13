from googletrans import Translator

def translate_text(text, dest_lang='en', src_lang='auto'):
    """
    Translates text from source language to destination language.
    """
    translator = Translator()
    try:
        translation = translator.translate(text, dest=dest_lang, src=src_lang)
        return translation.text
    except Exception as e:
        print(f"Error during translation: {e}")
        return text # Return original text on error

# Example Usage:
if __name__ == "__main__":
    from chatbot_core import Chatbot
    from voice_integration import listen_to_user, speak_response

    chatbot = Chatbot()
    print("Multi-language Chatbot ready! Speak 'quit' to exit. You can speak in English or Tamil.")

    while True:
        user_spoken_input = listen_to_user()
        if user_spoken_input.lower() == 'quit':
            speak_response("Goodbye!")
            break
        elif user_spoken_input:
            # Detect language and translate to English for NLP
            translated_to_english = translate_text(user_spoken_input, dest_lang='en')
            print(f"Translated to English for NLP: {translated_to_english}")
            
            # Get response from chatbot in English
            english_response = chatbot.get_response(translated_to_english)
            
            # Translate response back to Tamil (or detected user language)
            # For simplicity, let's assume user wants response in Tamil if they spoke Tamil.
            # A more robust solution would store user's preferred language.
            
            # Here we assume if the original input was likely Tamil, respond in Tamil.
            # This is a simplification; ideally, you'd detect the source language of `user_spoken_input`
            # and use that for `dest_lang` in `speak_response`.
            # For now, let's just translate the English response to Tamil for demonstration.
            tamil_response = translate_text(english_response, dest_lang='ta')
            
            print(f"Bot (English): {english_response}")
            print(f"Bot (Tamil): {tamil_response}")
            speak_response(tamil_response, lang='ta') # Speak in Tamil
        else:
            speak_response("Please say something.")

