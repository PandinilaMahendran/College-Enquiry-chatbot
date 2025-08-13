import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_query_email(user_name, user_email, query_message, recipient_email="college_support@example.com"):
    """
    Sends an email notification for a user query.
    You need to configure your email server details.
    """
    sender_email = "your_chatbot_email@example.com" # Your chatbot's email address
    sender_password = "your_email_password" # Your chatbot's email password (use environment variables for security!)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"New Chatbot Query from {user_name}"

    body = f"""
    A new query has been submitted via the college chatbot:

    User Name: {user_name}
    User Email: {user_email}
    Query: {query_message}

    Please respond to the user as soon as possible.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        # For Gmail, use 'smtp.gmail.com' and port 587 with TLS
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Enable TLS encryption
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Query email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send query email: {e}")
        print("Please ensure 'Less secure app access' is enabled for your Gmail account if using Gmail, or use app-specific passwords.")
        return False

# Integration with Chatbot:
"""
if predicted_tag == "query_ticket":
    speak_response("I can help you raise a query ticket. What is your full name?")
    user_name = listen_to_user()
    speak_response("What is your email address?")
    user_email = listen_to_user()
    speak_response("Please describe your query in detail.")
    query_description = listen_to_user()

    if send_query_email(user_name, user_email, query_description, "your_college_staff_email@erode-sengunthar.ac.in"):
        speak_response("Your query has been submitted to our support team. They will contact you shortly at " + user_email)
    else:
        speak_response("I apologize, but I was unable to submit your query at this time. Please try again later or contact the college directly.")
"""
