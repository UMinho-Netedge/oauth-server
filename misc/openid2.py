#! python3
from flask import (Flask, make_response, render_template, redirect, request,url_for)
import requests


# flask server
app = Flask(__name__)


keystone_url = "http://192.168.86.210:5000/"

base_auth_json = {
    "auth": {
        "identity": {
            "methods": [
                "password"
            ],
            "password": {
                "user": {
                    "name": "admin",
                    "domain": {
                        "name": "admin"
                    },
                    "password": "admin"
                }
            }
        }
    }
}


@app.route('/login', methods = ['POST'])
def login():
    # get the username and password from the request sent on body in json format
    username = request.json['username']
    password = request.json['password']

    # fill the base_auth_json with the username and password
    base_auth_json['auth']['identity']['password']['user']['name'] = username
    base_auth_json['auth']['identity']['password']['user']['password'] = password

    # make a POST request to get the token
    r = requests.post(keystone_url + "v3/auth/tokens", json = base_auth_json)
    
    # get the token from the response
    #token = r.headers['X-Subject-Token']







app.run(host='0.0.0.0', port = 5001, debug = True)
