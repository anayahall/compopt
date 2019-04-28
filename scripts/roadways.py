
# coding: utf-8

# In[5]:

# transport networks
# network x tutorial: https://www.datacamp.com/community/tutorials/networkx-python-graph-tutorial
# reading fgdbs: https://gis.stackexchange.com/questions/32762/how-to-access-feature-classes-in-file-geodatabases-with-python-and-gdal

# load packages
import geopandas as gpd
import fiona 
import os
#create a list of layers with in a file geodatabase 


# In[8]:

# import geodatabase files?
os.chdir("/Users/anayahall/projects/grapevine")


fgdb = 'data/roadways/District 4/District_4.gdb'

# layerlist = fiona.listlayers(fgdb)
# print(layerlist)
# for i in sorted(layerlist):
#     df1 = gpd.read_file(fgdb,layer=i)


type(fgdb)


# In[ ]:

# 

