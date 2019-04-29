import pandas as pd
import os
import numpy as np
import shapely as sp

import matplotlib.pyplot as plt
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
# only for jupyter nb to show plots inline
get_ipython().magic('matplotlib inline')

#set wd
os.chdir("/Users/anayahall/projects/grapevine")
CA_proj = gpd.read_file("data/raw/CA_Counties/CA_Counties_TIGER2016.shp")
#load rangeland results - fw75
