
# coding: utf-8

# In[4]:

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

get_ipython().magic(u'matplotlib inline')


# In[5]:

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


# In[6]:

# ******** Insert Year ******
year = 2016;
# ******** Insert Year ******


# In[9]:

start_str = str(year) + '-1-1'
end_str = str(year) + '-12-31'
print(start_str,end_str)

# Set filter variables.
start = ee.Date(start_str)
end = ee.Date(end_str)


# In[ ]:

collNPPFiltered = _L1_NPP_DEKADAL.filterDate(start, end).sort('system:time_start', True)


# In[12]:

# the image.multiply(0.01444) multiplies all bands by 0.01444, including the days in dekad.
# That is why the final WP values were so low...we should first multiply, then, in the same function, add the extra band
def AGBP_multiplication(image):
    img_multi = image.multiply(0.01444).addBands(image.metadata('days_in_dk'))
    return img_multi

AGBP_NPP_multiplied = collNPPFiltered.map(AGBP_multiplication)

# get AGBP value, divide by 10 (as per FRAME spec) to get daily value, and multiply by number of days in dekad
# we don't need to divide by 10 now: it was previously valid on sample data, and we don't use AGBP as input anyway.
def NPP_add_dk(image):   
    mmdk = image.select('b1').multiply(image.select('days_in_dk'))
    return mmdk

NPP_with_dekad = AGBP_NPP_multiplied.map(NPP_add_dk)

sum_AGBP_annual = NPP_with_dekad.reduce(ee.Reducer.sum())


# In[14]:

# Get scale (in meters) information from first image 
scale_calc = ee.Image(collNPPFiltered.first()).projection().nominalScale().getInfo()
print('Image scale: ', scale_calc)

# Convert the collection to a list and get the number of images.
size = collNPPFiltered.size()
print('Number of images (must 36 per year): ', size.getInfo())


# In[17]:

VisPar_AGBPy = {"opacity":1,
                "bands":"b1_sum",
                "min":0,
                "max":180,
                "palette":"f4ffd9,c8ef7e,87b332,566e1b",
                "region":region_json,
                "scale" : scale_calc}


# In[18]:

url_AGBP_annual = sum_AGBP_annual.getThumbUrl(VisPar_AGBPy)
Image(url=url_AGBP_annual)


# In[ ]:



