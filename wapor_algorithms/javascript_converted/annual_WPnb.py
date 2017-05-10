
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
region_json = [[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0], [-25.0, -37.0]]


# In[3]:

agbp_year_coll = ee.ImageCollection.fromImages([
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2010'),
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2011'),
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2012'),
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2013'),
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2014'),
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2015'),
  ee.Image('projects/fao-wapor/AGBP_Annual/AGBP-2016')]
  )
 
t_year_coll = ee.ImageCollection.fromImages([
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2010'),
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2011'),
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2012'),
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2013'),
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2014'),
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2015'),
  ee.Image('projects/fao-wapor/T_Annual/T_Annual-2016')]
)


# In[5]:

# ******** Insert Year ******
year = 2016;
# ******** Insert Year ******
start_str = str(year) + '-1-1'
end_str = str(year) + '-12-31'
print(start_str, end_str)

# Set filter variables.
start = ee.Date(start_str)
end = ee.Date(end_str)


# # OLD Method rewritten below

# In[12]:

AGBPy = ee.Image("projects/fao-wapor/AGBP_Annual/AGBP-" + str(year))
Ty = ee.Image("projects/fao-wapor/T_Annual/T_Annual-" + str(year))

# Or, as you will already have calculated AET annual and AGBP annual:
# AGBPy/(AETy*10) where *10 is to convert mm into m³/ha 
# var WPnb = AGBPy.divide(Ty.multiply(10));
def T_moreThan100(image): 
    return image.mask(image.select('b1_sum').gte(100))

t_year_coll_mt100 = t_year_coll.map(T_moreThan100)
first_t_masked = ee.Image(t_year_coll_mt100.first())

# /********* ORIGINAL MATH ***********/
# var WPnb = AGBPy.divide(Ty.multiply(10));
agbp_2010 = ee.Image(agbp_year_coll.first())
t_masked_gt100 = ee.Image(t_year_coll_mt100.first())
WPnb = agbp_2010.divide(t_masked_gt100.multiply(10))


# In[13]:
# Get scale (in meters) information from first image 
scale_calc = WPnb.projection().nominalScale().getInfo()
print('Image scale: ', scale_calc)


# In[14]:

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


# In[42]:

url_WPnb_annual = WPnb.getThumbUrl(VisPar_WPbm)
Image(url=url_WPnb_annual)


# # JOINING and Merging Final Method

# In[95]:

# JOINING agbp and t annual - Start
Join = ee.Join.inner()
FilterOnStartTime = ee.Filter.equals(
                       leftField = 'system:time_start', 
                       rightField = 'system:time_start'
                       )
AGBP_T_collection_Join = ee.ImageCollection(
                            Join.apply(agbp_year_coll, 
                                       t_year_coll_mt100,
                                       FilterOnStartTime))
print("Joined collections",AGBP_T_collection_Join)
# JOINING TWO Collections - End


# In[98]:

# MERGING JOINED agbp and t annual - Start
def MergeBands(element):
  return ee.Image.cat(element.get('primary'), element.get('secondary'));

agbp_t_coll_merged = AGBP_T_collection_Join.map(MergeBands)
print("Merged Joined collections",agbp_t_coll_merged);
# MERGING JOINED TWO Collections - End


# In[99]:

# /********* WPnb ****************/
def AGBP_T(image):  
  wp_nb = image.select('b1_sum').divide(image.select('b1_sum_1').multiply(10));
  return ee.Image(wp_nb)

WPnb_coll = agbp_t_coll_merged.map(AGBP_T)
print("WPnb_coll",WPnb_coll);


# ## Testing

# In[115]:

# TESTING Image metadata and properties - start
first_immage_of_join = ee.Image(WPnb_coll.first())
print("First: ",first_immage_of_join.getInfo())

properties = ee.List(first_immage_of_join.propertyNames())
print("Metadata properties of First: ", properties.getInfo())

collection = WPnb_coll.sort('system:time_start', False)
keys = WPnb_coll.aggregate_array('system:index').getInfo()
print(keys)

url_img_annual = first_immage_of_join.getThumbUrl(VisPar_WPbm)
print(url_img_annual)
Image(url=url_img_annual)

#for i in range(len(keys)):
#    id = keys[i]
#    img = ee.Image(id)  
#    print ee.String(img)


# In[119]:

# img_filter = ee.Image(collection.filter(ee.Filter.eq('system:index','0_0')))
img_filterMetadata = ee.Image(collection.filterMetadata("system:index", "equals", '0_0').first())

#.filterMetadata('system:index', 'not_less_than', accumStartDate)
#.filterMetadata('system:index', 'not_greater_than', accumEndDate);
#.filterMetadata('month', 'equals', month)
# print(type(img_filter))
# print(type(img_filterMetadata))

url_img_annual = img_filterMetadata.getThumbUrl(VisPar_WPbm)
print(url_img_annual)
Image(url=url_img_annual)


# In[120]:

sql = 'SELECT ST_METADATA(rast) from "projects/fao-wapor/AGBP_Annual/AGBP-2016"'
q = SQL2GEE(sql)
q.response


# In[ ]:



