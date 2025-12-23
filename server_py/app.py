from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

load_dotenv()

app = Flask(__name__)
CORS(app)

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USER)
RECIPIENT = os.getenv('CONTACT_RECIPIENT', 'spbluecorp@gmail.com')
PORT = int(os.getenv('PORT', 3000))
TEST_MODE = os.getenv('TEST_MODE', '').lower() == 'true'

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject', 'Website inquiry')
    message = data.get('message')
    if not name or not email or not message:
        return jsonify({'error': 'Missing required fields: name, email, message'}), 400

    body = f"Name: {name}\nEmail: {email}\n\n{message}"

    msg = EmailMessage()
    msg['Subject'] = f"[Website Contact] {subject}"
    msg['From'] = FROM_EMAIL or SMTP_USER
    msg['To'] = RECIPIENT
    msg['Reply-To'] = email
    msg.set_content(body)

    try:
        if TEST_MODE:
            app.logger.info('TEST_MODE enabled — email not sent. Message: %s', body)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        return jsonify({'ok': True})
    except Exception as e:
        app.logger.exception('Failed to send contact email')
        return jsonify({'error': 'Failed to send message'}), 500

if __name__ == '__main__':
    if TEST_MODE:
        app.logger.info('Starting in TEST_MODE — emails will be logged, not sent')
    else:
        if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
            app.logger.warning('SMTP not fully configured; see server_py/.env.example')
    app.run(host='0.0.0.0', port=PORT)
