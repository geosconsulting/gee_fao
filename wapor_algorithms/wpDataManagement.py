#!/usr/bin/env python
import ast
import requests
import os
import ee
import sys
from bs4 import BeautifulSoup
import logging
import retrying
import getpass
from urllib import unquote
from datetime import date, datetime
import calendar
import re
import time

class DataManagement():
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

        self.logger = logging.getLogger ( "wpWin.DataManagement" )
        self.logger.setLevel ( level=logging.DEBUG )
        formatter = logging.Formatter ( "%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s" )

        fh = logging.FileHandler ( 'wapor_gee_datamanagement.log' )
        fh.setLevel ( logging.ERROR )
        fh.setFormatter ( formatter )
        self.logger.addHandler ( fh )

        ch = logging.StreamHandler ( sys.stdout )
        ch.setLevel ( logging.DEBUG )
        ch.setFormatter ( formatter )
        self.logger.addHandler ( ch )

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
        login_html = session.get ( DataManagement.__GOOGLE_ACCOUNT_URL )

        #Check cookies returned because there is an issue with the authentication
        #GAPS , GALX , NID - These cookies are used to identify the user when using Google + functionality.
        #GAPS is still provided
        #self.logger.debug(session.cookies.get_dict ().keys ())
        try:
            galx = session.cookies['GALX']
        except:
            self.logger.info('No cookie GALX')

        soup_login = BeautifulSoup ( login_html.content , 'html.parser' ).find ( 'form' ).find_all ( 'input' )
        payload = {}
        for u in soup_login:
            if u.has_attr ( 'value' ):
                payload[u['name']] = u['value']

        payload['Email'] = self.__username
        payload['Passwd'] = self.__password

        auto = login_html.headers.get ( 'X-Auto-Login' )
        follow_up = unquote ( unquote ( auto ) ).split ( 'continue=' )[-1]
        #Commented as suggested in https://github.com/tracek/gee_asset_manager/issues/36
        #galx = login_html.cookies['GALX']

        payload['continue'] = follow_up

        # Commented as suggested in https://github.com/tracek/gee_asset_manager/issues/36
        #payload['GALX'] = galx

        session.post ( DataManagement.__AUTHENTICATION_URL , data=payload )
        return session

    def get_assets_info(self, asset_name):

        self.asset_path = 'users/fabiolananotizie/' + asset_name
        # self.asset_path = asset_name

        if ee.data.getInfo ( self.asset_path ):
            self.logger.debug('Collection %s Exists' %  self.asset_path)
        else:
            ee.data.createAsset ( {'type': ee.data.ASSET_TYPE_IMAGE_COLL} ,  self.asset_path )
            self.logger.debug('Collection %s Created' %  self.asset_path)

        assets_list = ee.data.getList ( params={'id':  self.asset_path} )
        assets_names = [os.path.basename ( asset['id'] ) for asset in assets_list]
        return assets_names

    def get_upload_url(self,session):

        r = session.get ( DataManagement.__APPSPOT_URL )
        if r.text.startswith ( '\n<!DOCTYPE html>' ):
            self.logger.debug ( 'Incorrect credentials. Probably. If you are sure the credentials are OK, '
                                'refresh the authentication token. If it did not work report a problem. '
                                'They might have changed something in the Matrix.' )
            sys.exit ( 1 )
        elif r.text.startswith ( '<HTML>' ):
            self.logger.debug ( 'Redirecting to upload URL' )
            r = session.get ( DataManagement.__APPSPOT_URL )
            d = ast.literal_eval ( r.text )

        return d['url']

    def retry_if_ee_error(self,exception):
        return isinstance ( exception , ee.EEException )

    def __delete_image(self,image):
        items_in_destination = ee.data.getList ( {'id': self.asset_path} )
        for item in items_in_destination:
            asset_to_delete = item['id']
            if image in asset_to_delete:
                self.logger.warning ( 'Found %s ' % image )
                ee.data.deleteAsset ( image )

    def __upload_image(self,file_path,session,upload_url,image_name,properties,nodata):
        with open ( file_path , 'rb' ) as f:
            files = {'file': f}
            resp = session.post ( upload_url , files=files )
            gsid = resp.json ()[0]
            asset_data = {"id": image_name ,
                          "tilesets": [
                              {"sources": [
                                  {"primaryPath": gsid ,
                                   "additionalPaths": []}
                              ]}
                          ] ,
                          "bands": [] ,
                          "properties": properties ,
                          "missingData": {"value": nodata}
                          }
            task_id = ee.data.newTaskId ( 1 )[0]
            _ = ee.data.startIngestion ( task_id , asset_data )

    @retrying.retry ( retry_on_exception=retry_if_ee_error , wait_exponential_multiplier=1000 ,
                      wait_exponential_max=4000 , stop_max_attempt_number=3 )
    def data_management(self,session,upload_url,assets_names,file_path, properties, nodata):

        file_root = file_path.split ( "/" )[-1].split ( "." )[0]
        image_name = self.asset_path + '/%s' % file_root

        already_uploaded = False
        if file_root in assets_names:
            self.logger.error("%s already in collection" % file_root)
            already_uploaded = True

        #if name file already in that asset it throws an error
        if os.path.exists ( file_path ) and not already_uploaded:
            self.__upload_image(file_path , session , upload_url , image_name,properties,nodata)
        else:
            self.logger.debug('%s already uploaded in GEE - Deleting old file' % file_root)
            self.__delete_image(image_name)
            self.__upload_image ( file_path , session , upload_url , image_name , properties , nodata )

    def get_days_in_dekad(self, year , dekad):
        dekads_eleven = [3 , 8 , 15 , 20 , 24 , 30 , 36]
        if dekad == 6:
            days = calendar.monthrange ( year , 2 )[1] - 20
        elif dekad in dekads_eleven:
            days = 11
        else:
            days = 10
        return days

    def get_month_of_dekad(self,dekad):

        if dekad < 3:
            month_dekad = 1
        elif dekad > 3 and dekad <= 6:
            month_dekad = 2
        elif dekad > 6 and dekad <= 9:
            month_dekad = 3
        elif dekad > 9 and dekad <= 12:
            month_dekad = 4
        elif dekad > 12 and dekad <= 15:
            month_dekad = 5
        elif dekad > 15 and dekad <= 18:
            month_dekad = 6
        elif dekad > 18 and dekad <= 21:
            month_dekad = 7
        elif dekad > 21 and dekad <= 24:
            month_dekad = 8
        elif dekad > 24 and dekad <= 27:
            month_dekad = 9
        elif dekad > 27 and dekad <= 30:
            month_dekad = 10
        elif dekad > 30 and dekad <= 33:
            month_dekad = 11
        else:
            month_dekad = 12

        return month_dekad

    def get_starting_day_of_dekad(self, year , month , dekad):

        first_dekads = range ( 1 , 37 , 3 )
        second_dekads = range ( 2 , 37 , 3 )
        thirds_dekads = range ( 3 , 37 , 3 )

        month_year = (str ( month ) , str ( year ))
        final_date = None
        if dekad in first_dekads:
            final_date = ('01' ,) + month_year + ('12:00:00' ,)
        elif dekad in second_dekads:
            final_date = ('11' ,) + month_year + ('12:00:00' ,)
        elif dekad in thirds_dekads:
            final_date = ('21' ,) + month_year + ('12:00:00' ,)

        starting_day = '-'.join ( final_date )

        return starting_day

    def no_data_assessment(self,path_test):

        file_only = os.path.split ( path_test )[1]
        level , data_component_code = file_only.split ( '_' )[0] , file_only.split ( '_' )[1]

        if level == 'L5':
            if data_component_code == 'AET':
                no_data = 255
            elif data_component_code == 'NPP':
                no_data = -9999
            elif data_component_code == 'AGBP':
                no_data = -9999
            elif data_component_code == 'RET':
                no_data = 255
            elif data_component_code == 'PCP':
                no_data = -9999
            elif data_component_code == 'LCC':
                no_data = 255
            elif data_component_code == 'TFRAC':
                no_data = 255
            else:
                no_data = None
        else:
            no_data = None

        return no_data

    def metadata_generator(self,gee_file):

        gee_asset = gee_file.split ( '.' )[0]
        level = int(re.split ( '(\d.*)' , gee_file.split ( "_" )[0] )[1])
        area = 'AfNE'

        initial_date = datetime.strptime ( '1970-1-1' , "%Y-%m-%d" )
        date_part = gee_file.split ( '_' )[2]
        year = int ( '20' + gee_file.split ( '_' )[2][0:2] )

        number_of_days = 0
        if len ( date_part ) == 4:
            dekad = int ( gee_file.split ( '_' )[2][2:4] )
            number_of_days = self.get_days_in_dekad ( year , dekad )
            month = self.get_month_of_dekad ( dekad )
            start_date = datetime.strptime ( self.get_starting_day_of_dekad ( year , month , dekad ) , "%d-%m-%Y-%H:%M:%S" )
        elif len ( date_part ) == 6:
            month = int ( gee_file.split ( '_' )[2][2:4] )
            day = int ( gee_file.split ( '_' )[2][4:6] )
            s = str ( day ) + "-" + str ( month ) + "-" + str ( year ) + "-" + '12:00:00'
            start_date = datetime.strptime ( s , "%d-%m-%Y-%H:%M:%S" )

        unix_time_manual = (start_date - initial_date).total_seconds () * 1000
        metadata = {'id_no': gee_file , 'system:time_start': unix_time_manual , 'level': level , 'area': area}

        if number_of_days != 0:
            metadata['days_in_dk'] = number_of_days

        return metadata

