#! python3
import http
import os
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
from pymongo import MongoClient
# flask cors
from flask_cors import CORS



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


mongodb_addr = os.environ.get("ME_CONFIG_MONGODB_SERVER")
mongodb_port = int (os.environ.get("ME_CONFIG_MONGODB_PORT"))
mongodb_username = os.environ.get("ME_CONFIG_MONGODB_ADMINUSERNAME")
mongodb_password = os.environ.get("ME_CONFIG_MONGODB_ADMINPASSWORD")

### Para testes locais
#mongodb_addr = "mongodb://localhost:27017"
#mongodb_port = 27017
#mongodb_username = ""
#mongodb_password = ""



# Auxiliar funcctions

def validation(jwt_claims):
    validation = True   
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
    
    return validation




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

    # return  access token from /callback endpoint in authorization header to the client
    return make_response(req.text, 200, {'Content-Type': 'text/html'})



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

    #print("RESPONSE: ", data)
    # get the access token
    access_token = data['access_token']
    # get the id token
    id_token = data['id_token']
    # get the scope
    scope = data['scope']

    # get the refresh token
    jwt = jwcrypto.jwt.JWT(jwt=id_token, key=id_token_keys, algs=oidc_config['id_token_signing_alg_values_supported'])
    jwt_claims = json.loads(jwt.claims)
    #print("\nJWT: ", jwt_claims)

    token_validation = validation(jwt_claims)
    if token_validation: # se for true, então guarda na BD, assim assegurando que tudo o que é guardado é válido.
        try:
            refresh_token = data['refresh_token']
            
            # get the expiration time from id token
            expiration = jwt_claims['exp']
            print("expiration: ", expiration)
            
            # save data in the database
            add_token_with_refresh(access_token, id_token, refresh_token, scope, expiration) 
        except:
            # if the refresh token is not returned, it means that it was already used (pedido de refresh)
            expiration = jwt_claims['exp']
            add_token(access_token, id_token, scope, expiration)
            conn.close()
            return data
    
    # Close the connection
    conn.close()

    # return token in authorization header
    response = make_response('Google Token received sucessfully!')
    response.headers['Authorization'] =  data
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

    # all data is returned
    # return data


# endpoint to get new access token with refresh token
@app.route('/refresh', methods = ['POST'])
def refresh():

    # get access token from header
    data = request.headers.get('Authorization')
    access_token = data.split(" ")[1]
    print("ACCESS TOKEN: ", access_token)
   
    # get refresh token from database
    refresh_token = get_refresh_token(access_token)
    
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

# endpoint to validate the access token
@app.route('/validate', methods = ['POST'])
def validate():
    data = request.headers.get('Authorization')
    print("DATA: ", data)
    access_token = data.split(" ")[1]
    print("ACCESS TOKEN: ", access_token)
    if validate_token(access_token):
        return "Token is VALID"
    else:
        return "Token is INVALID"



#################### DATABSE CONNECTION AND QUERIES ####################

# Se o servidor for reiniciado, então todos os tokens são apagados da base de dados.
@app.before_first_request
def reset_mongo():
    print("GOING TO RESET MONGO")
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    print("Connected to database successfully!")
    # delete token collection
    #db = client['openid']
    #tokens = db['tokens']
    #tokens.delete_many({})
    
    #client.drop_database('oauth')
    #print("Database dropped successfully!")
    # create the database and collections
    #db = client.oauth
    #db.create_collection('clients')
    #db.create_collection('tokens')
    # close connection
    client.close()

# Função que adiciona tokens a base de dados
def add_token(access_token, id_token, scope, expires):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.insert_one({'access_token': access_token, 'id_token': id_token, 'scope': scope, 'expires': expires})
    print("Token added successfully!")
    client.close()

# Função que adiciona tokens a base de dados
def add_token_with_refresh(access_token, id_token, refresh_token, scope, expires):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.insert_one({'access_token': access_token, 'id_token': id_token, "refresh_token": refresh_token, 'scope': scope, 'expires': expires})
    print("Token added successfully!")
    client.close()


# Função que elimina um token da base de dados
def delete_token(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.delete_one({'access_token': access_token})
    client.close()


# Função que valida um token da base de dados
def validate_token(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    token = tokens.find_one({'access_token': access_token})
    if token is None:
        client.close()
        return False
    # verifica-se se o token expirou
    else:
        if token['expires'] < time.time():
        # como já expirou, então é apagado da base de dados.
            delete_token(access_token)
            client.close()
            return False

    client.close()
    return True

# Função que vai buscar o refresh token a base de dados
def get_refresh_token(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    token = tokens.find_one({'access_token': access_token})
    if token is None:
        client.close()
        return "Token not found"
    else:
        client.close()
        return token['refresh_token']



app.run(host='0.0.0.0', port = 5000, debug = True)