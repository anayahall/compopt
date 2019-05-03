import pandas as pd
import os
import numpy as np
import shapely as sp
from os.path import join as opj


import matplotlib.pyplot as plt
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import json


DATA_DIR = "/Users/anayahall/projects/compopt/data"
OUT_DIR = "/Users/anayahall/projects/compopt/maps"

# read in data
CA = gpd.read_file(opj(DATA_DIR, "raw/CA_Counties/CA_Counties_TIGER2016.shp"))
CA = CA.to_crs(epsg=4326)

rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
# rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/grazingland_dis/CA_grazingland.shp"))
rangelands = rangelands.to_crs(epsg=4326)

# first plot
f, ax = plt.subplots()
CA.plot(ax = ax, color = "white", figsize = (10,10), linewidth=0.1, edgecolor = "grey")
rangelands.plot(ax= ax, color = "green", alpha = .5)
ax.axis('off')
ax.set_title('Grazing Land', fontdict={'fontsize': '12', 'fontweight' : '3'})
plt.savefig(opj(OUT_DIR, "rangelands.png"), dpi=300)

facilities = gpd.read_file(opj(DATA_DIR, "clean/clean_swis.shp"))
facilities.rename(columns={'County':'COUNTY'}, inplace=True)
# facilities = facilities.to_crs(epsg=4326)


# attempting to label CA polygons
# CA['coords'] = CA['geometry'].apply(lambda x: x.representative_point().coords[:])
# CA['coords'] = [coords[0] for coords in CA['coords']]

# # second plot
# f, ax = plt.subplots()
# CA.plot()
# for idx, row in CA.iterrows():
#     plt.annotate(s=row['NAME'], xy=row['coords'],
#                  horizontalalignment='center')
# plt.savefig(opj(OUT_DIR, "CA_Counties.png"), dpi=900)

def PlotCountyLevel(variable, cmap, title):
    print("THIS IS UTTER POOP")
    return