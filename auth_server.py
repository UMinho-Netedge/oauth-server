#! python3

import json
import time
from urllib.parse import urlencode, urlparse
#import requests
import urllib.parse as urlparse
import jwt
from cryptography.fernet import Fernet
from flask import (Flask, make_response, render_template, redirect, request,url_for)
import secrets
from pymongo import MongoClient


app = Flask(__name__)

## Chave usada para cifrar o token de acesso dado ao cliente.
SECRET_KEY = 'secret-key-of-the-portuguese-empire'


## Endpoint onde o cliente faz o pedido de autorização e recebe um token de acesso.
'''
Para testar este endpoint, pode-se enviar o seguinte pedido POST:
no body incluir os seguintes campos em JSON:
grant_type: client_credentials
client_id: XXXXXXXX
client_secret: XXXXXXXX
'''
@app.route('/token', methods = ['POST'])
def token():
    # verifica se o cliente se encontra na base de dados.
    client_id = request.get_json().get('client_id')
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    clients = db['clients']
    # se o cliente não se encontrar na base de dados, então é enviado um erro.
    if clients.find_one({'client_id': client_id}) == None:
        client.close()
        return make_response('Client not registered', 401)
    # se o cliente se encontrar na base de dados, então é verificado se o client_secret é válido.
    elif clients.find_one({'client_id': client_id})['client_secret'] != request.get_json().get('client_secret'):
        client.close()
        return make_response('Invalid client secret', 403)
    
    # 4. se tudo estiver OK, então é criado o token de acesso. O qual é cifrado com a chave secreta, inicialmente definida.
    access_token = jwt.encode({'client_id': client_id, 'exp': time.time() + 3600}, SECRET_KEY, algorithm = 'HS256')

    # 5. O token de acesso é guardado na base de dados.
    add_token(access_token, client_id, 'read', time.time() + 3600)
    client.close()

    # 5. O token de acesso é enviado ao cliente.
    return json.dumps({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3600
    })


# Endpoint usado para registo de novo clientes. Aqui o cliente apenas precisa de fazer um pedido get.
# A resposta será um client_id e um client_secret gerados aleatoriamente.
@app.route('/register', methods = ['GET'])
def register():
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)

    # a informação do cliente é guardada na base de dados.
    add_client(client_id, client_secret)

    # finalmente é enviado ao cliente o client_id e o client_secret.
    return json.dumps({
        'client_id': client_id,
        'client_secret': client_secret,
        "message": "Client registered successfully"
    })

## Endpoint onde é feito o pedido para apagar o cliente da "base de dados".
'''
Para testar este endpoint, pode-se enviar o seguinte pedido POST:
no body incluir os seguintes campos em JSON:
client_id: XXXXXXXX
client_secret: XXXXXXXX
'''
@app.route('/delete', methods = ['POST'])
def delete():
    # 1. Verifica-se se o cliente se encontra registado no servidor de autorização.

    # verifica se o cliente se encontra na base de dados.
    client_id = request.get_json().get('client_id')
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    clients = db['clients']
    # se o cliente não se encontrar na base de dados, então é enviado um erro.
    if clients.find_one({'client_id': client_id}) == None:
        client.close()
        return make_response('Client not registered', 401)
    # se o cliente se encontrar na base de dados, então é verificado se o client_secret é válido.
    elif clients.find_one({'client_id': client_id})['client_secret'] != request.get_json().get('client_secret'):
        client.close()
        return make_response('Invalid client secret', 403)
    
    # 2. Se o cliente se encontra registado, então é apagado da base de dados.
    delete_client(client_id)
    client.close()

    return json.dumps({
        "message": "Client deleted successfully"
    })


# Este endpoint apenas serve para teste e despeza todos os clientes registados no servidor de autorização.
@app.route('/clients', methods = ['GET'])
def clients():
    resultado = get_clients()
    print(resultado)
    #clean result
    for i in resultado:
        i.pop('_id')
    return json.dumps(resultado)

  
# Neste endpoint é feita a validação do token enviado pelo cliente.
# Como está a usar usado uma chave simátrica apenas conhecida por este servidor, se for possivel decifar então comprova-se que o token é autentico.
# seguidamente é feita a validação do tempo de expiração do token.
# se tudo estiver OK, então é enviado uma mensagem a indicar que o token é valido.
@app.route('/validate_token', methods = ['POST'])
def validate():
    #access_token = request.form.get('access_token')
    access_token = request.args.get('access_token')
    print("access_token: ", access_token)
    if validate_token(access_token):
        return make_response('Valid access token', 200)
    else:    
        return make_response('Invalid access token', 401)

################# chamadas a base de dados #####################

# everytime the serser starts run this function
@app.before_first_request
def reset_mongo():
    client = MongoClient('mongodb', 27017)
    print("Connected to database successfully!")
    # delete the database and collections if they exist
    client.drop_database('oauth')
    print("Database dropped successfully!")
    # create the database and collections
    db = client.oauth
    db.create_collection('clients')
    db.create_collection('tokens')
    # close connection
    client.close()

# add client to database
def add_client(client_id, client_secret):
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    clients = db['clients']
    clients.insert_one({'client_id': client_id, 'client_secret': client_secret})
    client.close()

# add token to database
def add_token(access_token, client_id, scope, expires):
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    tokens = db['tokens']
    tokens.insert_one({'access_token': access_token, 'client_id': client_id, 'scope': scope, 'expires': expires})
    client.close()

# delete client from database
def delete_client(client_id):
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    clients = db['clients']
    clients.delete_one({'client_id': client_id})
    client.close()

# delete token from database
def delete_token(access_token):
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    tokens = db['tokens']
    tokens.delete_one({'access_token': access_token})
    client.close()

# validate token from database
def validate_token(access_token):
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    tokens = db['tokens']
    token = tokens.find_one({'access_token': access_token})
    if token is None:
        client.close()
        return False
    else:
        # check if token has expired
        if token['expires'] < time.time():
            client.close()
            return False
    client.close()
    return True

# get all clients from database
def get_clients():
    client = MongoClient('mongodb', 27017)
    db = client['oauth']
    clients = db['clients']
    resultado = []
    for client in clients.find():
        print(client)
        resultado.append(client)
    return resultado



app.run(host='0.0.0.0', port = 5001, debug = True)