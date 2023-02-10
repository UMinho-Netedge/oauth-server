#! python3
import http
import json
import ssl
import sys
import time
from flask import (Flask, make_response, render_template, redirect, request,url_for)
import requests
#import oauthlib
from oauthlib.oauth2 import WebApplicationClient
import jwcrypto.jwk
import jwcrypto.jwt



# read the client id and client secret from credentials.json
with open('credentials.json') as f:
    data = json.load(f)
    client_id = data['client_id']
    client_secret = data['client_secret']

print("client_id: ", client_id)
print("client_secret: ", client_secret)

redirect_uri = "http://localhost:5000/callback"
discovery_url = "https://accounts.google.com/.well-known/openid-configuration"

#client = WebApplicationClient(client_id)
oidc_config = requests.get(discovery_url).json()

# Get the ID Token JWT signing keys
# This works because the jwks_url returns an RFC 7517 JWK set, which jwcrypto
# can import directly.
jwks_url = oidc_config['jwks_uri']
id_token_keys = jwcrypto.jwk.JWKSet.from_json(
    requests.get(jwks_url).text
)

# flask server
app = Flask(__name__)

# endpoint to get the login page
@app.route('/login')
def login():

    # here it ip address of the client is saved so that it can be used to reply to the client.
    # not being used at the moment
    client_ip = request.remote_addr
    print("client_ip: ", client_ip)

    
    #req = requests.get("https://accounts.google.com/o/oauth2/v2/auth", params = {
    #    'client_id': client_id,
    #    'response_type': 'code',
    #    'scope': 'openid email',
    #    'redirect_uri': 'http://localhost:5000/callback'})
    ## redirect to google login page
    url = "https://accounts.google.com/o/oauth2/v2/auth?client_id=" + client_id + "&response_type=code&scope=openid%20email&access_type=offline&redirect_uri=http://localhost:5000/callback"
    print(url)
    return redirect(url)

# callback endpoint, to get the access token and id token
@app.route('/callback', methods = ['GET'])
def callback():
    ## get the code from the url
    code = request.args.get('code')

    print("CODE: ", code)

    # make a POST request to get the access token and id token
    conn = http.client.HTTPSConnection("oauth2.googleapis.com", context=ssl._create_unverified_context())
    payload = f'code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code'
    headers = { 'content-type': "application/x-www-form-urlencoded" }
    conn.request("POST", "/token", payload, headers)

    res = conn.getresponse()
    data = json.loads(res.read())

    print("RESPONSE: ", data)
    # get the access token
    access_token = data['access_token']
    # get the id token
    id_token = data['id_token']
    # get the refresh token
    refresh_token = data['refresh_token']

    # Close the connection
    conn.close()

    # aqui tenho que enviar para o cliente o id token e o access token
    return data


# endpoint to get new access token with refresh token
@app.route('/refresh', methods = ['POST'])
def refresh():
    # get the refresh token from request body (json)
    refresh_token = request.json['refresh_token']

    
    print("REFRESH TOKEN: ", refresh_token)

    # make a POST request to get the access token and id token
    conn = http.client.HTTPSConnection("oauth2.googleapis.com", context=ssl._create_unverified_context())
    payload = f'client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token&access_type=offline'
    headers = { 'content-type': "application/x-www-form-urlencoded" }
    conn.request("POST", "/token", payload, headers)

    res = conn.getresponse()
    data = json.loads(res.read())

    print("RESPONSE: ", data)


    return data

# endpoint to validate the id token
@app.route('/validate', methods = ['POST'])
def validate():

    validation = True

    # get the id token from request body (json)
    id_token = request.json['id_token']

    # Decode and display the ID Tokens
    # This works because the ID Token is a JWT, which jwcrypto can decode and verify directly.
    ## catch exception if the token is invalid or expired
    try:
        jwt = jwcrypto.jwt.JWT(jwt=id_token, key=id_token_keys, algs=oidc_config['id_token_signing_alg_values_supported'])
        jwt_claims = json.loads(jwt.claims)
    except:
        #validation = False
        return  "Token INVALID or EXPIRED"

    print("\nJWT: ", jwt_claims)
    jwt_formatted = json.dumps(jwt_claims, indent=4)
    print('')
    print(f"ID Token:")
    print(jwt_formatted)

    # validation (era bom por isto de outra maneira)

    # 1. AUD - The audience of the token. This should be equal to the client_id.
    if jwt_claims['aud'] != client_id:
        validation = False
    
    # 2. ISS - The issuer of the token. This should be equal to https://accounts.google.com or accounts.google.com.
    if jwt_claims['iss'] != "https://accounts.google.com" and jwt_claims['iss'] != "accounts.google.com":
        validation = False
    
    # 3. EXP - The expiration time of the token. This should be after the current time.
    if jwt_claims['exp'] < time.time():
        validation = False

    # 4. IAT - The time the token was issued. This should be before the current time.
    if jwt_claims['iat'] > time.time():
        validation = False
    
    if validation:
        return "Token VALID"
    else:
        return  "Token INVALID"


app.run(host='0.0.0.0', port = 5000, debug = True)

