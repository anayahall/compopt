
import cvxpy as cp
import numpy as np
import os
from os.path import join as opj

import pandas as pd
import shapely as shp
import geopandas as gpd
import scipy as sp
import pickle

from compostLP import Haversine, Distance, Fetch, SolveModel, SaveModelVars

# state, county_results = SolveModel(scenario = "FG_test")

# state, county_results = SolveModel(scenario = 'fg_75', disposal_rate = 0.75)


# print("HALF DISPOSAL*********************************")
# s2 = SolveModel(scenario = "S_high", feedstock = "food_and_green", 
# 	disposal_rate = 0.5, seq_f = -357)

c2f_val, f2r_val, land_app = SolveModel(disposal_rate = 0.50) 

# save all of these

with open('c2f_quant_50.p', 'wb') as f:
        pickle.dump(c2f_val, f)

with open('f2r_quant_50.p', 'wb') as f:
        pickle.dump(f2r_val, f)

with open('land_app_quant_50.p', 'wb') as f:
        pickle.dump(land_app, f)

# then plot the first two with flow figure

# for land app- need to merge with rangeland gdf
# set data path
DATA_DIR = "/Users/anayahall/projects/compopt/data"

# read in data
# rangeland polygons
rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
# county polygons

# first turn into df
land_df = pd.DataFrame.from_dict(land_app, orient = 'index')
# need to get OBJECTID as str before merge
rangelands.OBJECTID = rangelands.OBJECTID.astype(str)
# merge land_app with rangeland geodataframe 
rangelands_app = pd.merge(rangelands, land_df, on = 'OBJECTID')

rangelands_app.to_file("rangelands_app_75.shp")

raise Exception(" loaded function, ran scenario, prepped for plotting!!!")

s1 = SolveModel(scenario = "S_high", feedstock = "food_and_green", 
		seq_f = -357)
print("DOUBLE CAPACITY****************************")
s3 = SolveModel(scenario = "Cap_high", feedstock = "food_and_green", 
		capacity_multiplier = 2, seq_f = -357)

print("-------------------------------------")

print("s **** scenario: food waste under 25 disposal rate ")
t1 = SolveModel(scenario = "food_25d", feedstock = "food",  
	disposal_rate = 0.25)	

print("s **** scenario: food waste under 50 percent disposal rate")
t2 = SolveModel(scenario = "food_50d", feedstock = "food", 
	disposal_rate = 0.5)

print("-------------------------------------")

print("s **** scenario: food waste under 75 percent disposal rate")
t3 = SolveModel(scenario = "food_75d", feedstock = "food",  
	disposal_rate = 0.75)


print("-------------------------------------")
print("s **** scenario:  food waste")
t4 = SolveModel(scenario = "food_100d", feedstock = "food")

# raise Exception(" load function and run set of scenarios")


print("s **** scenario:  food waste, 20 percent recovered")
t5 = SolveModel(scenario = "food_20r", feedstock = "food", 
	fw_reduction = 0.2)
# print("-------------------------------------")
# print("-------------------------------------")
# print("-------------------------------------")

# print("s **** scenarrio: Food and green waste with 20 percent fw reduction")
# p0state, p0county, p0c2fval, p0f2rval = SolveModel(scenario = "fg_20r", feedstock = "food_and_green", 
# 	fw_reduction = 0.2)



# print("s ******* scenario: food and green waste at 25 percent disposal")
# p1state, p1county, p1c2fval, p1f2rval = SolveModel(scenario = "fg_25d", feedstock = "food_and_green", 
# 	disposal_rate= .25)

# print("s ******* scenario: food and green waste at 50 percent disposal")
# p2state, p2county, p2c2fval, p2f2rval = SolveModel(scenario = "fg_50d", feedstock = "food_and_green", 
# 	disposal_rate= .5)


# print("s ******* scenario: food and green waste at 75 percent disposal")
# p3state, p3county, p3c2fval, p3f2rval = SolveModel(scenario = "fg_75d", feedstock = "food_and_green", 
# 	disposal_rate= .75)

# print("s ******* scenario: food and green waste")
# p4state, p4county, p4c2fval, p4f2rval = SolveModel(scenario = "fg", feedstock = "food_and_green")


# raise Exception(" load function and run set of scenarios")


print("-------------------------------------")

# print("next scenario: food waste ignoring facillity capacity limitations")
# x4 = SolveModel(scenario = "food_nocap", feedstock = "food", ignore_capacity = True)

# print("-------------------------------------")

# print("next scenario: food & green waste ignoring facillity capacity limitations")
# x5 = SolveModel(scenario = "fg_nocap", feedstock = "food_and_green", ignore_capacity = True)


print("-------------------------------------")
print("-------------------------------------")

# x5 = SolveModel(scenario = "EVswcv", kilometres_to_emissions = 0.1)

# also need to do sensitivitys, for these just need the main results I think, not full df?
print("STARTING SENSTIVITY RUNS")

# print("s ******* scenario: low landfill")
# s5 = SolveModel(scenario = "no_lf", feedstock = "food_and_green", disposal_rate =.5,
# 		landfill_ef = 0 )


# print("s ******* scenario: process emis high")
# s5 = SolveModel(scenario = "P_high", feedstock = "food_and_green", 
# 		process_emis = 16)


s2 = SolveModel(scenario = "t_high", feedstock = "food_and_green", 
		kilometres_to_emissions = 0.69)


s1 = SolveModel(scenario = "S_high", feedstock = "food_and_green", 
		seq_f = -160)

print("s ******* scenario: low cost")
s3 = SolveModel(scenario = "low cost", feedstock = "food_and_green", 
		spreader_cost = 3)




## test capacity limits
print("s ******* scenario: double capacity")
s4 = SolveModel(scenario = "Cap_high", feedstock = "food_and_green", 
		capacity_multiplier = 2)


s6 = SolveModel(scenario = "t_high", feedstock = "food_and_green", 
		c2f_trans_cost = 1.2)
