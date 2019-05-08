# functions.py
from os.path import join as opj

import pandas as pd
import shapely as shp
import geopandas as gpd


# dictionary = testf2r

def plotrangelandapp(dictionary, name):


rappdf = pd.DataFrame.from_dict(dictionary)
# sum application on rangeland by all facilities
rappdf['sum'] = rappdf.sum(axis = 1, skipna = True)*1000

# load files for plotting
CA = gpd.read_file(opj(DATA_DIR, "raw/CA_Counties/CA_Counties_TIGER2016.shp"))
CA = CA.to_crs(epsg=4326)
CA['county_centroid'] = CA['geometry'].centroid

swis =  gpd.read_file(opj(DATA_DIR, "clean/clean_swis.shp"))


# load shapefil for merge
rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
# rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/grazingland_dis/CA_grazingland.shp"))
rangelands = rangelands.to_crs(epsg=4326)
# make column of object ID for merging
rappdf['OBJECTID'] = rappdf.index
# only keep id and summed 
rappdf_min = rappdf[['sum', 'OBJECTID']]


# merge with rangelands
merge = pd.merge(rangelands, rappdf_min, on = "OBJECTID")
# plot
f, ax = plt.subplots()
CA.plot(ax = ax, color = "white", figsize = (10,10), linewidth=0.3, edgecolor = "grey")
# CA.set_geometry('centroid').plot(ax= ax, color = 'black')
swis.plot(ax = ax, marker = '*', color = 'black', alpha=.7, markersize = 10, linewidth=0)
merge.plot(ax= ax, column = merge['sum']**2, cmap = 'Greens', linewidth=0.03, 
	edgecolor = "green", legend = False)
ax.axis('off')
ax.set_title('Rangeland Application', fontdict={'fontsize': '12', 'fontweight' : '3'})
plt.savefig(opj(OUT_DIR, str(name) + "_rangelandapps.png"), dpi=300)
# plt.savefig(opj(OUT_DIR, "fg100_rangelandapps.png"), dpi=300)

	return