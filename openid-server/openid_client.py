#! python3


import requests


url = "http://localhost:5000"

# este está a receber o pedido feito pelo browser
def test_login():
    #make get request to /login
    response = requests.get(url + "/login")
    print(response.headers.get("Authorization"))
    # mas é desta forma que se apanha o header de autorização

data = 'ya29.a0AVvZVsollf_tYmuor1W8C4V3cgVgsZiMcotF6dbfjL1BG9xhXsi8-_krKj6_pdmo5A5N-kpF8uKCZwNVXiSjwgaZ7UJvqY3AzNDwVdqMOUekEXYkiLZDODyXTyW-7PZL_yoWCQ_F6FUid0SJ3m-wf5Bbaaw3aCgYKAcYSARMSFQGbdwaIJseo0n0sD7mkLbtX8lmyhQ0163'
    
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
