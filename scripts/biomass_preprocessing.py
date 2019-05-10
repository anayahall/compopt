# Script to clean pre-process BIOMASS INVENTORY and make spatial

####################################################################
# First, load packages
import pandas as pd
import os
import geopandas as gpd
from fxns import epsg_meters

def MergeInventoryAndCounty(gross_inventory, technical_inventory, county_shapefile, fips_data):
    """
        Cleans biomass inventory data and merges with county shapefiles
        gross_inventory      - gross estimate of biomass inventory
        technical_inventory  - technical estimate of biomass inventory
        county_shapefile     - shapefile of county polygons

        Returns: cleaned, spatial biomass data (assigned to county centroids)
    """

    ##################################################################
    #read in biomass inventory
    # GROSS inventory
    gbm = pd.read_csv(gross_inventory)

    # TECHNICAL inventory
    tbm = pd.read_csv(technical_inventory)


    gbm.rename(columns={"biomass.feedstock":"feedstock",
                          'biomass.category':'category',
                          'disposal.yields':'disposal_BDT'}, 
                 inplace=True)

    tbm.rename(columns={"biomass.feedstock":"feedstock",
                          'biomass.category':'category',
                          'disposal.yields':'disposal_BDT'}, 
                 inplace=True)    


    # check that all counties in there
    assert len(gbm.COUNTY.unique())==59
    #yup, plus one "other"

    # gbm[gbm['disposal.yields'] == gbm['disposal.yields'].max()]

    # #look at just manure (if feedstock, needs to be capitalized), if category, lower case -- should be equivalent!
    # gbm[(gbm['biomass.feedstock'] == "MANURE") & (gbm['year'] == 2014)].head()

    # #start grouping by: biomass category
    # gbm.groupby(['biomass.category'])['disposal.yields'].sum()
    # gbm[gbm['biomass.category'] == "manure"].groupby(['COUNTY'])['disposal.yields'].sum().head()

    fw_mc = 0.7
    gw_mc = 0.5
    manure_mc = 0.85

    def bdt_to_wettons(df):
        df['wettons'] = 0.0
        n = len(df.index)
        for i in range(n):
            if df.feedstock[i] == "FOOD":
                df.at[i, 'wettons'] = df.disposal_BDT[i] * (1 + fw_mc)
            if df.feedstock[i] == "GREEN":
                df.at[i, 'wettons'] = df.disposal_BDT[i] * (1 + gw_mc)
            if df.feedstock[i] == "MANURE":
                df.at[i, 'wettons'] = df.disposal_BDT[i] * (1 + manure_mc)

    bdt_to_wettons(gbm)
    bdt_to_wettons(tbm)

    # turn from wet tons to wet m3
    gbm['disposal_wm3'] = gbm['wettons'] / (1.30795*(1/2.24))
    tbm['disposal_wm3'] = tbm['wettons'] / (1.30795*(1/2.24))


    # # now load SHAPEFILE for all CA COUNTIES to merge this
    # print("p Read in CA COUNTIES shapefile and reproject")
    CA = gpd.read_file(county_shapefile)
    CA= CA.to_crs(epsg=4326)
    # CA.head()

    # Create new geoseries of county centroids - 
    # note, technically still a panda series until 'set_geomtry()' is called
    CA['county_centroid'] = CA['geometry'].centroid
    # CA.tail()


    # both set geometry (see above) and plot to check it looks right
    CA.set_geometry('county_centroid')


    # CREATE FIPS ID to merge with county names
    CA['FIPS']=CA['STATEFP'].astype(str)+CA['COUNTYFP']

    # get rid of leading zero
    CA.FIPS = [s.lstrip("0") for s in CA.FIPS]

    #convert to integer for merging below
    CA.FIPS = [int(i) for i in CA.FIPS]
    #print(CA.head())


    # NEED TO BRING IN COUNTY NAMES TO MERGE WITH BIOMASS DATA
    countyIDs = pd.read_csv(fips_data, names = ["FIPS", "COUNTY", "State"])
    #print(countyIDs)

    #print(type(countyIDs.FIPS[0]))
    #print(type(CA.FIPS[0]))

    CAshape = pd.merge(CA, countyIDs, on = 'FIPS')

    # Create subset of just county centroid points NOT POLYGONS
    CAshape.head()

    CA_pts = CAshape.set_geometry('county_centroid')[['county_centroid','FIPS', 'COUNTY', 'ALAND', 'AWATER']]

    # now can merge with biomass data finally!!!
    #print(gbm.columns)
    print("merging biomass data with CA shapefile county centroids")

    #POLYGONS - mostly for plotting?
    # gbm_shp = pd.merge(CAshape, gbm, on = 'COUNTY')
    # # Do same for technical biomass
    # tbm_shp = pd.merge(CAshape, tbm, on = 'COUNTY')


    # COUNTY CENTROIDS
    gbm_pts = pd.merge(CA_pts, gbm, on = 'COUNTY')
    tbm_pts = pd.merge(CA_pts, tbm, on = 'COUNTY')

    print("p BIOMASS PRE_PROCESSING DONE RUNNING")

    return gbm_pts, tbm_pts
