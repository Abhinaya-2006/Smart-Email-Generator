import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# --- Configure the Gemini API ---
GEMINI_API_KEY = "YOUR_API_KEY"  # <-- Paste your key here

app = Flask(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    model = None
    print("WARNING: API key not configured. The application will not generate real emails.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_email', methods=['POST'])
def generate_email():
    if not model:
        return jsonify({
            'error': 'API key is not configured.'
        }), 503

    data = request.json
    tone = data.get('tone')
    
    try:
        if tone == 'Formal':
            recipient = data.get('recipient_name')
            sender = data.get('sender_name')
            topic = data.get('body_topic')

            prompt = f"Write a professional and formal email from '{sender}' to '{recipient}' based on the following topic. Include a clear subject line and then the email body:\n\nTopic: {topic}"

        elif tone == 'Informal':
            recipient = data.get('recipient_name')
            topic = data.get('body_topic')

            prompt = f"Write a friendly and informal email to '{recipient}' based on the following topic. Include a clear subject line and then the email body:\n\nTopic: {topic}"
        else:
            return jsonify({'error': 'Invalid tone specified.'}), 400
        
        response = model.generate_content(prompt)
        generated_text = response.text

        # Assuming the AI response starts with "Subject:"
        if 'Subject:' in generated_text:
            parts = generated_text.split('Subject:', 1)
            subject_and_body = parts[1].strip().split('\n\n', 1)
            subject = subject_and_body[0].strip()
            body = subject_and_body[1].strip()
        else:
            # Fallback if AI doesn't include a subject line
            subject = "Generated Email"
            body = generated_text

        return jsonify({'subject': subject, 'email': body})

    except Exception as e:
        return jsonify({
            'error': f"Error generating email: {e}"
        }), 500


@app.route('/generate_reply', methods=['POST'])
def generate_reply():
    if not model:
        return jsonify({
            'reply': 'Error: API key is not configured. Please add your GEMINI_API_KEY to the app.py file.'
        }), 503

    data = request.json
    email_text = data.get('email_text')
    tone = data.get('tone')

    if tone == 'None':
        prompt = f"Act as a person who has received the following email. Write a concise and direct reply. Here is the email to reply to:\n\n{email_text}"
    else:
        prompt = f"Act as a person who has received the following email. Write a concise reply with a {tone} tone. Here is the email to reply to:\n\n{email_text}"

    try:
        response = model.generate_content(prompt)
        generated_reply = response.text
    except Exception as e:
        generated_reply = f"Error generating reply: {e}"
        print(f"API Error: {e}")
    
    return jsonify({'reply': generated_reply})

if __name__ == '__main__':
    app.run(debug=True)