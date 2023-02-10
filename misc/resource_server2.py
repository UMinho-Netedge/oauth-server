#! python3

import json
import requests
import jwt
from flask import (Flask, make_response, render_template, redirect, request,
                   url_for)

app = Flask(__name__)

with open('public.pem', mode='rb') as publicfile:
    public_key = publicfile.read()

clients_app_1 = [{
  "first_name": "Pavlov",
  "last_name": "Blinerman",
  "email": "pblinerman0@marketwatch.com",
  "ip_address": "66.231.212.151"
}, {
  "first_name": "Demeter",
  "last_name": "Winspare",
  "email": "dwinspare1@w3.org",
  "ip_address": "134.166.3.66"
}, {
  "first_name": "Alessandra",
  "last_name": "Le land",
  "email": "aleland2@networkadvertising.org",
  "ip_address": "217.167.143.69"
}]

clients_app_2 = [{"first_name": "Ebba",
  "last_name": "Ranald",
  "email": "eranald3@cafepress.com",
  "ip_address": "71.122.237.68"
}, {
  "first_name": "Hedwiga",
  "last_name": "Maynard",
  "email": "hmaynard4@cnbc.com",
  "ip_address": "146.56.169.2"
}, {
  "first_name": "Alta",
  "last_name": "Mattaser",
  "email": "amattaser5@hibu.com",
  "ip_address": "116.119.245.242"
}]

@app.route('/recurso1')
def recurso1():
    token = request.headers.get('Authorization')
    print("token: ", token)
    if validate_token(token):
        return json.dumps(clients_app_1)
    else:
        return make_response('Token inválido', 401)

@app.route('/recurso2')
def recurso2():
    token = request.args.get('token')
    if validate_token(token):
        return json.dumps(clients_app_2)
    else:
        return make_response('Token inválido', 402)

@app.route('/recurso3')
def recurso3():
    return make_response('Recurso Indisponivel', 403)

@app.route('/recurso4')
def recurso4():
    return make_response('Recurso Indisponivel', 404)


#validates access token sent from client, and to do that, it sends the token to the authorization server
def validate_token(token):

    url = 'http://localhost:5001/validate_token'
    response = requests.post(url, data={'access_token': token})
    if response.status_code == 200:
        return True
    else:
        return False



app.run(port = 5002, debug = True)