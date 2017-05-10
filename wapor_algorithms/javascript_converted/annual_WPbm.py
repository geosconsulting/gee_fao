
# coding: utf-8

# In[1]:

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


# In[2]:

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


# In[3]:

# ******** Insert Year ******
year = 2016;
# ******** Insert Year ******
start_str = str(year) + '-1-1'
end_str = str(year) + '-12-31'
print(start_str,end_str)

# Set filter variables.
start = ee.Date(start_str)
end = ee.Date(end_str)


# In[6]:

collNPPFiltered = _L1_NPP_DEKADAL.filterDate(start, end).sort('system:time_start', True)


# In[8]:

# Get scale (in meters) information from first image 
scale_calc = ee.Image(collNPPFiltered.first()).projection().nominalScale().getInfo()
print('Image scale: ', scale_calc)

# Convert the collection to a list and get the number of images.
size = collNPPFiltered.size()
print('Number of images (must 36 per year): ', size.getInfo())


# In[9]:

VisPar_ETay = {"opacity":1,
                "bands" : 'b1_sum',
                "min":0,
                "max":2000,
                "palette":"d4ffc6,beffed,79c1ff,3e539f",
                "region": region_json,
                "scale" : scale_calc}


VisPar_AGBPy = {"opacity":1,
                "bands":"b1_sum",
                "min":0,
                "max":180,
                "palette":"f4ffd9,c8ef7e,87b332,566e1b",
                "region": region_json,
                "scale" : scale_calc}


VisPar_WPbm = {"opacity":1,
               "bands":"b1_sum",
               "max":1.2,
               "palette":"bc170f,e97a1a,fff83a,9bff40,5cb326",
               "region": region_json,
               "scale" : scale_calc}


# In[14]:

AGBPy = ee.Image("projects/fao-wapor/AGBP_Annual/AGBP-" + str(year))
ETa = ee.Image("projects/fao-wapor/AET_Annual/AET-" + str(year))

# Or, as you will already have calculated AET annual and AGBP annual:
# AGBPy/(AETy*10) where *10 is to convert mm into m³/ha 

WPbm = AGBPy.divide(ETa.multiply(10))
WPbm.getInfo()


# In[16]:

url_WPbm_annual = WPbm.getThumbUrl(VisPar_WPbm)
Image(url=url_WPbm_annual)


# In[ ]:



