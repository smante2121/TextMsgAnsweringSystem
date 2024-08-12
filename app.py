import os
import re
import telnyx
from flask import Flask, request, Response

# this implementation uses Telnyx Call Control API to handle inbound calls and their messaging API to send SMS messages

app = Flask(__name__)

telnyx.api_key = os.getenv("TELNYX_API_KEY")  # Initialize Telnyx client with the API key
PHONE_NUMBER_REGEX = re.compile(r"^\d{10}$")  # Regular expression to validate a 10-digit phone number


speak_tracker = {} # Dictionary to track the type of message played for each call_control_id

@app.route('/handle_call', methods=['POST'])
def handle_call():
    data = request.json
    event_type = data['data']['event_type']
    payload = data['data'].get('payload', {})
    call_control_id = payload.get('call_control_id')

    if not call_control_id:
        handle_messaging_event(data)
        return Response(status=200)

    if event_type == 'call.initiated':
        handle_call_initiated(call_control_id)

    elif event_type == 'call.answered':
        handle_call_answered(call_control_id)

    elif event_type == 'call.gather.ended':
        handle_gather_ended(call_control_id, payload)

    elif event_type == 'call.speak.ended':
        handle_speak_ended(call_control_id)

    return Response(status=200)

def handle_call_initiated(call_control_id):
    print("Event: Call initiated.")
    telnyx.Call.retrieve(call_control_id).answer()

def handle_call_answered(call_control_id):
    print("Event: Call answered.")
    call = telnyx.Call.retrieve(call_control_id)
    call.speak(
        payload='Please enter your 10-digit callback number followed by the pound sign.',
        language='en-US',
        voice='female'
    )
    call.gather(
        minimum_digits=10,
        maximum_digits=10,
        timeout_millis=60000,
        terminating_digit="#",
        valid_digits="0123456789#"
    )

def handle_gather_ended(call_control_id, payload):
    digits = payload.get('digits')
    print(f"Event: Gather ended. Digits received: {digits}")
    call = telnyx.Call.retrieve(call_control_id)

    if digits and PHONE_NUMBER_REGEX.match(digits):
        print("Event: Validating number.")
        send_confirmation_message(call, digits, call_control_id)
    else:
        print("Event: Invalid number entered.")
        play_invalid_number_message(call, call_control_id)

def handle_speak_ended(call_control_id):
    last_message = speak_tracker.get(call_control_id)
    call = telnyx.Call.retrieve(call_control_id)

    if last_message == 'confirmation':
        print("Event: Confirmation message ended, hanging up now.")
        call.hangup()
        speak_tracker.pop(call_control_id, None)
    elif last_message == 'invalid_number':
        print("Event: Invalid number prompt ended, waiting for user input.")

def send_confirmation_message(call, digits, call_control_id):
    telnyx.Message.create(
        from_=os.getenv('TELNYX_NUMBER'),
        to=f"+1{digits}",
        text=f"We received your callback number: {digits}. We will contact you shortly."
    )
    call.speak(
        payload='Thank you! We have received your callback number and will reach out soon.',
        language='en-US',
        voice='female'
    )
    speak_tracker[call_control_id] = 'confirmation'

def play_invalid_number_message(call, call_control_id):
    call.speak(
        payload='The number you entered is invalid. Please try again.',
        language='en-US',
        voice='female'
    )
    speak_tracker[call_control_id] = 'invalid_number'

def handle_messaging_event(data):
    event_type = data['data']['event_type']
    print("Handling messaging event.")
    if event_type == 'message.sent':
        print("Event: Message sent successfully.")
    elif event_type == 'message.finalized':
        print("Event: Message finalized.")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
