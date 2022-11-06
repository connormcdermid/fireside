from dotenv import load_dotenv
import os
from os.path import join, dirname
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TWILIO_AUTH_KEY = os.environ.get("TWILIO_AUTH_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_NUMBER = "+17014909781"

from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = TWILIO_SID
auth_token = TWILIO_AUTH_KEY
client = Client(account_sid, auth_token)

# message = client.messages \
#     .create(
#     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
#     from_=TWILIO_NUMBER,
#     to='+18622285361'
# )

# print(message.sid)

app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")
    client.messages \
        .create(
        body="Message received successfully.",
        from_=TWILIO_NUMBER,
        to='+18622285361'
    )
    print(str(resp))
    return str(resp)


@app.route("/reg", methods=['POST'])
def reg_reply():
    jsonraw = json.dumps(request.json)
    jsonData = json.load(jsonraw)
    alias = jsonData["alias"]
    phone = jsonData["number"]
    print(alias)
    print(phone)
    return "Data received."


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
