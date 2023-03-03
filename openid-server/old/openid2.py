#! python3
from flask import Flask, redirect, url_for, session, request, make_response
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
import json


app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY_HERE'
cors = CORS(app, origins=['*','http://localhost:3000'])

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='786927509372-8qqn3ed0lsdjk29ihvg9ob0eerqqia2n.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
    },
)

@app.route('/')
def index():
    if 'google_token' in session:
        data = {}
        data['access_token'] = session['google_access_token']
        data['id_token'] = session['google_id_token']
        data['refresh_token'] = session['google_refresh_token']
        data['expires_at'] = session['google_expires_at']
        #access_token = session['google_access_token']
        #id_token = session['google_id_token']
        #refresh_token = session['google_refresh_token']
        #expires_at = session['google_expires_at']
        #return f"Access token: {access_token}<br> ID token: {id_token}<br> Refresh token: {refresh_token}<br> Expires at: {expires_at}"

        response = make_response(json.dumps(data))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Authorization'] =  data
        response.set_cookie('access_token', data['access_token'], secure=False, httponly=False, expires=data['expires_at'])
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')

        #### FALTA LIGAR A BD E GUARDAR OS DADOS

        return response
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri, access_type='offline')

@app.route('/callback')
def callback():
    token = google.authorize_access_token()
    id_token = token['id_token']
    access_token = token['access_token']
    refresh_token = token.get('refresh_token')
    expires_at = token.get('expires_at')
    session['google_id_token'] = id_token
    session['google_access_token'] = access_token
    session['google_refresh_token'] = refresh_token
    session['google_expires_at'] = expires_at
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


app.run(host='0.0.0.0', port = 5000, debug = True)
