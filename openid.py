#! python3
import http
import json
import ssl
import sys
from flask import (Flask, make_response, render_template, redirect, request,url_for)
import requests
import oauthlib
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

# flask server on port 6000
app = Flask(__name__)


@app.route('/login')
def login():

    #req = requests.get("https://accounts.google.com/o/oauth2/v2/auth", params = {
    #    'client_id': client_id,
    #    'response_type': 'code',
    #    'scope': 'openid email',
    #    'redirect_uri': 'http://localhost:5000/callback'})
    ## redirect to google login page
    url = "https://accounts.google.com/o/oauth2/v2/auth?client_id=" + client_id + "&response_type=code&scope=openid%20email&redirect_uri=http://localhost:5000/callback"
    print(url)
    return redirect(url)

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

    # Close the connection
    conn.close()

    # Decode and display the ID Tokens
    # This works because the ID Token is a JWT, which jwcrypto can decode and verify directly.
    jwt = jwcrypto.jwt.JWT(jwt=id_token, key=id_token_keys, algs=oidc_config['id_token_signing_alg_values_supported'])
    jwt_claims = json.loads(jwt.claims)

    print("\nJWT: ", jwt_claims)

    jwt_formatted = json.dumps(jwt_claims, indent=4)
    print('')
    print(f"ID Token:")
    print(jwt_formatted)


    return jwt_formatted




app.run(host='0.0.0.0', port = 5000, debug = True)

