# Telnyx Text Response

## Overview
Welcome to the Telnyx Text Response repository. This project is a Python Flask application that leverages Telnyx's API to handle inbound calls, gather caller information, and send SMS messages. The application is designed to automate the process of collecting a callback number from a caller and sending a confirmation message to that number.

### Features
- **Call Handling:** Uses Telnyx Call Control API to answer incoming calls and interact with the caller.
- **Callback Number Collection:** Prompts the caller to enter their 10-digit callback number via DTMF input.
- **Phone Number Validation:** Validates the entered callback number to ensure it is a valid 10-digit US number.
- **SMS Confirmation:** Sends a confirmation SMS to the validated callback number using Telnyx's Messaging API.
- **Call Termination:** Automatically hangs up the call after sending the confirmation message.
- **Error Handling:** If an invalid number is entered, the caller is prompted to try again.

### How It Works
- **Ngrok Webhooks:** The application currently runs locally using ngrok to expose the `/handle_call` endpoint to Telnyx.
- **Webhook Configuration:** The webhook URL must be configured in Telnyx and linked to the phone number profile to handle messaging and voice responses.

### Improvements and Further Development
- **Confirm Number Before SMS:** Add logic to confirm the callback number before sending the SMS.
- **Database Integration:** Record the caller ID upon answering the call and integrate with a database.
- **Deployment:** Plan to deploy the application using Google Cloud Run for better scalability and accessibility.

### Use Cases
- **Automated Messaging:** Ideal for scenarios where a message containing a link or further instructions needs to be sent to the caller after a phone interaction.

## Project Structure
- **app.py:** The main application file that handles incoming calls, gathers DTMF input, validates the number, and sends SMS messages.
- **TwilioImplementation:** Functions the exact same as app.py but uses Twilio's apis for answering, speaking, gathering, and messaging.
