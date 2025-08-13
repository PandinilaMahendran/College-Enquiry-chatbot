from chatbot_core import Chatbot
from voice_integration import listen_to_user, speak_response
from multi_language import translate_text
from eligibility_checker import check_admission_eligibility
from email_notifier import send_query_email # For query ticketing

# --- Initialize Chatbot ---
chatbot = Chatbot()

# --- Main Interaction Loop ---
def start_chatbot():
    print("Welcome to Erode Sengunthar Engineering College Chatbot!")
    speak_response("Welcome to Erode Sengunthar Engineering College Chatbot! How can I help you today?")

    while True:
        user_input = listen_to_user() # Listen for voice input

        if not user_input:
            speak_response("I didn't catch that. Could you please repeat?")
            continue

        if user_input.lower() == 'quit':
            speak_response("Goodbye! Have a great day!")
            break

        # --- Language Detection and Translation ---
        # For simplicity, we'll assume English for NLP core and translate back to Tamil if needed.
        # A more advanced system would use a language detection library first.
        # For this example, let's assume if the user asks in Tamil, we respond in Tamil.
        # Otherwise, respond in English.
        
        # You'll need to implement actual language detection here for robust multi-language.
        # For now, let's just translate to English for intent recognition.
        translated_input_for_nlp = translate_text(user_input, dest_lang='en', src_lang='auto')
        
        # --- Get Chatbot Response (English) ---
        response_tag = chatbot.model.predict([" ".join(chatbot._preprocess_text(translated_input_for_nlp))])[0]
        
        # Handle special intents (eligibility, feedback, ticketing)
        if response_tag == "admissions": # General admissions query
            english_response = "For detailed admission information, please visit our official admissions page: https://erode-sengunthar.ac.in/admission/"
            # You could add a sub-question here: "Are you looking for eligibility criteria?"
        elif response_tag == "check_eligibility":
            speak_response("To check your eligibility, please tell me your 12th standard percentage?")
            percentage_str = listen_to_user()
            try:
                percentage = float(percentage_str)
            except ValueError:
                speak_response("That's not a valid percentage. Please enter a number.")
                continue

            speak_response("Which course are you interested in (e.g., CSE, ECE)?")
            course = listen_to_user()

            speak_response("Do you have a JEE score or a State Entrance Exam rank? If so, please provide it. Otherwise, say 'no'.")
            exam_score_input = listen_to_user()
            jee_score = None
            state_exam_score = None
            if exam_score_input.lower() != 'no':
                try:
                    if "jee" in exam_score_input.lower():
                        jee_score = float(exam_score_input.replace("jee", "").strip())
                    elif "state" in exam_score_input.lower() or "rank" in exam_score_input.lower():
                        state_exam_score = int(exam_score_input.replace("state", "").replace("rank", "").strip())
                except ValueError:
                    speak_response("Invalid score/rank. Proceeding without it.")

            speak_response("What is your category (e.g., General, SC, ST, OBC)?")
            category = listen_to_user()

            eligible, message = check_admission_eligibility(course, percentage, jee_score, state_exam_score, category)
            english_response = message # Get the eligibility message
            
        elif response_tag == "feedback":
            speak_response("We value your feedback! Please tell me your feedback message.")
            feedback_message = listen_to_user()
            speak_response("What is your name?")
            user_name_feedback = listen_to_user()
            speak_response("What is your email address (optional)?")
            user_email_feedback = listen_to_user()

            # Call the Flask feedback app endpoint (assuming it's running)
            # In a real scenario, you'd make an HTTP POST request here.
            # For this example, we'll just print a confirmation.
            print(f"Simulating sending feedback: From {user_name_feedback} ({user_email_feedback}): {feedback_message}")
            english_response = "Thank you for your feedback! It has been noted."
            # In a real app, you'd send this to your Flask app or a database.
            # import requests
            # try:
            #     requests.post("http://127.0.0.1:5000/submit_feedback", json={"user_id": user_name_feedback, "message": feedback_message, "email": user_email_feedback})
            #     english_response = "Thank you for your feedback! It has been submitted."
            # except requests.exceptions.ConnectionError:
            #     english_response = "I apologize, I couldn't connect to the feedback system. Please try again later."

        elif response_tag == "query_ticket":
            speak_response("I can help you raise a query ticket. What is your full name?")
            user_name_ticket = listen_to_user()
            speak_response("What is your email address?")
            user_email_ticket = listen_to_user()
            speak_response("Please describe your query in detail.")
            query_description_ticket = listen_to_user()

            if send_query_email(user_name_ticket, user_email_ticket, query_description_ticket, "your_college_staff_email@erode-sengunthar.ac.in"):
                english_response = f"Your query has been submitted to our support team. They will contact you shortly at {user_email_ticket}"
            else:
                english_response = "I apologize, but I was unable to submit your query at this time. Please try again later or contact the college directly."
        else:
            # For other intents, get the response directly from the chatbot core
            english_response = chatbot.get_response(translated_input_for_nlp)

        # --- Translate Response back to User's Language (if needed) ---
        # Here, we're simplifying: if user input was detected as Tamil, respond in Tamil.
        # Otherwise, respond in English.
        # A more robust system would use a proper language detection for `user_input`.
        
        # For demonstration, let's assume we respond in Tamil if the original input was Tamil.
        # This is a placeholder for actual language detection.
        # You might need a more sophisticated language detection for `user_input` here.
        # For now, let's just translate to Tamil if the input had Tamil characters.
        
        # A simple check (not robust language detection):
        # if any(u'\u0B80' <= char <= u'\u0BFF' for char in user_input): # Check for Tamil Unicode range
        #     final_response = translate_text(english_response, dest_lang='ta')
        #     speak_response(final_response, lang='ta')
        # else:
        #     final_response = english_response
        #     speak_response(final_response, lang='en')

        # For now, let's always translate to Tamil for demonstration of multi-language output
        final_response_tamil = translate_text(english_response, dest_lang='ta')
        print(f"Bot (English): {english_response}")
        print(f"Bot (Tamil): {final_response_tamil}")
        speak_response(final_response_tamil, lang='ta') # Speak in Tamil

if __name__ == "__main__":
    start_chatbot()

