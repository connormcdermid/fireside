from dotenv import load_dotenv
import os
from os.path import join, dirname
from flask import Flask, request, redirect, make_response
from twilio.twiml.messaging_response import MessagingResponse
import json
import pymysql
from flask_cors import CORS, cross_origin

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
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'

conn = pymysql.connect(
    db="conversations",
    user="apache",
    passwd="campguy",
    host="localhost"
)
c = conn.cursor()


@app.route("/sms", methods=['GET', 'POST'])
@cross_origin()
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()
    args = request.args
    form = request.form
    values = request.values
    print(args)
    print(form)
    print(values)

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
@cross_origin()
def reg_reply():
    jsonraw = json.dumps(request.json)
    jsonData = json.loads(jsonraw)
    alias = jsonData["user_alias"]
    phone = jsonData["user_number"]
    print(alias)
    print(phone)
    if c.execute(f"SELECT * FROM conversations.test_users WHERE number={phone}") != 0:
        response = make_response("user_exists", 200)
        response.mimetype = "text/plain"
        response.headers.add('Access-Control-Allow-Origin', 'http://sms.firesidechat.tech')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    c.execute(f"INSERT INTO conversations.test_users VALUES ('{alias}', '{phone}')")
    conn.commit()
    response = make_response("success", 200)
    response.mimetype = "text/plain"
    response.headers.add('Access-Control-Allow-Origin', 'http://sms.firesidechat.tech')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