def main(argv):

    if len ( argv ) != 1:
        print '\nSend a filename or directory\n'
        sys.exit ( 'Usage: wpDataManagement.py <directory_name>' )

    username_gee = raw_input ( 'Please Enter a Valid GEE User Name (without @gmail.com): ' ) + "@gmail.com"
    password_gee = getpass.getpass ( 'Please Enter a Valid GEE Password: ' )

    #gee_root = 'projects/fao-wapor/'

    data_management_session = DataManagement ( username_gee , password_gee )
    active_session = data_management_session.create_google_session ()
    upload_url = data_management_session.get_upload_url(active_session)

    path_or_file = argv[0]

    # Receives one single file
    if os.path.isfile ( path_or_file ):
        gee_asset = '_'.join (path_or_file.split('/')[-1].split ( "_" )[0:2] )
        file_only = os.path.split ( path_or_file )[1]
        gee_file = file_only.split ( "." )[0]

        no_data = data_management_session.no_data_assessment ( path_or_file )
        properties = data_management_session.metadata_generator ( gee_file )

        data_management_session.logger.info(properties)
        data_management_session.logger.info (no_data )

        present_assets = data_management_session.get_assets_info ( gee_asset )
        data_management_session.data_management ( active_session ,
                                                  upload_url ,
                                                  present_assets ,
                                                  path_or_file,
                                                  properties ,
                                                  no_data )

    # Receives un directory containing al new files sent from FRAME
    elif os.path.isdir ( path_or_file ):
        new_released_files = []
        root_dir = None
        for (dirpath , dirnames , filenames) in os.walk ( path_or_file ):
            new_released_files.extend (filenames )
            root_dir = dirpath
            break

        for each_file in new_released_files:
            no_data = data_management_session.no_data_assessment ( each_file )
            file_temp = root_dir + "/" + each_file
            gee_asset = '_'.join ( each_file.split ( "_" )[0:2] )
            gee_file = each_file.split ( "." )[0]
            properties = data_management_session.metadata_generator ( gee_file )

            data_management_session.logger.info ( properties )
            data_management_session.logger.info ( no_data )

            present_assets = data_management_session.get_assets_info (gee_asset)
            data_management_session.data_management ( active_session ,
                                                      upload_url ,
                                                      present_assets ,
                                                      file_temp ,
                                                      properties ,
                                                      no_data )

if __name__ == "__main__":
    main ( sys.argv[1:] )