#!/usr/bin/env python
import ast
import requests
import getpass
import urllib
from requests_oauthlib import OAuth2Session
import time
import os
import ee
import sys
from bs4 import BeautifulSoup
import logging

if sys.version_info > (3 , 0):
    from urllib.parse import unquote
else:
    from urllib import unquote

logger = logging.getLogger ( "wpDataManagementGEE" )
logger.setLevel ( level=logging.DEBUG )

formatter = logging.Formatter ( "%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s" )

fh = logging.FileHandler ( 'wapor_gee_datamanagement.log' )
fh.setLevel ( logging.ERROR )
fh.setFormatter ( formatter )
logger.addHandler ( fh )

ch = logging.StreamHandler ( sys.stdout )
ch.setLevel ( logging.DEBUG )
ch.setFormatter ( formatter )
logger.addHandler ( ch )

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
ee.Initialize ()

# Define URLs
GOOGLE_ACCOUNT_URL = 'https://accounts.google.com'
AUTHENTICATION_URL = 'https://accounts.google.com/ServiceLoginAuth'
APPSPOT_URL = 'https://ee-api.appspot.com/assets/upload/geturl?'

USERNAME = 'fabiolana.notizie@gmail.com'
PASSWORD = 'antar.n1'
# password =  getpass.getpass()

ASSET_NAME = 'users/fabiolananotizie/imgscoll'
ASSET_ITEM_ID = 'users/fabiolananotizie/imgscoll/%s'

# Local file path
file_path = 'images/230.tif'
file_root = file_path.split ( "/" )[1].split ( "." )[0]
logger.info ( file_root )

IMAGE_NAME = 'users/fabiolananotizie/imgscoll/%s' % file_root

session = requests.session ()
login_html = session.get ( GOOGLE_ACCOUNT_URL )

soup_login = BeautifulSoup ( login_html.content , 'html.parser' ).find ( 'form' ).find_all ( 'input' )
payload = {}
for u in soup_login:
    if u.has_attr ( 'value' ):
        payload[u['name']] = u['value']

payload['Email'] = USERNAME
payload['Passwd'] = PASSWORD

auto = login_html.headers.get ( 'X-Auto-Login' )
follow_up = unquote ( unquote ( auto ) ).split ( 'continue=' )[-1]
galx = login_html.cookies['GALX']
payload['continue'] = follow_up
payload['GALX'] = galx

session.post ( AUTHENTICATION_URL , data=payload )

if ee.data.getInfo ( ASSET_NAME ):
    logger.debug('collection %s exist' % ASSET_NAME)
else:
    ee.data.createAsset ( {'type': ee.data.ASSET_TYPE_IMAGE_COLL} , ASSET_NAME )
    logger.debug('Collection %s Created' % ASSET_NAME)

assets_list = ee.data.getList ( params={'id': ASSET_NAME} )
assets_names = [os.path.basename ( asset['id'] ) for asset in assets_list]
already_uploaded = False
if file_root in assets_names:
    logger.error("%s already in collection" % file_root)
    already_uploaded = True

#SE IL FILE GIA ESISTE DA ERRORE
if os.path.exists ( file_path ) and not already_uploaded:
    with open ( file_path , 'rb' ) as f:
        r = session.get ( APPSPOT_URL )
        if r.text.startswith ( '\n<!DOCTYPE html>' ):
            print(
                 'Incorrect credentials. Probably. If you are sure the credentials are OK, refresh the authentication token. '
                 'If it did not work report a problem. They might have changed something in the Matrix.')
            sys.exit ( 1 )
        elif r.text.startswith ( '<HTML>' ):
            logging.debug('Redirecting to upload URL')
            r = session.get ( APPSPOT_URL )
            d = ast.literal_eval ( r.text )
            upload_url = d['url']

            properties = None
            nodata = None

            files = {'file': f}
            resp = session.post ( upload_url , files=files)
            gsid = resp.json ()[0]
            asset_data = {"id": IMAGE_NAME ,
                          "tilesets": [
                           {"sources": [
                                 {"primaryPath": gsid ,
                                  "additionalPaths": []}
                               ]}
                           ] ,
                           "bands": [] ,
                           "properties": properties,
                           "missingData": {"value": nodata}
                      }
            task_id = ee.data.newTaskId ( 1 )[0]
            _ = ee.data.startIngestion ( task_id , asset_data )
else:
    logger.debug('%s already uploaded in GEE - DELETING' % file_root)
    items_in_destination = ee.data.getList ( {'id': ASSET_NAME} )
    for item in items_in_destination:
        #logger.info(item['id'])
        asset_to_delete = item['id']
        if  IMAGE_NAME in asset_to_delete:
            logger.warning('Trovato %s ' % IMAGE_NAME )
            ee.data.deleteAsset ( IMAGE_NAME )
