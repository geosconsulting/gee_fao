
# coding: utf-8

# In[10]:

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
import numpy as np
import datetime
import pandas as pd
from sql2gee import SQL2GEE

get_ipython().magic(u'matplotlib inline')


# In[11]:

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


# In[12]:

# ******** Insert Year ******
year = 2016;
# ******** Insert Year ******
start_str = str(year) + '-1-1'
end_str = str(year) + '-12-31'
print(start_str,end_str)

# Set filter variables.
start = ee.Date(start_str)
end = ee.Date(end_str)


# In[13]:

collAETFiltered = _L1_AET_DEKADAL.filterDate(start, end).sort('system:time_start',True)
collTFRACFiltered = _L1_TFRAC_DEKADAL.filterDate(start, end).sort('system:time_start', True)

TFRAC_AET_collection = collAETFiltered.merge(collTFRACFiltered)


# In[66]:

print TFRAC_AET_collection.first().propertyNames().getInfo()
print TFRAC_AET_collection.first().propertyNames().getInfo()[7]


# In[113]:

# JOINING TWO Collections - Start
Join = ee.Join.inner()
FilterOnStartTime = ee.Filter.equals(
                       leftField = 'system:time_start', 
                       rightField = 'system:time_start'
                       )

TFRAC_AET_collection_Join = ee.ImageCollection(Join.apply(
                                        collAETFiltered,
                                        collTFRACFiltered,
                                        FilterOnStartTime))
print("Joined collections",TFRAC_AET_collection_Join)
# JOINING TWO Collections - End


# In[119]:

# TESTING Image metadata and properties - start
first_immage_of_join = ee.Image(TFRAC_AET_collection_Join.first())
print("First: ",first_immage_of_join)

properties = first_immage_of_join.propertyNames()
print("Metadata properties of First: ", properties)

AET_component = ee.Image(first_immage_of_join.get("primary"))
print("get(days_in_dk)", AET_component.get('days_in_dk'))

AET_component_3dekad = ee.Image("projects/fao-wapor/L1_TFRAC/L1_TFRAC_1003")
days_directly = AET_component_3dekad.get('days_in_dk')
print("Third Dekad January 11 days check",days_directly.getInfo())

# Get scale (in meters) information from first image 
scale_calc = AET_component_3dekad.projection().nominalScale().getInfo()
print('Image scale: ', scale_calc)


# In[123]:

TFRAC_component = ee.Image(first_immage_of_join.get("secondary"));
TFRAC_band = TFRAC_component.select('b1');

# ***************** TESTING Image metadata and properties - End
# ***************** CALCULATE TFRAC ANNUAL - Start
# Tfrac is the percentage of T in AET (the rest is evaporation from soil), 
# so to get Transpiration, similarly to AET annual:
# SUM((Tfrac*AETdk)*0.1)*N_days_in_dk)
contatore = 1
def Tfrac_AETdk(image):
    # print contatore
    image_aet = ee.Image(image.get("primary"))     
    band_aet = image.select("b1")    
    image_tfrac = ee.Image(image.get("secondary"))
    t_a = ((image_aet.select('b1').multiply(image_tfrac.select('b1').divide(100)))
         .multiply(0.1)).multiply(ee.Number(image_aet.get('days_in_dk'))).float()
    # contatore += contatore
    return ee.Image(t_a)

T_annual = TFRAC_AET_collection_Join.map(Tfrac_AETdk)
print("TFRAC_annual_split",T_annual)


# In[126]:

first_image_tfrac = ee.Image(T_annual.first())

SUM_TFRAC_annual = T_annual.reduce(ee.Reducer.sum()).toFloat()
print SUM_TFRAC_annual


# In[129]:

# Get scale (in meters) information from first image 
scale_calc = first_image_tfrac.projection().nominalScale().getInfo()
print('Image scale: ', scale_calc)

# Convert the collection to a list and get the number of images.
size = T_annual.size()
print('Number of images (must 36 per year): ', size.getInfo())


# In[135]:

VisPar_ETay = {"opacity":1,
                "bands":'b1_sum',
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

VisPar_TFRAC = {"opacity":1,
               "bands":"b1_sum",
               "max":800,
               "palette":"fffcdb,b4ffa6,3eba70,195766",
               "region": region_json,
               "scale" : scale_calc}


# In[136]:

url_SUM_TFRAC_annual = SUM_TFRAC_annual.getThumbUrl(VisPar_TFRAC)
Image(url=url_SUM_TFRAC_annual)


# In[ ]:



