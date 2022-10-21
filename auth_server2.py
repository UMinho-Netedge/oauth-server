#! python3

import base64
import json
import time
from urllib.parse import urlencode, urlparse
import requests
import urllib.parse as urlparse
import jwt
from cryptography.fernet import Fernet
from flask import (Flask, make_response, render_template, redirect, request,
                   url_for)

app = Flask(__name__)

registered_clients = {'client-id': 'serviços de ediçao de fotos'}
client_secrets = {'client-id': 'client-secret'}
registered_users = {'rafa': '123', 'user2': 'password2'}
authorization_codes = {}

SECRET_KEY = 'secret-key-of-the-portuguese-empire'

#with open('private.pem', mode='rb') as privatefile:
#    private_key = privatefile.read()
    
#with open('public .pem', mode='rb') as publicfile:
#    public_key = publicfile.read()

@app.route('/auth')
def auth():

    redirect_url = request.args.get('redirect_url')  

    # 1. Check if the client is registered
    client_id = request.args.get('client_id')
    if client_id not in registered_clients:
        return make_response('Client not registered', 401)
    
    # 2. Check if the client is authorized
    if client_id not in client_secrets:
        return make_response('Client not authorized', 401)
    
    return render_template('login.html', client_id=registered_clients[client_id], redirect_url = redirect_url)


@app.route('/signin', methods = ['POST'])
def signin():

    username = request.form.get('username')
    password = request.form.get('password')
    client_id = request.form.get('client_id')
    redirect_url = request.form.get('redirect_url')

    if None in [ username, password, client_id, redirect_url ]:
        return json.dumps({
            "error": "invalid_request"
        }), 400

    # 3. Check if the user is registered
    if username not in registered_users:
        return make_response('User not registered', 401)
    
    # 4. Check if the password is correct
    if password != registered_users[username]:
        return make_response('Invalid password', 401)

    authorization_code = generate_authorization_code(client_id, redirect_url)

    #return authorization_code to the redirect_url
    url = process_redirect_url(redirect_url, authorization_code)
    return redirect(url)



@app.route('/token', methods = ['POST'])
def token():
    # 1. Check if the client is registered
    client_id = request.form.get('client_id')
    if client_id not in registered_clients:
        return make_response('Client not registered', 401)
    
    # 2. Check if the client is authorized
    if client_id not in client_secrets:
        return make_response('Client not authorized', 402)
    
    # 3. Check if the client secret is correct
    client_secret = request.form.get('client_secret')
    if client_secret != client_secrets[client_id]:
        return make_response('Invalid client secret', 403)
    
    # 4. Check if the authorization code is correct
    authorization_code = request.form.get('code')
    if authorization_code is None:
        return make_response('Invalid authorization code', 404)
    
    # 5. Generate the access token
    access_token = jwt.encode({'client_id': client_id, 'exp': time.time() + 3600}, SECRET_KEY, algorithm = 'HS256')
    
    # 6. Generate the refresh token
    refresh_token = jwt.encode({'client_id': client_id}, client_secret, algorithm = 'HS256')
    
    return json.dumps({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 3600
    })

  
# endpoint to validate access tokens sent by the client to the resource server
@app.route('/validate_token', methods = ['POST'])
def validate():
    access_token = request.form.get('access_token')
    try:
        jwt.decode(access_token, SECRET_KEY, algorithms = ['HS256'])
    except:
        return make_response('Invalid access token', 401)
    return make_response('Valid access token', 200)
    

def generate_authorization_code(client_id, redirect_url):
  #f = Fernet(KEY)
  f = Fernet(Fernet.generate_key())
  authorization_code = f.encrypt(json.dumps({
    "client_id": client_id,
    "redirect_url": redirect_url,
  }).encode())

  authorization_code = base64.b64encode(authorization_code, b'-_').decode().replace('=', '')

  expiration_date = time.time() + 3600

  authorization_codes[authorization_code] = {
    "client_id": client_id,
    "redirect_url": redirect_url,
    "exp": expiration_date
  }
  return authorization_code

def verify_authorization_code(authorization_code, client_id, redirect_url):
  #f = Fernet(KEY)
  record = authorization_codes.get(authorization_code)
  if not record:
    return False

  client_id_in_record = record.get('client_id')
  redirect_url_in_record = record.get('redirect_url')
  exp = record.get('exp')

  if client_id != client_id_in_record or \
     redirect_url != redirect_url_in_record:
    return False

  if exp < time.time():
    return False

  del authorization_codes[authorization_code]

  return True

def process_redirect_url(redirect_url, authorization_code):
  # Prepare the redirect URL
  url_parts = list(urlparse.urlparse(redirect_url))
  queries = dict(urlparse.parse_qsl(url_parts[4]))
  queries.update({ "authorization_code": authorization_code })
  url_parts[4] = urlencode(queries)
  url = urlparse.urlunparse(url_parts)
  return url

app.run(host='0.0.0.0', port = 5001, debug = True)