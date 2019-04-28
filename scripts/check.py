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

# ej = gpd.read_file(opj(DATA_DIR, 
    # "/calenviroscreen/CESJune2018Update_SHP/CES3June2018Update.shp")

# tbm = gpd.read_file(opj(DATA_DIR, "clean/techbiomass_pts.shp"))

# tbm.rename(columns={"biomass.fe":"feedstock",
#                           'biomass.ca':'category',
#                           'disposal.y':'disposal'}, 
#                  inplace=True)   

# fw_mc = 0.7
# gw_mc = 0.5
# manure_mc = 0.85

# def bdt_to_wettons(df):
#     df['wettons'] = 0.0
#     n = len(df.index)
#     for i in range(n):
#         if df.feedstock[i] == "FOOD":
#             df.at[i, 'wettons'] = df.disposal_BDT[i] * (1 + fw_mc)
#         if df.feedstock[i] == "GREEN":
#             df.at[i, 'wettons'] = df.disposal_BDT[i] * (1 + gw_mc)
#         if df.feedstock[i] == "MANURE":
#             df.at[i, 'wettons'] = df.disposal_BDT[i] * (1 + manure_mc)

# bdt_to_wettons(gbm)
# bdt_to_wettons(tbm)

# # turn from wet tons to wet m3
# gbm['disposal_wm3'] = gbm['wettons'] / (1.30795*(1/2.24))
# tbm['disposal_wm3'] = tbm['wettons'] / (1.30795*(1/2.24))

# rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
# rangelands = rangelands.to_crs(epsg=4326) # make sure this is read in degrees (WGS84)


gbm_pts, tbm_pts = MergeInventoryAndCounty(
    gross_inventory     = opj(DATA_DIR, "raw/biomass.inventory.csv"),
    technical_inventory = opj(DATA_DIR, "raw/biomass.inventory.technical.csv"),
    county_shapefile    = opj(DATA_DIR, "raw/CA_Counties/CA_Counties_TIGER2016.shp"),
    fips_data           = opj(DATA_DIR, "interim/CA_FIPS.csv")
)

# # mini gdfs of county wastes (tbm - location and MSW for 2014) 
# # counties = gpd.read_file(opj(DATA_DIR, "clean/techbiomass_pts.shp"))
# # counties = counties.to_crs(epsg=4326)
counties = tbm_pts # could change to GBM


counties = counties[((counties['feedstock'] == "FOOD") | 
    (counties['feedstock'] == "GREEN") | (counties['feedstock'] == "MANURE")) & 
    (counties['year'] == 2014)].copy()




# if counties.feedstock == "FOOD": 
#     counties.disposal == x*counties.disposal

# mask = df.my_channel > 20000
mask = counties.feedstock == "FOOD"
# column_name = 'my_channel'
column_name = 'disposal'
# df.loc[mask, column_name] = 0
counties.loc[mask, column_name] = x*counties.loc[mask,column_name]


counties['disposal'] = counties.groupby(['COUNTY'])['disposal_wm3'].transform('sum')
# collapse counties
counties = counties.drop_duplicates(subset = 'COUNTY')



