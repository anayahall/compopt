#checking gross v tech biomass
# First, load packages
import pandas as pd
import os
from os.path import join as opj
import numpy as np
import fiona
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import plotly.plotly as py

from biomass_preprocessing import MergeInventoryAndCounty

#change wd
DATA_DIR = "/Users/anayahall/projects/grapevine/data"

# from fxns import epsg_meters
##################################################################
# tbm = pd.read_csv("data/raw/biomass.inventory.technical.csv")

ej = gpd.read_file(opj(DATA_DIR, 
    "/calenviroscreen/CESJune2018Update_SHP/CES3June2018Update.shp")



for k,v in 


