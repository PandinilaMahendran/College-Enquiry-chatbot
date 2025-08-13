from flask import Flask, request, jsonify, render_template
import datetime
import os

app = Flask(__name__)

# This is a very simple way to store feedback (NOT for production, use a database like SQLite or Firestore)
FEEDBACK_FILE = 'feedback.txt'

@app.route('/')
def index():
    # A simple HTML form would be rendered here.
    # For now, just a placeholder message.
    return "<h1>College Chatbot Feedback System</h1><p>Send feedback via /submit_feedback API endpoint.</p>"

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    """
    Receives feedback via POST request and saves it to a text file.
    In a real application, you'd save to a database.
    """
    if request.is_json:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message', '')
        rating = data.get('rating', None) # Optional: e.g., 1-5 stars

        if not message:
            return jsonify({"status": "error", "message": "Feedback message cannot be empty."}), 400

        timestamp = datetime.datetime.now().isoformat()
        feedback_entry = f"[{timestamp}] User ID: {user_id}, Rating: {rating}, Message: {message}\n"

        try:
            with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
                f.write(feedback_entry)
            return jsonify({"status": "success", "message": "Feedback submitted successfully!"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to save feedback: {str(e)}"}), 500
    else:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

@app.route('/view_feedback')
def view_feedback():
    """
    Displays collected feedback (for internal use, not for public access).
    """
    if not os.path.exists(FEEDBACK_FILE):
        return "No feedback collected yet."
    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
        feedback_data = f.read()
    return f"<pre>{feedback_data}</pre>"


if __name__ == '__main__':
    # To run this Flask app:
    # 1. Save as feedback_app.py
    # 2. In terminal (with venv active): python feedback_app.py
    # 3. Access at http://127.0.0.1:5000/
    # You'd send POST requests to http://127.0.0.1:5000/submit_feedback
    app.run(debug=True) # debug=True is for development, set to False for production
