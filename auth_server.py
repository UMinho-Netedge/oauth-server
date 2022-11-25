#! python3

import json
import os
import time
from urllib.parse import urlencode, urlparse
#import requests
import urllib.parse as urlparse
import jwt
from cryptography.fernet import Fernet
from flask import (Flask, make_response, render_template, redirect, request,url_for)
import secrets
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

mongodb_addr = os.environ.get("ME_CONFIG_MONGODB_SERVER")
mongodb_port = int (os.environ.get("ME_CONFIG_MONGODB_PORT"))
mongodb_username = os.environ.get("ME_CONFIG_MONGODB_ADMINUSERNAME")
mongodb_password = os.environ.get("ME_CONFIG_MONGODB_ADMINPASSWORD")

# Para testes locais
#mongodb_addr = "localhost"
#mongodb_port = 27017
#mongodb_username = ""
#mongodb_password = ""
#mongodb_database = os.environ.get("ME_CONFIG_MONGODB_DATABASE")

## Chave usada para cifrar o token de acesso dado ao cliente.
## nesta ultima versão não está a ser uadada para efeitos de verificação, porque a verificação está a ser feita na base de dados.
## server apenas para cifrar o JWT.
## no futuro porderá vir a ser usada novamente.
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
    # 1. é feita a ligação com a base de dados.
    client_id = request.get_json().get('client_id')
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    clients = db['clients']
    # 2. verifica se o cliente se encontra na base de dados.
    # se o cliente não se encontrar na base de dados, então é enviado um erro.
    if clients.find_one({'client_id': client_id}) == None:
        client.close()
        return make_response('Client not registered', 401)
    # 3. se o cliente se encontrar na base de dados, então é verificado se o client_secret é válido.
    # para isto é feito a hash do client_secret recebido no pedido e feita a comparação, com a presente na base de dados.
    # se não não forem iguais é lançado um erro.
    elif not bcrypt.checkpw(request.get_json().get('client_secret').encode('utf-8') , clients.find_one({'client_id': client_id})['client_secret']):
            client.close()
            return make_response('Invalid client secret', 403)
    
    # 4. se tudo estiver OK, então é criado o token de acesso (JWT). O qual é cifrado com a chave secreta, inicialmente definida.
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
    # são criados os client_id e client_secret com tamanho de 16 e 32 caracteres respetivamente.
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
    client_id = request.get_json().get('client_id')
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    clients = db['clients']
    # se o cliente não se encontrar na base de dados, então é enviado um erro.
    if clients.find_one({'client_id': client_id}) == None:
        client.close()
        return make_response('Client not registered', 401)
    # se o cliente se encontrar na base de dados, então é verificado se o client_secret é válido.
    # para isto é feito a hash do client_secret recebido no pedido e feita a comparação, com a presente na base de dados.
    # se não não forem iguais é lançado um erro.
    elif not bcrypt.checkpw(request.get_json().get('client_secret').encode('utf-8') , clients.find_one({'client_id': client_id})['client_secret']):
        client.close()
        return make_response('Invalid client secret', 403)
    
    # 2. Se o cliente se encontra registado, então é apagado da base de dados.
    delete_client(client_id)

    # 3. todos os tokens de acesso associados ao cliente são apagados da base de dados.
    delete_tokens(client_id)
    client.close()

    return json.dumps({
        "message": "Client and associated tokens deleted successfully"
    })


# Este endpoint apenas serve para teste e despeza todos os clientes registados no servidor de autorização.
# como agora apenas a hash do client_secret é guardada na base de dados, não vale a pena a mostrar.
@app.route('/clients', methods = ['GET'])
def clients():
    resultado = get_clients()
    for i in resultado:
        i.pop('_id')
        i.pop('client_secret')
        #print(i, type(i['client_secret']))
        # convert bytes to string
        #i['client_secret'] = i['client_secret']
    return json.dumps(resultado)

  
# Neste endpoint é feita a validação do token enviado pelo cliente.
# para este efeito é verificado se o token se encontra na base de dados.
# seguidamente é feita a validação do tempo de expiração do token.
# se tudo estiver OK, então é enviado uma mensagem a indicar que o token é valido.
@app.route('/validate_token', methods = ['POST'])
def validate():
    ## se o token viesse no body era assim.
    #access_token = request.form.get('access_token')
    ## tento tirar o token da query string
    access_token = request.args.get('access_token')
    if access_token == None:
        ## se não conseguir, então tento tirar o token do header de autorização.
        access_token = request.headers.get('authorization')
        access_token = access_token.split(' ')[1]
    ## se não conseguir de nenhuma das formas, então assumo que o cliente enviou um pedido inválido.
    else:
        if access_token == None:
            return make_response('No token provided correctly', 401)
    
    # responde de acordo com o resultado da validação.
    if validate_token(access_token):
        return make_response('Valid access token', 200)
    else:    
        return make_response('Invalid access token', 402)

################# chamadas a base de dados #####################

# Se o servidor for reiniciado, então todos os tokens são apagados da base de dados.
# Deverá apagar também todos os clientes registados? penso que não.
@app.before_first_request
def reset_mongo():
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    print("Connected to database successfully!")
    # delete token collection
    db = client['oauth']
    tokens = db['tokens']
    tokens.delete_many({})
    #client.drop_database('oauth')
    #print("Database dropped successfully!")
    # create the database and collections
    #db = client.oauth
    #db.create_collection('clients')
    #db.create_collection('tokens')
    # close connection
    client.close()

# Função que adiciona clientes a base de dados
def add_client(client_id, client_secret):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    # É usado a bibliotace BCrypt para criar a hash do client_secret.
    hashed_client_secret = bcrypt.hashpw(client_secret.encode('utf-8'), bcrypt.gensalt())
    db = client['oauth']
    clients = db['clients']
    clients.insert_one({'client_id': client_id, 'client_secret': hashed_client_secret})
    client.close()

# Função que adiciona tokens a base de dados
def add_token(access_token, client_id, scope, expires):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    tokens = db['tokens']
    tokens.insert_one({'access_token': access_token, 'client_id': client_id, 'scope': scope, 'expires': expires})
    client.close()

# Função que elimina clietes da base de dados
def delete_client(client_id):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    clients = db['clients']
    clients.delete_one({'client_id': client_id})
    client.close()

# Função que elimina um token da base de dados
def delete_token(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    tokens = db['tokens']
    tokens.delete_one({'access_token': access_token})
    client.close()

# Função que valida um token da base de dados
def validate_token(access_token):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
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

# Função que devolve todos os clientes registados na base de dados
def get_clients():
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    clients = db['clients']
    resultado = []
    for client in clients.find():
        print(client)
        resultado.append(client)
    return resultado

# Função que elimina todos os tokens associados a um cliente, presentes na base de dados
def delete_tokens(client_id):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['oauth']
    tokens = db['tokens']
    tokens.delete_many({'client id': client_id})
    client.close()




app.run(host='0.0.0.0', port = 5001, debug = True)