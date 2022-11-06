import re

from dotenv import load_dotenv
import os
from os.path import join, dirname
from flask import Flask, request, redirect, make_response
from twilio.twiml.messaging_response import MessagingResponse
import json
import pymysql
from flask_cors import CORS, cross_origin
import socket
from OpenSSL import SSL
from twilio.request_validator import RequestValidator

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TWILIO_AUTH_KEY = os.environ.get("TWILIO_AUTH_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_NUMBER = "+19785811148"

from twilio.rest import Client
validator = RequestValidator(TWILIO_AUTH_KEY)

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

# Create SSL context to bind the Flask app to
#context = SSL.Context(SSL.TLSv1_2_METHOD)
#context.use_privatekey_file('/etc/letsencrypt/live/sms.firesidechat.tech/privkey.pem')
#context.use_certificate_chain_file('/etc/letsencrypt/live/sms.firesidechat.tech/fullchain.pem')
#context.use_certificate_file('/etc/letsencrypt/live/sms.firesidechat.tech/cert.pem')

#socket_instance = socket.socket()

#ssl_socket_instance = context.wrap_socket(socket_instance)

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


    # Start our TwiML response
    resp = MessagingResponse()
    form = request.form
    source = form.get('From')
    print(source)
    body = form.get('Body')
    print(body)

    if "STOP" in body:
        c.execute(f"DELETE FROM conversations.associations WHERE registered_number='{source}'")
        conn.commit()
    c.execute(f"SELECT unregistered_number FROM conversations.associations WHERE registered_number='{source}'")
    result1 = c.fetchone()
    c.execute(f"SELECT registered_number FROM conversations.associations WHERE unregistered_number='{source}'")
    result2 = c.fetchone()
    print("result1:", result1)
    print("result2:", result2)
    target = None
    if result1 is not None or result2 is not None:
        if result1 is not None:
            target = str(result1[0])
        else:
            target = str(result2[0])
        client.messages.create(body=body, from_=TWILIO_NUMBER, to=target)
        return "success"

    alias = body.split(",")[0].lower()
    c.execute(f"SELECT number FROM conversations.test_users WHERE alias='{alias}'")
    result = c.fetchone()
    if "+" not in source:
        source = "+" + source
    while result:
        target = str(result[0])
        if re.match("^([+])[\d]{11}$", target):
            client.messages \
            .create(
                body=re.split("^(\w+),", body)[0],
                from_=TWILIO_NUMBER,
                to=target
            )
            c.execute(f"INSERT INTO conversations.associations(registered_alias, registered_number, unregistered_number) VALUES ('{alias}', '{target}', '{source}')")
            conn.commit()
            return "success";


    # Add a message
    resp.message("Invalid alias, please try again!")
    client.messages.create(body="Invalid alias!", from_=TWILIO_NUMBER, to=source)
    print(str(resp))
    return str(resp)


@app.route("/reg", methods=['POST'])
@cross_origin()
def reg_reply():
    contentype = request.content_type;
    print(contentype)
    form = request.form
    alias = form.get("user_alias")
    phone = form.get("user_number")

    print(alias)
    print(phone)
    if c.execute(f"SELECT * FROM conversations.test_users WHERE alias='{alias}'") != 0:
        response = make_response("user_exists", 200)
        response.mimetype = "text/plain"
#        response.headers.add('Access-Control-Allow-Origin', 'https://sms.firesidechat.tech/reg')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    c.execute(f"INSERT INTO conversations.test_users VALUES ('{alias}','{phone}')")
    conn.commit()
    response = make_response("success", 200)
    response.mimetype = "text/plain"
#    response.headers.add('Access-Control-Allow-Origin', 'https://sms.firesidechat.tech/reg')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0", ssl_context=('/etc/letsencrypt/live/sms.firesidechat.tech/cert.pem', '/etc/letsencrypt/live/sms.firesidechat.tech/privkey.pem'))
#   app.run(debug=True, port=8000, host="0.0.0.0", ssl_context=ssl_socket_instance)
