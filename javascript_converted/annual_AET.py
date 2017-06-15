
# coding: utf-8

# In[15]:

import ee
from IPython import display
from IPython.display import Image
import math
import matplotlib.pyplot as plt
from osgeo import gdal
import tempfile
import urllib
import zipfile
import os
from mpl_toolkits.basemap import Basemap
import numpy as np
import datetime
import pandas as pd
from sql2gee import SQL2GEE
import unicode

get_ipython().magic(u'matplotlib inline')


# In[16]:

ee.Initialize()

_L1_RET_DAILY = ee.ImageCollection("projects/fao-wapor/L1_RET")
_L1_PCP_DAILY = ee.ImageCollection("projects/fao-wapor/L1_PCP")
_L1_NPP_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_NPP")
_L1_AET_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_AET")
_L1_TFRAC_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_TFRAC")

_REGION = [[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0], [-25.0, -37.0]]
_COUNTRIES = ee.FeatureCollection('ft:1ZDEMjtnWm_smu7l_z3fx91BbxyCRzP2A3cEMrEiP')
_WSHEDS = ee.FeatureCollection('ft:1IXfrLpTHX4dtdj1LcNXjJADBB-d93rkdJ9acSEWK')

# AREA OF INTEREST
region_L1 = ee.Geometry.Polygon([[[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0], [-25.0, -37.0]]])
region_json= [[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0], [-25.0, -37.0]]


# In[17]:

# ******** Insert Year ******
year = 2016;
# ******** Insert Year ******


# In[18]:

start_str = str(year) + '-1-1'
end_str = str(year) + '-12-31'
print(start_str, end_str)

# Set filter variables.
start = ee.Date(start_str)
end = ee.Date(end_str)

collAETFiltered = _L1_AET_DEKADAL.filterDate(start, end).sort('system:time_start', True)
                
# Get scale (in meters) information from first image 
scale_calc = ee.Image(collAETFiltered.first()).projection().nominalScale().getInfo()
print('Image scale: ', scale_calc)


# In[41]:

# Convert the collection to a list and get the number of images.
size = collAETFiltered.size()
print('Number of images (must 36 per year): ', size.getInfo())

# add image property (days in dekad) as band
def n_days(image):
    days = image.addBands(image.metadata('days_in_dk'))
    return days
ETaColl1 = collAETFiltered.map(n_days)

# get ET value, divide by 10 (as per FRAME spec) to get daily value, 
# and multiply by number of days in dekad
def ETdk(image):
    mmdk = image.select('b1').divide(10).multiply(image.select('days_in_dk'))
    return mmdk
AET_annual = ETaColl1.map(ETdk)

sum_AET_annual = AET_annual.reduce(ee.Reducer.sum())
print sum_AET_annual.getInfo()['bands'][0]['id']


# In[33]:

VisPar_ETay = {"opacity":1,
                "bands":'b1_sum',
                "min":0,
                "max":2000,
                "palette":"d4ffc6,beffed,79c1ff,3e539f",
                "region":region_json,
                "scale" : scale_calc}


# In[34]:

url_AET_annual = sum_AET_annual.getThumbUrl(VisPar_ETay)
Image(url=url_AET_annual)


# In[ ]:



