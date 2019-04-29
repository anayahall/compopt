
import cvxpy as cp
import numpy as np
import os
from os.path import join as opj

import pandas as pd
import shapely as shp
import geopandas as gpd
import scipy as sp

from compostLP import Haversine, Distance, Fetch, SolveModel


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



print("s **** scenario:  food waste, 20 percent recovered")
t5 = SolveModel(scenario = "food_20r", feedstock = "food", 
	fw_reduction = 0.2)
print("-------------------------------------")
print("-------------------------------------")
print("-------------------------------------")

print("s **** scenarrio: Food and green waste with 20 percent fw reduction")
p0 = SolveModel(scenario = "fg_20r", feedstock = "food_and_green", 
	fw_reduction = 0.2)

print("s ******* scenario: food and green waste")
p1 = SolveModel(scenario = "fg", feedstock = "food_and_green")

print("s ******* scenario: food and green waste at 50 percent disposal")
p2 = SolveModel(scenario = "fg_50d", feedstock = "food_and_green", 
	disposal_rate= .5)

print("s ******* scenario: food and green waste at 25 percent disposal")
p3 = SolveModel(scenario = "fg_25d", feedstock = "food_and_green", 
	disposal_rate= .25)


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


s2 = SolveModel(scenario = "t_high", feedstock = "food_and_green", 
		kilometres_to_emissions = 0.69)


s1 = SolveModel(scenario = "S_high", feedstock = "food_and_green", 
		seq_f = -160)

print("s ******* scenario: low cost")
s3 = SolveModel(scenario = "low cost", feedstock = "food_and_green", 
		spreader_cost = 3)


print("s ******* scenario: process emis high")
s4 = SolveModel(scenario = "P_high", feedstock = "food_and_green", 
		process_emis = -16)

## test capacity limits
print("s ******* scenario: double capacity")
s4 = SolveModel(scenario = "Cap_high", feedstock = "food_and_green", 
		capacity_multiplier = 2)


