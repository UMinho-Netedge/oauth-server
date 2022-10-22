#! python3

import base64
import json
import time
from urllib.parse import urlencode, urlparse
#from winsound import Beep
import requests
import urllib.parse as urlparse
import jwt
from cryptography.fernet import Fernet
from flask import (Flask, make_response, render_template, redirect, request,url_for)
import secrets


app = Flask(__name__)

#registered_clients = {'client-id': 'serviços de ediçao de fotos'}
with open('reg_clients.json') as f:
    registered_clients = json.load(f)
f.close()

print("registered_clients: ", registered_clients)
SECRET_KEY = 'secret-key-of-the-portuguese-empire'

#with open('private.pem', mode='rb') as privatefile:
#    private_key = privatefile.read()
    
#with open('public .pem', mode='rb') as publicfile:
#    public_key = publicfile.read()


@app.route('/token', methods = ['POST'])
def token():
    # 1. Check if the client is registered
    client_id = request.form.get('client_id')
    if client_id not in registered_clients:
        return make_response('Client not registered', 401)
    
    # 3. Check if the client secret is correct
    client_secret = request.form.get('client_secret')
    if client_secret != registered_clients[client_id]:
        return make_response('Invalid client secret', 403)
    
    # 4. Generate the access token
    access_token = jwt.encode({'client_id': client_id, 'exp': time.time() + 3600}, SECRET_KEY, algorithm = 'HS256')

    return json.dumps({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3600
    })

# register new client in authorization server
@app.route('/register', methods = ['GET'])
def register():
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)

    registered_clients[client_id] = client_secret

    with open('reg_clients.json', 'w') as f:
        json.dump(registered_clients, f)
    f.close()

    return json.dumps({
        'client_id': client_id,
        'client_secret': client_secret,
        "message": "Client registered successfully"
    })

# view registred clients
@app.route('/clients', methods = ['GET'])
def clients():
    return json.dumps(registered_clients)

  
# endpoint to validate access tokens sent by the client to the resource server
@app.route('/validate_token', methods = ['POST'])
def validate():
    access_token = request.form.get('access_token')
    try:
        tok = jwt.decode(access_token, SECRET_KEY, algorithms = ['HS256'])
        if tok['exp'] < time.time():
            return json.dumps({
                'message': 'Token expired'
            }), 401
    except:
        return make_response('Invalid access token', 401)
    return make_response('Valid access token', 200)
    

def process_redirect_url(redirect_url, authorization_code):
  # Prepare the redirect URL
  url_parts = list(urlparse.urlparse(redirect_url))
  queries = dict(urlparse.parse_qsl(url_parts[4]))
  queries.update({ "authorization_code": authorization_code })
  url_parts[4] = urlencode(queries)
  url = urlparse.urlunparse(url_parts)
  return url

app.run(host='0.0.0.0', port = 5001, debug = True)