#! python3


import requests


url = "http://localhost:5000"

# este está a receber o pedido feito pelo browser
def test_login():
    #make get request to /login
    response = requests.get(url + "/")
    #print(response.headers.get("Authorization"))
    print(response.headers)
    # mas é desta forma que se apanha o header de autorização

data = "im an access token"

def test_validation():
    headers = {'Authorization' : f'Bearer {data}'}
    response = requests.post(url + "/validate", headers=headers)
    print(response.text)

def test_refresh():
    headers = {'Authorization' : f'Bearer {data}'}
    response = requests.post(url + "/refresh", headers=headers)
    print(response.text)

test_login()
#test_validation()
#test_refresh()
