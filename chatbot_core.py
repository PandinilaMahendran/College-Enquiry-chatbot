import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
import pickle
import os

# Download NLTK data (run once)
# This block checks if NLTK data is downloaded and gets it if it's missing.
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Wordnet resource not found. Downloading...")
    nltk.download('wordnet')
    print("Download complete.")

class Chatbot:
    def __init__(self, knowledge_base_path='knowledge_base.json', model_path='chatbot_model.pkl'):
        self.knowledge_base_path = knowledge_base_path
        self.model_path = model_path
        self.intents = self._load_knowledge_base()
        self.lemmatizer = WordNetLemmatizer()
        self.model = None
        self.vectorizer = None # Store vectorizer separately if needed for prediction
        self._train_model()

    def _load_knowledge_base(self):
        """Loads the chatbot's knowledge base from a JSON file."""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as file:
                return json.load(file)['intents']
        except FileNotFoundError:
            print(f"Error: Knowledge base file not found at {self.knowledge_base_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.knowledge_base_path}")
            return []

    def _preprocess_text(self, text):
        """Tokenizes, lowercases, and lemmatizes the input text."""
        tokens = nltk.word_tokenize(text.lower())
        return [self.lemmatizer.lemmatize(word) for word in tokens]

    def _train_model(self):
        """Trains the SVM model for intent classification."""
        if os.path.exists(self.model_path):
            print("Loading pre-trained model...")
            with open(self.model_path, 'rb') as file:
                self.model = pickle.load(file)
            print("Model loaded successfully.")
            return

        print("Training new model...")
        patterns = []
        tags = []

        for intent in self.intents:
            for pattern in intent['patterns']:
                patterns.append(" ".join(self._preprocess_text(pattern)))
                tags.append(intent['tag'])

        if not patterns:
            print("No training data found in knowledge base. Cannot train model.")
            return

        # Create a pipeline with TF-IDF vectorizer and SVM classifier
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('svm', SVC(kernel='linear', probability=True)) # probability=True for confidence scores
        ])

        self.model.fit(patterns, tags)

        # Save the trained model
        with open(self.model_path, 'wb') as file:
            pickle.dump(self.model, file)
        print("Model trained and saved successfully.")

    def get_response(self, user_input):
        """
        Predicts the intent of the user input and returns a random response.
        """
        if not self.model:
            return "I'm sorry, my model is not trained yet. Please check the knowledge base and try again."

        processed_input = " ".join(self._preprocess_text(user_input))
        
        # Predict the intent and get probabilities
        probabilities = self.model.predict_proba([processed_input])[0]
        max_prob_index = probabilities.argmax()
        predicted_tag = self.model.classes_[max_prob_index]
        confidence = probabilities[max_prob_index]

        # Set a confidence threshold
        confidence_threshold = 0.70 # Adjust as needed

        if confidence < confidence_threshold:
            return "I'm not sure I understand. Could you please rephrase your question or ask something else?"

        for intent in self.intents:
            if intent['tag'] == predicted_tag:
                return random.choice(intent['responses'])
        
        # Fallback if for some reason the predicted tag isn't found (shouldn't happen if model is trained well)
        return "I'm having trouble understanding that. Could you please provide more details?"

# Example Usage (for testing the core chatbot)
if __name__ == "__main__":
    chatbot = Chatbot()
    print("Chatbot ready! Type 'quit' to exit.")
    while True:
        user_message = input("You: ")
        if user_message.lower() == 'quit':
            break
        response = chatbot.get_response(user_message)
        print(f"Bot: {response}")
        import openai

openai.api_key = 'YOUR_API_KEY'

def get_ai_response(user_message):
    system_prompt = """
    You are 'Erode Sengunthar College Bot', a helpful AI assistant for the Erode Sengunthar Engineering College. 
    Your goal is to assist users with their questions about the college. 
    Be friendly and professional. Only answer questions related to courses, fees, placements, campus life, and admission procedures. 
    If asked about something unrelated, politely state that you can only answer questions about the college.
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content