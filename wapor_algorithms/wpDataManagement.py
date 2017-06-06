#!/usr/bin/env python
import ast
import requests
import os
import ee
import sys
from bs4 import BeautifulSoup
import logging
import getpass

if sys.version_info > (3 , 0):
    from urllib.parse import unquote
else:
    from urllib import unquote

class wpDataManagement():
    """Algorithm for managing assets in GEE"""

    # Define URLs
    __GOOGLE_ACCOUNT_URL = 'https://accounts.google.com'
    __AUTHENTICATION_URL = 'https://accounts.google.com/ServiceLoginAuth'
    __APPSPOT_URL = 'https://ee-api.appspot.com/assets/upload/geturl?'

    def __init__(self,usr,pwd): #,local_data,asset_name):

        """Constructor for wpDataManagement"""
        ee.Initialize ()

        self.__username = usr
        self.__password = pwd

        self.logger = logging.getLogger ( "wpDataManagementGEE" )
        self.logger.setLevel ( level=logging.DEBUG )
        formatter = logging.Formatter ( "%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s" )

        fh = logging.FileHandler ( 'wapor_gee_datamanagement.log' )
        fh.setLevel ( logging.ERROR )
        fh.setFormatter ( formatter )
        self.logger.addHandler ( fh )

        ch = logging.StreamHandler ( sys.stdout )

    @property
    def user_name(self):
        return self.__username

    @user_name.setter
    def user_name(self , name):
        self.__username = name

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self , pwd):
        self.__password = pwd

    def create_google_session(self):

        session = requests.session ()
        login_html = session.get ( wpDataManagement.__GOOGLE_ACCOUNT_URL )

        soup_login = BeautifulSoup ( login_html.content , 'html.parser' ).find ( 'form' ).find_all ( 'input' )
        payload = {}
        for u in soup_login:
            if u.has_attr ( 'value' ):
                payload[u['name']] = u['value']

        payload['Email'] = self.__username
        payload['Passwd'] = self.__password

        auto = login_html.headers.get ( 'X-Auto-Login' )
        follow_up = unquote ( unquote ( auto ) ).split ( 'continue=' )[-1]
        galx = login_html.cookies['GALX']
        payload['continue'] = follow_up
        payload['GALX'] = galx

        session.post (wpDataManagement.__AUTHENTICATION_URL , data=payload )

        return session

    def get_assets_info(self,asset_name):

        self.asset_path = 'users/fabiolananotizie/' + asset_name
        # self.asset_path = asset_name

        if ee.data.getInfo ( self.asset_path ):
            self.logger.debug('Collection %s exist' %  self.asset_path)
        else:
            ee.data.createAsset ( {'type': ee.data.ASSET_TYPE_IMAGE_COLL} ,  self.asset_path )
            self.logger.debug('Collection %s Created' %  self.asset_path)

        assets_list = ee.data.getList ( params={'id':  self.asset_path} )
        assets_names = [os.path.basename ( asset['id'] ) for asset in assets_list]

        return assets_names

    def data_management(self,session,assets_names,file_path, properties, nodata):

        self.file_root = file_path.split ( "/" )[-1].split ( "." )[0]
        self.logger.info ( self.file_root )
        self.image_name = self.asset_path + '/%s' % self.file_root

        already_uploaded = False
        if self.file_root in assets_names:
            self.logger.error("%s already in collection" % self.file_root)
            already_uploaded = True

        #if name file already in that asset it throws an error
        if os.path.exists ( file_path ) and not already_uploaded:
            with open ( file_path , 'rb' ) as f:
                r = session.get (wpDataManagement.__APPSPOT_URL )
                if r.text.startswith ( '\n<!DOCTYPE html>' ):
                    self.logger.debug( 'Incorrect credentials. Probably. If you are sure the credentials are OK, '
                                       'refresh the authentication token. If it did not work report a problem. '
                                       'They might have changed something in the Matrix.')
                    sys.exit ( 1 )
                elif r.text.startswith ( '<HTML>' ):
                    self.logger.debug('Redirecting to upload URL')
                    r = session.get (wpDataManagement.__APPSPOT_URL )
                    d = ast.literal_eval ( r.text )
                    upload_url = d['url']

                    files = {'file': f}
                    resp = session.post ( upload_url , files=files)
                    gsid = resp.json ()[0]
                    asset_data = {"id": self.image_name ,
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
            self.logger.debug('%s already uploaded in GEE - DELETING' % self.file_root)
            items_in_destination = ee.data.getList ( {'id': self.asset_path} )
            for item in items_in_destination:
                #logger.info(item['id'])
                asset_to_delete = item['id']
                if  self.image_name in asset_to_delete:
                    self.logger.warning('Found %s ' % self.image_name )
                    ee.data.deleteAsset ( self.image_name )

def task_management(self):
    pass

#path_test = '../snippets/images/230.tif'
path_test = '../snippets/files_test'
#path_test = '../snippets/files_test/L1_AET_0910.tif'

username_gee = 'fabiolana.notizie@gmail.com'
password_gee =  getpass.getpass()
properties = None
nodata = None

#raiz = 'projects/fao-wapor/'
raiz = 'users/fabiolananotizie/'
data_management_session = wpDataManagement ( username_gee , password_gee )
active_session = data_management_session.create_google_session ()

if os.path.isfile ( path_test ):
        gee_asset = '_'.join (path_test.split('/')[-1].split ( "_" )[0:2] )
        gee_file = path_test.split('/')[-1].split ( "." )[0]
        print  raiz + gee_asset + "/" + gee_file

        present_assets = data_management_session.get_assets_info ( gee_asset )
        data_management_session.data_management ( active_session , present_assets , path_test, properties , nodata )
elif os.path.isdir ( path_test ):
    new_files = []
    for (dirpath , dirnames , filenames) in os.walk ( path_test ):
        new_files.extend ( filenames )
        # break
    for each_file in new_files:
        print each_file
        gee_asset = '_'.join ( each_file.split ( "_" )[0:2] )
        gee_file = each_file.split ( "." )[0]
        #data_management_session = wpDataManagement ( username_gee , password_gee , path_test , gee_asset )
        #active_session = data_management_session.create_google_session ()
        present_assets = data_management_session.get_assets_info (gee_asset)
        data_management_session.data_management ( active_session , present_assets , each_file , properties , nodata )

