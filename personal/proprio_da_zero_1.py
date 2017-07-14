import requests
from requests import Request, Session

url_1 = 'https://tutsplus.com/'
url_2 = 'https://tutsplus.com/tutorials'

req_one = requests.get(url_1)
print req_one.cookies['_tuts_session']

req_two = requests.get(url_2)
print req_two.cookies['_tuts_session']

ssn_one = requests.Session()
ssn_one.get(url_1)
print ssn_one.cookies['_tuts_session']

req_three = ssn_one.get(url_2)
print req_three.cookies['_tuts_session']


def write_cookies():
    ssn = requests.Session ()
    ssn.cookies.update ( {'visit-month': 'February'} )
    reqOne = ssn.get ( 'http://httpbin.org/cookies' )
    print(reqOne.text)
    # prints information about "visit-month" cookie
    reqTwo = ssn.get ( 'http://httpbin.org/cookies' , cookies={'visit-year': '2017'} )
    print(reqTwo.text)
    # prints information about "visit-month" and "visit-year" cookie
    reqThree = ssn.get ( 'http://httpbin.org/cookies' )
    print(reqThree.text)
    # prints information about "visit-month" cookie

write_cookies ()

