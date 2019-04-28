
# coding: utf-8

# In[2]:

# Reading in Rasters
# Rasterio tutorial here: 
#https://automating-gis-processes.github.io/CSC18/lessons/L6/reading-raster.html

# First, load packages
import pandas as pd
import os
import fiona
import rasterio

import numpy as np
import shapely as sp
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs

os.chdir("/Users/anayahall/projects/grapevine")

from fxns import epsg_meters


# os.chdir("/Volumes/My Passport/CAland")
rangelands = gpd.read_file("data/raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp")
rangelands.crs

# get area in meters
rangelands["area_km"] = rangelands['geometry'].area/ 10**6


# estimate centroid
rangelands['centroid'] = rangelands['geometry'].centroid


### CONVERT LAND AREA TO VOLUME OF COMPOST CAPACITY (*33.6cuyd/acre)