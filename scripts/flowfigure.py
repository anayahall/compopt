## flowfigure.py

# map flow of material from urban centers to facilities and then facilities to rangelands
# import model output for a few scenarios
# plot!

# import modules
import pandas as pd
import numpy as np
import shapely as shp
import geopandas as gpd
from os.path import join as opj
import matplotlib.pyplot as plt
import os
import pickle


# suppress warnings in jupyter notebook!
import warnings
warnings.simplefilter('ignore')

def Fetch(df, key_col, key, value):
    #counties['disposal'].loc[counties['COUNTY']=='San Diego'].values[0]
    return df[value].loc[df[key_col]==key].values[0]

# set data path
DATA_DIR = "/Users/anayahall/projects/compopt/data"

# read in data
# rangeland polygons
rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
# county polygons
county_shape = gpd.read_file(opj(DATA_DIR, "raw/CA_Counties/CA_Counties_TIGER2016.shp")) # OLD- raw shape
counties_popcen = pd.read_csv(opj(DATA_DIR, "counties/CenPop2010_Mean_CO06.txt")) # NEW - population weighted means!
counties_popcen.rename(columns = {'LATITUDE': 'lat', 'LONGITUDE': 'lon', 'COUNAME': 'NAME'}, inplace=True)

county_shape = county_shape.to_crs(epsg=4326)
county_shape['county_centroid'] = county_shape['geometry'].centroid


# solid waste inventory data (CLEANED)
swis =  gpd.read_file(opj(DATA_DIR, "clean/clean_swis.shp"))


# Minimize geodataframe to dataframe with just fields of interest
swis_df = swis[['SwisNo', 'Name', 'Latitude', 'Longitude', 'cap_m3', 'AcceptedWa']]

# rename lat and lon for easier plotting
swis_df.rename(columns = {'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)

# may just want foodwaste for adding to the plot
foodwaste_facilities = swis_df[swis_df['AcceptedWa'].str.contains("Food", na=False)]


##### FLAG - generate random data--- need to load real matrix of quantities here!!!
testmatrix = np.random.randint(100, size=(58, 109))
c2fmatrix = testmatrix


## LOAD REAL DATA HERE!!!! 
# with open('../c2f_test.p', 'rb') as f:
#     c2f_test = pickle.load(f) 
# c2f_test


fig, ax = plt.subplots(figsize = (10,10))
county_shape.plot(ax = ax, color = "white", linewidth=0.3, edgecolor = "grey")
ax.plot(swis_df['lon'], swis_df['lat'], 'x')
for i in range(len(county_shape)):
    lon, lat = county_shape['county_centroid'][i].xy
    ax.plot(lon, lat, c= 'lightgrey', marker='+')
for c_i,c in enumerate(counties_popcen):     
    c_lon = counties_popcen['lon'].iloc[counties_popcen.index == c_i].values[0]
    c_lat = counties_popcen['lat'].iloc[counties_popcen.index == c_i].values[0]
    for f_j,f in enumerate(swis):
        f_lon = swis_df['lon'].iloc[swis_df.index == f_j].values[0]
        f_lat = swis_df['lat'].iloc[swis_df.index == f_j].values[0]
        ## need to check connectivity matrix here
        q = c2fmatrix[c_i, f_j]
        if 0<q<25:
            ax.plot([c_lon, f_lon], [c_lat, f_lat], 'k-', alpha = 0.5, linewidth=(0.2))
        elif q<50:    
            ax.plot([c_lon, f_lon], [c_lat, f_lat], 'k-', alpha = 0.5, linewidth=(0.5))
        elif q<100:
            ax.plot([c_lon, f_lon], [c_lat, f_lat], 'k-', alpha = 0.5, linewidth=(1))
plt.show()


