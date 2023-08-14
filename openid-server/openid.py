#! python3

from flask import (Flask, make_response, render_template, redirect, request,url_for)
import time
import json
import os
import jwt
from flask_cors import CORS
from pymongo import MongoClient
import secrets
from osmclient import client
import requests



app = Flask(__name__)
app.debug = True
SECRET_KEY = 'secret-key-of-the-portuguese-empire'
SECRET_KEY2 = 'another-very-secret-key'
COR = CORS(app, origins=['*','http://localhost:3000'])


# dados predefinidos no docker compose
mongodb_addr = os.environ.get("ME_CONFIG_MONGODB_SERVER")
mongodb_port = int (os.environ.get("ME_CONFIG_MONGODB_PORT"))
mongodb_username = os.environ.get("ME_CONFIG_MONGODB_ADMINUSERNAME")
mongodb_password = os.environ.get("ME_CONFIG_MONGODB_ADMINPASSWORD")
osm_hostname = os.environ.get("OSM_HOSTNAME")

### Para testes locais
#mongodb_addr = "mongodb://localhost:27017"
#mongodb_port = 27017
#mongodb_username = ""
#mongodb_password = ""



# receives username and password from the client ( and then tests login on OSM client)
@app.route('/login', methods = ['POST'])
def login():
    # get username and password from request body
    username = request.json.get('username')
    password = request.json.get('password')
    project = request.json.get('project')

    app.logger.debug("username: %s" %username)
    app.logger.debug("password: %s" %password)
    app.logger.debug("project: %s" %project)
    #print(username)
    #print(password)  for debug
    #print(project)

    ####### OSM CLIENT ########
    result = []
    try:
        
        #myclient = client.Client(host="192.168.86.210", sol005=True)
        #myclient = client.Client(host="192.168.86.210", sol005=True, user="test", password="netedge!T3st", project="test", debug=True)
        myclient = client.Client(host=osm_hostname, sol005=True, user=username, password=password, project=project, debug=True)
        result = myclient.nsd.list()
        #result = myclient.get_token()
        app.logger.debug("OSM RESULT: %s", result)
    except Exception as e:
        if "401" in str(e):
            app.logger.debug("Exception: %s", e)
            return make_response('Login failed: Invalid credentials --- Unauthorized', 401)
        else:
            return make_response('error: %s' %e, 500)


   
    # if login is successful, return a response with the access token
    # add a random nonce to the token
    expires = round(time.time() + 3600)
    nonce = secrets.token_urlsafe(16)
    access_token = jwt.encode({'client_id': username, 'exp': expires, 'nonce': nonce}, SECRET_KEY, algorithm = 'HS256')
    # create a refresh token, must be different from access token
    expires2 = round(time.time() + 43200)
    nonce2 = secrets.token_urlsafe(16)                                 
    refresh_token = jwt.encode({'client_id': username, 'exp': expires2, 'nonce': nonce2}, SECRET_KEY2, algorithm = 'HS256')
    
    #print("access_token: ", access_token)
    #print("refresh_token: ", refresh_token)
    app.logger.debug("access_token: %s" %access_token)
    app.logger.debug("refresh_token: %s" %refresh_token)
    scope = {}
    # save token in database
    add_token(access_token, username, scope, expires, nonce)
    add_refresh_token(refresh_token, access_token, username, expires2, nonce2)
    # tenho que adicionar o refresh tokem a bd
    return json.dumps({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires': expires,
        'nsd': result,
    })


## rota de validação do token
# por agora recebe o token no header de autorização
@app.route('/validate', methods = ['POST'])
def validate():
    ## alterar, se falhar alguma destas fases de tirar o token, então tem de ser considerado um pedido invalido
    data = request.headers.get('Authorization')
    print("DATA: ", data)
    access_token = data.split(" ")[1]
    print("ACCESS TOKEN: ", access_token)

    if access_token == None:
        return make_response('No token provided correctly', 401)

    if validate_token(access_token):
        return make_response('Valid access token', 200)
    else:
        return make_response('Invalid access token', 402)
    

