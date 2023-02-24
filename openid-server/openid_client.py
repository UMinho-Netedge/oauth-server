#! python3


import requests


url = "http://localhost:5000"

# este está a receber o pedido feito pelo browser
def test_login():
    #make get request to /login
    response = requests.get(url + "/login")
    #print(response.headers.get("Authorization"))
    print(response.headers)
    # mas é desta forma que se apanha o header de autorização

data = 'ya29.a0AVvZVsqGqpsskXE6D_zscykb5XvPPCdgdcc6fXg5epGs8cax0sUSXUDYX4I9ID1BOP5YXwYSVSMNPyzy9a_lWGic070eBkmIyb5H3l4Uod7MVStSPEQHhLAYwPqqMzeWpGz0dyVIlGPlhWFL3D3yyRBvFQmiaCgYKAR0SARMSFQGbdwaIoX3Gsu15olDHGwR1QQ0GJA0163'
    
def test_validation():
    headers = {'Authorization' : f'Bearer {data}'}
    response = requests.post(url + "/validate", headers=headers)
    print(response.text)

def test_refresh():
    headers = {'Authorization' : f'Bearer {data}'}
    response = requests.post(url + "/refresh", headers=headers)
    print(response.text)

#test_login()
#test_validation()
test_refresh()
