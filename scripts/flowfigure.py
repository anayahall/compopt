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
rangelands = rangelands.to_crs(epsg=4326)
rangelands['centroid'] = rangelands['geometry'].centroid 
rl_lon, rl_lat = rangelands.centroid.x, rangelands.centroid.y


# county polygons
county_shape = gpd.read_file(opj(DATA_DIR, 
        "raw/CA_Counties/CA_Counties_TIGER2016.shp")) # OLD- raw shape
counties_popcen = pd.read_csv(opj(DATA_DIR, 
        "counties/CenPop2010_Mean_CO06.txt")) # NEW - population weighted means!
counties_popcen.rename(columns = {'LATITUDE': 'lat', 
        'LONGITUDE': 'lon', 'COUNAME': 'COUNTY'}, inplace=True)

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
# testmatrix = np.random.randint(500000, size=(58, 109))
# c2f_dict = testmatrix


## LOAD REAL DATA HERE!!!! 
# will be a dictionary 
with open('c2f_quant.p', 'rb') as f:
    c2f_quant = pickle.load(f) 
c2f_dict = c2f_quant


# with open('../c2f_test.p', 'rb') as f:
#     c2f_test = pickle.load(f) 

dictlist = []
for k, v in c2f_dict.items():
    temp = v
    for l,m in temp.items():
        if m > 11:
            dictlist.append(m)
np.quantile(dictlist, [.05, .25, .5 , .75, .95])
# array([ 55278.1, 130799. , 253441. , 377828.5, 450098.5])

# PLOT
fig, ax = plt.subplots(figsize = (10,10))
county_shape.plot(ax = ax, color = "lightgrey", linewidth=1, edgecolor = "white")
ax.plot(swis_df['lon'], swis_df['lat'], 'kx', markersize = 3, label = 'Compost Facility')
for i in counties_popcen.index:
    county_name = counties_popcen['COUNTY'].iloc[counties_popcen.index == i].values[0]
    c_lon = counties_popcen['lon'].iloc[counties_popcen.index == i].values[0]
    c_lat = counties_popcen['lat'].iloc[counties_popcen.index == i].values[0]
    _ = ax.plot(c_lon, c_lat, c= 'white', marker='+', markersize = 3)
    # print('*************')
    # print(county_name)
    for j in swis_df.index:
        f_no = swis_df['SwisNo'].iloc[swis_df.index == j].values[0]
        f_lon = swis_df['lon'].loc[swis_df.index == j].values[0]
        f_lat = swis_df['lat'].loc[swis_df.index == j].values[0]
        # THIS IS HOW REAL DATA WILL BE FORMATTED - AS DICT
        q = c2f_dict[county_name][f_no]
        # print(q)
        # q = c2f_dict.loc[c2f_dict.index == f_no, county_name].values[0]
        # q = c2f_dict[i, j] # USE THIS FOR TEST MATRIX ONLY
        if q > 1000000:
            _ = ax.plot([c_lon, f_lon], [c_lat, f_lat], 'm-', alpha = 0.6, linewidth=5.5)
        elif q > 200000:
            _ = ax.plot([c_lon, f_lon], [c_lat, f_lat], 'm-', alpha = 0.6, linewidth=3.5)
        elif q > 50000:
            _ = ax.plot([c_lon, f_lon], [c_lat, f_lat], 'm-', alpha = 0.6, linewidth=2.5)
        elif q > 20000:
            _ = ax.plot([c_lon, f_lon], [c_lat, f_lat], 'm-', alpha = 0.6, linewidth=1.5)
        elif q > 2000: 
            _ = ax.plot([c_lon, f_lon], [c_lat, f_lat], 'm-', alpha = 0.6, linewidth=0.75)
        elif q > 200: 
            _ = ax.plot([c_lon, f_lon], [c_lat, f_lat], 'm-', alpha = 0.6, linewidth=0.5)

# plot plot plot
# plot

ax.plot([], [], '+', color = 'darkgrey', markersize = 3, label = 'County Centroid')
ax.plot([], [], 'm-', alpha = 0.6, linewidth=2.5, label = 'Flow')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title("Feedstock Flow from County Centroid to Compost Facility")
ax.legend()
fig.savefig('Maps/C2Fflow_100.png')       
plt.show()

#################################################################################
# NOW REDO for F2R?


## LOAD REAL DATA HERE!!!! 
# will be a dictionary 
with open('f2r_quant.p', 'rb') as f:
    f2r_quant = pickle.load(f)


f2r_dict = f2r_quant

dictlist = []
for k, v in f2r_dict.items():
    temp = v
    for l,m in temp.items():
        if m > 10:
            dictlist.append(m)

np.quantile(dictlist, [.05, .25, .5 , .75, .95])
# array([  1317.2 ,   9618.5 ,  26591.  ,  63611.  , 140616.85])


# PLOT
fig, ax = plt.subplots(figsize = (10,10))
county_shape.plot(ax = ax, color = "lightgrey", linewidth=1, edgecolor = "white")
ax.plot(swis_df['lon'], swis_df['lat'], 'kx', markersize = 3, label = 'Compost Facility')
for j in swis_df.index:
    f_no = swis_df['SwisNo'].iloc[swis_df.index == j].values[0]
    f_lon = swis_df['lon'].iloc[swis_df.index == j].values[0]
    f_lat = swis_df['lat'].iloc[swis_df.index == j].values[0]
    # print('*************')
    # print(f_no)
    for r in rangelands.index:
        r_no = rangelands['OBJECTID'].iloc[rangelands.index == r].values[0]
        r_lon = rl_lon.loc[rl_lon.index == r].values[0]
        r_lat = rl_lat.loc[rl_lat.index == r].values[0]        # THIS IS HOW REAL DATA WILL BE FORMATTED - AS DICT
        if r_no in f2r_dict[f_no].keys():
            q = f2r_dict[f_no][r_no]
            # print(q)
        # q = c2fmatrix.loc[c2fmatrix.index == f_no, county_name].values[0]
        # q = c2fmatrix[i, j] # USE THIS FOR TEST MATRIX ONLY
            if q > 100000:
                _ = ax.plot([f_lon, r_lon], [f_lat, r_lat], 'c-', alpha = 0.6, linewidth=5.5)
            elif q > 600000:
                _ = ax.plot([f_lon, r_lon], [f_lat, r_lat], 'c-', alpha = 0.6, linewidth=3.5)
            elif q > 25000:
                _ = ax.plot([f_lon, r_lon], [f_lat, r_lat], 'c-', alpha = 0.6, linewidth=2.5)
            elif q > 10000:
                _ = ax.plot([f_lon, r_lon], [f_lat, r_lat], 'c-', alpha = 0.6, linewidth=1.5)
            elif q > 2000: 
                _ = ax.plot([f_lon, r_lon], [f_lat, r_lat], 'c-', alpha = 0.6, linewidth=0.75)
            elif q > 200: 
                _ = ax.plot([f_lon, r_lon], [f_lat, r_lat], 'c-', alpha = 0.6, linewidth=0.5)

# plot plot plot
# plot
# ax.plot([], [], '+', color = 'darkgrey', markersize = 3, label = 'County Centroid')
ax.plot([], [], 'm-', alpha = 0.6, linewidth=2.5, label = 'Flow')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title("Feedstock Flow from Facility to rangeland Facility")
ax.legend()
# fig.savefig('Maps/C2Fflow_100.png')       
plt.show()

