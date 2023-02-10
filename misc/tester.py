#! python3

import requests
import json

# exemplo de pedido de token de acesso para o servidor de autorização.
def test_get_token():
    url = 'http://localhost:5001/token'
    body = {'grant_type': 'client_credentials', 'client_id': 'DUCVckr0z2rxRBbBX6eHzA', 'client_secret': 'yF2ZB_lOVKqNObxXJRl1sq-pKox_x0MnZSG40wQfZiQ'}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    print(response.text)

# exemplo de pedido de registo de cliente para o servidor de autorização.
def test_register():
    url = 'http://localhost:5001/register'
    response = requests.get(url)
    print(response.text)

# exemplo de pedido para apagar um cliente do servidor de autorização.
def test_delete(client_id, client_secret):
    url = 'http://localhost:5001/delete'
    headers = {'Content-Type': 'application/json'}
    body = {'client_id': client_id, 'client_secret' : client_secret} 
    response = requests.post(url, data=json.dumps(body), headers=headers)
    print(response.text)

# exemplo de pedido de validação de token de acesso para o servidor de autorização.
# the token must be sent in the authorization header as a oauth2 bearer token.
def test_validate(access_token):
    url = 'http://localhost:5001/validate_token'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
    response = requests.post(url, headers=headers)
    print(response.text)


# exemplo de pedido que devolve todos os clientes registados no servidor de autorização. (util para debug)
def test_get_clients():
    url = 'http://localhost:5001/clients'
    response = requests.get(url)
    print(response.text)

#test_token()
#test_register()
#test_delete('HGsC5D-v2z7BAOSuy2v8zw', '2kvLW6aWHYKRRN0jNXr2HLw6W3mDEWThzH-EY4NXPQY')
#test_validate("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJ2TkRHM3c2UmQzWUJDdWZqTmZncDN3IiwiZXhwIjoxNjY4NTIzMjAwLjAzMDEyMzJ9.onJFymwnHsydQl3XgGy2LGb-pwY5VTwaTxxQ04oEvJY")

test_get_clients()


