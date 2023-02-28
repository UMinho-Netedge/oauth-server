#! python3

from flask import (Flask, make_response, render_template, redirect, request,url_for)
import time
import json
import jwt
#from osmclient import client



app = Flask(__name__)
SECRET_KEY = 'secret-key-of-the-portuguese-empire'

####### OSM CLIENT ########
#myclient = client.Client(host="192.168.86.210", sol005=True, user="test", password="netedge!T3st", project="test")
#myclient.get_token()



# receives username and password from the client ( and then tests login on OSM client)
@app.route('/login')
def login():
    # get username and password from request body
    username = request.args.get('username')
    password = request.args.get('password')
    project = request.args.get('project')

    # test login on OSM client

    # if login is successful, return a response with the access token
    expires = time.time() + 3600
    access_token = jwt.encode({'client_id': username, 'exp': time.time() + 3600}, SECRET_KEY, algorithm = 'HS256')

    return json.dumps({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires': expires,
    })

app.run(host='0.0.0.0', port = 5000, debug = True)



