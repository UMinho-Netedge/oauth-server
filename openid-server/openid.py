#! python3

from flask import (Flask, make_response, render_template, redirect, request,url_for)
import time
import json
import os
import jwt
from flask_cors import CORS
from pymongo import MongoClient
#from osmclient import client



app = Flask(__name__)
SECRET_KEY = 'secret-key-of-the-portuguese-empire'
COR = CORS(app, origins=['*','http://localhost:3000'])


mongodb_addr = os.environ.get("ME_CONFIG_MONGODB_SERVER")
mongodb_port = int (os.environ.get("ME_CONFIG_MONGODB_PORT"))
mongodb_username = os.environ.get("ME_CONFIG_MONGODB_ADMINUSERNAME")
mongodb_password = os.environ.get("ME_CONFIG_MONGODB_ADMINPASSWORD")

### Para testes locais
#mongodb_addr = "mongodb://localhost:27017"
#mongodb_port = 27017
#mongodb_username = ""
#mongodb_password = ""

####### OSM CLIENT ########
#myclient = client.Client(host="192.168.86.210", sol005=True, user="test", password="netedge!T3st", project="test")
#myclient.get_token()



# receives username and password from the client ( and then tests login on OSM client)
@app.route('/login', methods = ['POST'])
def login():
    # get username and password from request body
    username = request.json.get('username')
    password = request.json.get('password')
    project = request.json.get('project')

    print(username)
    print(password)
    print(project)

    # test login on OSM client (EM FALTA)

    # if login is successful, return a response with the access token
    expires = round(time.time() + 3600)
    access_token = jwt.encode({'client_id': username, 'exp': expires}, SECRET_KEY, algorithm = 'HS256')

    scope = {}
    # save token in database
    add_token(access_token, username, scope, expires)

    return json.dumps({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires': expires,
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
    

## rota de fefresh do token ?
## preciso de gerar o de refresh token tambem no inicio? ou como sou eu que valido então posso gerar logo outro token de acesso?
## pensar melhor que isto pode gerar problemas de segurança


#logout
@app.route('/logout', methods = ['POST'])
def logout():
    app.logger.info("HEADERS: ", request.headers)
    #print(request.headers)
    #get token from authorization header
    token = request.json.get('access_token')
    #data = request.headers.get('Authorization')
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
    #db.create_collection('clients')
    #db.create_collection('tokens')
    # close connection
    client.close()

# Função que adiciona tokens a base de dados
def add_token(access_token, username, scope, expires):
    client = MongoClient(host=mongodb_addr, port=mongodb_port, username=mongodb_username, password=mongodb_password)
    db = client['openid']
    tokens = db['tokens']
    tokens.insert_one({'username': username, 'access_token': access_token, 'scope': scope, 'expires': expires})
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





app.run(host='0.0.0.0', port = 5000, debug = True)