## rota de refresh do token 
@app.route('/refresh', methods = ['POST'])
def refresh():
    # recebe o refresh token da mesma maneira que o access token
    # Authorization: Bearer <refresh_token>   faz sentido?
    data = request.headers.get('Authorization')
    print("DATA: ", data)
    refresh_token = data.split(" ")[1]
    print("REFRESH TOKEN: ", refresh_token)

    if refresh_token == None:
        return make_response('No token provided correctly', 401)
    
    # se o token for válido, então é gerado um novo access token
    if validate_refresh_token(refresh_token):
        # get username from refresh token
        username = get_username_from_refresh_token(refresh_token)
        # create a new access token
        expires = round(time.time() + 3600)
        nonce = secrets.token_urlsafe(16)
        access_token = jwt.encode({'client_id': username, 'exp': expires, 'nonce' : nonce}, SECRET_KEY, algorithm = 'HS256')

        expires2 = round(time.time() + 43200)
        nonce2 = secrets.token_urlsafe(16)                                 
        new_refresh_token = jwt.encode({'client_id': username, 'exp': expires2, 'nonce': nonce2}, SECRET_KEY2, algorithm = 'HS256')
        # save token in database
        scope = {} # por agora está assim.... [EM FALTA]
        add_token(access_token, username, scope, expires, nonce)
        delete_refresh_token(refresh_token)
        # return new access token
        return json.dumps({
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'Bearer',
            'expires': expires,
        })
    else:
        return make_response('Invalid refresh token', 402)



# rota de logout. Aqui o token é apagado da base de dados.
# desta forma garantindo que o token não é mais válido.
@app.route('/logout', methods = ['POST'])
def logout():
    # get all info from request header
    app.logger.debug("CHEGUEI AO LOGOUT")

    data = request.headers.get('Authorization')
    if data == None:
        return make_response("Token not received", 401)
    app.logger.debug("DATA: ", data)
    token = data.split(" ")[1]
    app.logger.debug("TOKEN: ", token)
    print("TOKEN: ", token)

    if token == None:
        return make_response("Erro", 401)
    else:
        #access_token = token.split(" ")[1]
        #delete token from database
        delete_token(token)
        print("Token deleted from database successfully!")
        return make_response("sucesso", 200)






###### QUERIES DA BASE DE DADOS ######

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
    #db.create_collection('refresh_tokens')
    #db.create_collection('tokens')
    # close connection
    client.close()

# Função que adiciona tokens a base de dados
def add_token(access_token, username, scope, expires, nonce):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.insert_one({'username': username, 'access_token': access_token, 'scope': scope, 'expires': expires, 'nonce': nonce})
    print("Token added successfully!")
    client.close()

# Função de adiciona o refresh token a base de dados na coleção refresh_tokens
def add_refresh_token(refresh_token, access_token, username, expires, nonce):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    refresh_tokens = db['refresh_tokens']
    # there will be a list with all the access tokens that were generated with the same refresh token
    refresh_tokens.insert_one({'username': username, 'refresh_token': refresh_token, 'access_token': access_token, 'expires': expires, 'nonce': nonce})
    print("Refresh token added successfully!")
    client.close()

# Função que adiciona um access token a coleção de refresh tokens
def add_access_token_to_refresh(refresh_token, access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    refresh_tokens = db['refresh_tokens']
    # there will be a list with all the access tokens that were generated with the same refresh token
    refresh_tokens.update_one({'refresh_token': refresh_token}, {'$push': {'access_token': access_token}})
    print("Access token added successfully!")
    client.close()


# Função que elimina um token da base de dados
def delete_token(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.delete_one({'access_token': access_token})
    client.close()


# Função que elimina um token da base de dados
def delete_token_r(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.delete_one({'access_token': access_token})
    tokens = db['refresh_tokens']
    tokens.delete_one({'access_token': access_token})
    client.close()


# Função que elimina um refresh token da base de dados
def delete_refresh_token(refresh_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['refresh_tokens']
    tokens.delete_one({'refresh_token': refresh_token})
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

# Função que valida um refresh token da base de dados
def validate_refresh_token(refresh_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['refresh_tokens']
    token = tokens.find_one({'refresh_token': refresh_token})
    if token is None:
        client.close()
        return False
    # verifica-se se o token expirou
    else:
        if token['expires'] < time.time():
        # como já expirou, então é apagado da base de dados.
            delete_refresh_token(refresh_token)
            client.close()
            return False

    client.close()
    return True

# Função que retorna o username de um refresh token
def get_username_from_refresh_token(refresh_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['refresh_tokens']
    token = tokens.find_one({'refresh_token': refresh_token})
    if token is None:
        client.close()
        return None
    else:
        # get username
        username = token['username']
        client.close()
        return username



app.run(host='0.0.0.0', port = 5000, debug = True)



