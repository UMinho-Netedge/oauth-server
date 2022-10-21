#! python3

import json
import requests
import jwt
from flask import (Flask, make_response, render_template, redirect, request,
                   url_for)

AUTH_PATH = 'http://localhost:5001/auth'
TOKEN_PATH = 'http://localhost:5001/token'
RES_PATH = 'http://localhost:5002/recurso'
REDIRECT_URL = 'http://localhost:5000/callback'

CLIENT_ID = 'client-id'
CLIENT_SECRET = 'client-secret'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('client_home.html', dest = AUTH_PATH, client_id = CLIENT_ID, redirect_url = REDIRECT_URL)

@app.route('/callback')
def callback():
    # Accepts the authorization code and exchanges it for access token
    authorization_code = request.args.get('authorization_code')
    
    print(authorization_code)

    #if not authorization_code:
    #    return json.dumps({
    #        'error': 'invalid_request'
    #    }), 400
    
    r = requests.post(TOKEN_PATH, data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_url': REDIRECT_URL
    })

    if r.status_code != 200:
        return json.dumps({
            'error': 'invalid_request'
        }), 400
    
    access_token = json.loads(r.text).get('access_token')

    return render_template('resource_request.html', token = access_token)


@app.route('/recurso')
def recurso():
    # Accepts the access token and makes a request to the resource server
    tipo_recurso = request.args.get('tipo')
    access_token = request.args.get('access_token')
    print("access_token: ", access_token)
    print("tipo_recurso: ", tipo_recurso)
    r = requests.get(RES_PATH + tipo_recurso, headers = {
        'Authorization': format(access_token)
    })
    print("path: ", RES_PATH + tipo_recurso)
    if r.status_code != 200:
        return json.dumps({
            'error': 'invalid_request'
        }), 400

    return r.text


app.run(port = 5000, debug = True)