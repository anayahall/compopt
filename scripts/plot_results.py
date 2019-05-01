import pandas as pd
import os
import numpy as np
import shapely as sp
from os.path import join as opj


import matplotlib.pyplot as plt
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import json


DATA_DIR = "/Users/anayahall/projects/compopt/results"

# load transit distances
with open("c2f.json", "r") as read_file:
    c2f_dist2 = json.load(read_file)

# this using the dissolved set of rangelands
with open("f2r_dissolve_dist.json", "r") as read_file:
    f2r_dist = json.load(read_file)

#might want facility shapefile for bubble by intake?
facilities = gpd.read_file(opj(DATA_DIR, "../data/clean/clean_swis.shp"))
# facilities = facilities.to_crs(epsg=4326)
facilities = facilities[['SwisNo', 'County', 'geometry', 'cap_m3']]


#CA if needed
# CA = gpd.read_file("../data/raw/CA_Counties/CA_Counties_TIGER2016.shp")

countyoutput = (opj(DATA_DIR, "food_50d_CountyOutput.csv"))
facintake = opj(DATA_DIR, "food_50d_FacIntake.csv")
landapp = opj(DATA_DIR, "food_50d_LandApp.csv")

output = pd.read_csv(countyoutput, 
	names = ['County', 'output'],
	header = 0)
intake_swis = pd.read_csv(facintake)
land = pd.read_csv(landapp, 
	names = ['OBJECTID', 'land_area', 'volume_applied'],
	header = 0)


# rangeland_app = land.to_dict()



raise Exception("belh")




intake = pd.merge(intake_swis, facilities, on = 'SwisNo')

# data = pd.merge(output, land, on = 'County')
# data = pd.merge(data, intake, on = 'County') # note that geometry is facility location!

# calculate cost by county
costs = {}

raise Exception("belh")

for county in data['County']:
        costs[county] = {}
        print(county)
        temp = 0
        for facility in data['SwisNo']:
            print(facility)
            dist = c2f_dist[county][facility]['trans_dist']
            print(dist)
            temp += data['output']*dist*2
#             temp += x['quantity'].value*x['trans_cost']
#         cost_by_county[county]['cost'] = int(round(temp))

#     for facility in facilities['SwisNo']:
#         for rangeland in rangelands['COUNTY']:
#             x = f2r[facility][rangeland]
#             applied_amount = x['quantity'].value
#             # emissions due to transport of compost from facility to rangelands
#             cost += x['trans_cost']* applied_amount
#             # emissions due to application of compost by manure spreader
#             cost += spreader_cost * applied_amount



# general structure

# cost = [q1]*trans_cost_c + [q2]*(trans_cost_h+apply_cost)



