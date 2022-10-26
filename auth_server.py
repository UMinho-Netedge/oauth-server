#! python3

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

## Neste ficheiro ficam guardados os dados do cliente que se encontra registado no servidor de autorização.
## Desta maneira é preciso fazer sempre load ao iniciar.
with open('reg_clients.json') as f:
    registered_clients = json.load(f)
f.close()


## Chave usada para cifrar o token de acesso dado ao cliente.
SECRET_KEY = 'secret-key-of-the-portuguese-empire'


## Endpoint onde o cliente faz o pedido de autorização e recebe um token de acesso.
'''
Para testar este endpoint, pode-se enviar o seguinte pedido POST:
no body incluir os seguintes campos:
grant_type: client_credentials
client_id: XXXXXXXX
client_secret: XXXXXXXX
'''
@app.route('/token', methods = ['POST'])
def token():
    # 1. Verifica-se se o cliente se encontra registado no servidor de autorização.
    client_id = request.form.get('client_id')
    if client_id not in registered_clients:
        return make_response('Client not registered', 401)
    
    # 3. Se o cliente se encontra registado, verifica-se se o client_secret é válido.
    client_secret = request.form.get('client_secret')
    if client_secret != registered_clients[client_id]:
        return make_response('Invalid client secret', 403)
    
    # 4. se tudo estiver OK, então é criado o token de acesso. O qual é cifrado com a chave secreta, inicialmente definida.
    access_token = jwt.encode({'client_id': client_id, 'exp': time.time() + 3600}, SECRET_KEY, algorithm = 'HS256')

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

    # aqui são armazenados os dados do cliente registado no servidor de autorização.
    registered_clients[client_id] = client_secret

    # aqui é guardado no ficheiro os dados do cliente registado.
    with open('reg_clients.json', 'w') as f:
        json.dump(registered_clients, f)
    f.close()

    # finalmente é enviado ao cliente o client_id e o client_secret.
    return json.dumps({
        'client_id': client_id,
        'client_secret': client_secret,
        "message": "Client registered successfully"
    })

# Este endpoint apenas serve para teste e despeza todos os clientes registados no servidor de autorização.
@app.route('/clients', methods = ['GET'])
def clients():
    return json.dumps(registered_clients)

  
# Neste endpoint é feita a validação do token enviado pelo cliente.
# Como está a usar usado uma chave simátrica apenas conhecida por este servidor, se for possivel decifar então comprova-se que o token é autentico.
# seguidamente é feita a validação do tempo de expiração do token.
# se tudo estiver OK, então é enviado uma mensagem a indicar que o token é valido.
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


app.run(host='0.0.0.0', port = 5001, debug = True)