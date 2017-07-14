import requests
from requests import Request, Session

'''
## UNA RICHIESTA ##
## UNA RICHIESTA ##
url = 'https://api.github.com/events'
r = requests.get(url)

print r.status_code
# print r.text
print r.headers
# print r.json()

print r.headers['Content-Type']
print r.headers.get('content-type')

# filename = 'response'
# r1 = requests.get(url, stream=True)
#
# with open(filename, 'wb') as fd:
#     for chunk in r1.iter_content(chunk_size=128):
#         fd.write(chunk)

# r.encoding = 'ISO-8859-1'
# print r.text
## UNA RICHIESTA ##
'''

## UNA SESSIONE ##
s = requests.Session()
r = s.get(url)
print r.status_code

#Headers INVIATI al server
print r.request.headers

#Headers RICEVUTI dal server
print r.headers
print r.headers['Content-Type']

# req = Request('POST', url) #, data=data, headers=headers)
# prepped = req.prepare()
# print prepped
# print prepped.body

# Chiavi e valori da JSON
commit_data = r.json()
print(commit_data[0].keys())
print(commit_data[0])
print(commit_data[0][u'payload'])
print(commit_data[0].values())



