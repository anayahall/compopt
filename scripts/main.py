
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

print("s **** scenario: food waste under 25 percent diversion goals")
x3 = SolveModel(scenario = "food25_nl", feedstock = "food",  
	diversion_rate = 0.25, landfill_ef = 0)

print("s **** scenario: food waste under 50 percent diversion goals")
x2 = SolveModel(scenario = "food50_nl", feedstock = "food", 
	diversion_rate = 0.5, landfill_ef = 0)

print("-------------------------------------")

print("s **** scenario: food waste under 75 percent diversion goals")
x3 = SolveModel(scenario = "food75_nl", feedstock = "food",  
	diversion_rate = 0.75, landfill_ef = 0)

print("-------------------------------------")
print("s **** scenario: ALL food waste")
x1 = SolveModel(scenario = "food_100_nl", feedstock = "food", landfill_ef = 0)


print("s **** scenarrio: Food and green waste")
x0 = SolveModel(scenario = "food_and_green", feedstock = "food_and_green", landfill_ef = 0)

raise Exception(" load function and run set of scenarios")


print("-------------------------------------")

print("next scenario: food waste ignoring facillity capacity limitations")
x4 = SolveModel(scenario = "food_nocap", feedstock = "food", ignore_capacity = True)

print("-------------------------------------")

print("next scenario: food & green waste ignoring facillity capacity limitations")
x5 = SolveModel(scenario = "fg_nocap", feedstock = "food_and_green", ignore_capacity = True)


print("-------------------------------------")
print("-------------------------------------")

# x5 = SolveModel(scenario = "EVswcv", kilometres_to_emissions = 0.1)

# also need to do sensitivitys, for these just need the main results I think, not full df?
print("STARTING SENSTIVITY RUNS")
s1 = SolveModel(scenario = "S_low", feedstock = "food_and_green", 
		seq_f = -56)

s2 = SolveModel(scenario = "S_high", feedstock = "food_and_green", 
		seq_f = -160)

