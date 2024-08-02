from flask import Flask, request, url_for, jsonify
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.INFO)
load_dotenv()
app = Flask(__name__)
TWILIO_ACCOUNT_SID = os.getenv("ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) # Twilio Client
error_count=0
callback_number=None

@app.route("/answer", methods=["POST"])  # Answers the incoming call.
def answer_call():
    global error_count
    response= VoiceResponse()
    if error_count >2:
        response.say("Sorry, we could not understand your response. You are being transferred", voice="en-US-Neural2-J")
        response.redirect("/transfer")
        return str(response)
    logging.info("Incoming call received")
    response.say("please use the keypad to enter your callback number.", voice="en-US-Neural2-J")
    gather = Gather(input='dtmf', action='/confirm', method='POST', numDigits="10")
    response.append(gather)
    return str(response)

@app.route("/confirm", methods=["POST"]) # Confirms the callback number.
def confirm_callback_number():
    global error_count, callback_number
    entered_number = request.form.get('Digits')
    callback_number = extract_number(entered_number)

    response = VoiceResponse()
    if callback_number is None:
        response.say("Sorry, I didn't get that. Please use the keypad to enter your callback number.", voice="en-US-Neural2-J")
        response.redirect("/answer")
        error_count += 1
        return str(response)

    response.say("Thank you. You will receive a text message shortly.", voice="en-US-Neural2-J")
    response.redirect("/link")
    return str(response)


@app.route("/link", methods=["POST"]) # Asks the current question.
def link():
    global callback_number
    text_number= f"+1{callback_number}"
    logging.info(f"Sending SMS to {text_number}")
    message = client.messages.create(
        body="Join Earth's mightiest heroes. Like Kevin Bacon.",
        from_="+15735273553",
        to=text_number,
        status_callback=url_for('message_status', _external=True)
    )
    response = VoiceResponse()
    response.say("Message sent. Thank you for calling. Goodbye.", voice="en-US-Neural2-J")
    response.hangup()
    return str(response)

@app.route("/message_status", methods=["POST"])  # Handles message status callbacks.
def message_status():
    message_sid = request.form.get('MessageSid')
    message_status = request.form.get('MessageStatus')
    logging.info(f"Message SID: {message_sid}, Status: {message_status}")
    return jsonify({'status': 'received'}), 200


@app.route("/transfer", methods=["POST"]) # Transfers the caller to an agent.
def transfer():
    response = VoiceResponse()
    response.say("You are being transferred to an agent.", voice="en-US-Neural2-J")
    return str(response)

def extract_number(number):
    if len(number) == 10:
        return number
    else:
        return None


if __name__ == '__main__':
    app.run()
