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


# GOALS FOR FRIDAY AFTERNOON



# function that takes gdf and plots choropleth maps of a set of variables 
# (facility emissions to plot with EJ ; abatement cost ; quantity out, area applied, etc)



