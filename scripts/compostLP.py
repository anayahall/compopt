## testOP.py

import cvxpy as cp
import numpy as np
import os
import datetime
from os.path import join as opj

import pandas as pd
import shapely as shp
import geopandas as gpd
import scipy as sp

from biomass_preprocessing import MergeInventoryAndCounty
#from swis_preprocessing import LoadAndCleanSWIS #TODO

DATA_DIR = "/Users/anayahall/projects/compopt/data"


############################################################
# FUNCTIONS USED IN THIS SCRIPT

def Haversine(lat1, lon1, lat2, lon2):
  """
  Calculate the Great Circle distance on Earth between two latitude-longitude
  points
  :param lat1 Latitude of Point 1 in degrees
  :param lon1 Longtiude of Point 1 in degrees
  :param lat2 Latitude of Point 2 in degrees
  :param lon2 Longtiude of Point 2 in degrees
  :returns Distance between the two points in kilometres
  """
  Rearth = 6371
  lat1   = np.radians(lat1)
  lon1   = np.radians(lon1)
  lat2   = np.radians(lat2)
  lon2   = np.radians(lon2)
  #Haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
  c = 2 * np.arcsin(np.sqrt(a)) 
  return Rearth*c


def Distance(loc1, loc2):
    # print(loc1.x, loc1.y, loc2.x, loc2.y)
    return Haversine(loc1.y, loc1.x, loc2.y, loc2.x)


def Fetch(df, key_col, key, value):
    #counties['disposal'].loc[counties['COUNTY']=='San Diego'].values[0]
    return df[value].loc[df[key_col]==key].values[0]

############################################################

# bring in biomass data
gbm_pts, tbm_pts = MergeInventoryAndCounty(
    gross_inventory     = opj(DATA_DIR, "raw/biomass.inventory.csv"),
    technical_inventory = opj(DATA_DIR, "raw/biomass.inventory.technical.csv"),
    county_shapefile    = opj(DATA_DIR, "raw/CA_Counties/CA_Counties_TIGER2016.shp"),
    fips_data           = opj(DATA_DIR, "interim/CA_FIPS.csv")
)

# mini gdfs of county wastes (tbm - location and MSW for 2014) 
# counties = gpd.read_file(opj(DATA_DIR, "clean/techbiomass_pts.shp"))
# counties = counties.to_crs(epsg=4326)
counties = tbm_pts # could change to GBM

# filter by YEAR up here, then refine by  feedstock inside the function
counties = counties[((counties['feedstock'] == "FOOD") | 
    (counties['feedstock'] == "GREEN") | (counties['feedstock'] == "MANURE")) & 
    (counties['year'] == 2014)].copy()
# counties = counties[(counties['feedstock'] == "FOOD") & (counties['year'] == 2014)].copy()

###############################################################



####MAKE DICTIONARY HERE
# cdict = dict(zip(counties['COUNTY'], counties['disposal']))


############################################################
# COMPOSTING/PROCESSING FACILITIES
############################################################


# Mini gdfs of facilites (location and capacity)
facilities = gpd.read_file(opj(DATA_DIR, "clean/clean_swis.shp"))
facilities = facilities.to_crs(epsg=4326)
# facilities.head(8)

# facilities = facilities[['SwisNo', 'AcceptedWa', 'County', 'cap_m3', 'geometry']].copy()



############################################################
# RANGELANDS 
############################################################
# Import rangelands
rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
rangelands = rangelands.to_crs(epsg=4326) # make sure this is read in degrees (WGS84)

# Fix county names! 
countyIDs = pd.read_csv(opj(DATA_DIR, "interim/CA_FIPS_wcode.csv"), 
    names = ['FIPS', 'COUNTY', 'State', 'county_nam'])
countyIDs = countyIDs[['COUNTY', 'county_nam']]
rangelands = pd.merge(rangelands, countyIDs, on = 'county_nam')

# convert area capacity into volume capacity
rangelands['area_ha'] = rangelands['Shape_Area']/10000 # convert area in m2 to hectares
rangelands['capacity_m3'] = rangelands['area_ha'] * 63.5 # use this metric for m3 unit framework
# rangelands['capacity_ton'] = rangelands['area_ha'] * 37.1 # also calculated for tons unit framework

# estimate centroid
rangelands['centroid'] = rangelands['geometry'].centroid 


############################################################
# SUBSET!! for testing functions
############################################################# 
# SUBSET out four counties
# counties = counties[(counties['COUNTY'] == "Los Angeles") | (counties['COUNTY'] == "San Diego") |
#     (counties['COUNTY'] == "Orange")| (counties['COUNTY'] == "Imperial")]


# # # SUBSET out four counties
# facilities = facilities[(facilities['County'] == "San Diego") | (facilities['County'] == "Orange") | 
#     (facilities['County'] == "Imperial")].copy()
# # too many, just select first 5
# facilities = facilities[0:5]

# # # # SUBSET
# subset = ["los", "slo", "sbd"]
# rangelands = rangelands[rangelands['county_nam'].isin(subset)]


# raise Exception("data loaded - pre optimization")

############################################################
# CROPLANDS
#############################################################
 
# # Import croplands
# cropmap = gpd.read_file(opj(DATA_DIR, 
#   "raw/Crop__Mapping_2014/Crop__Mapping_2014.shp"))

# # exclude non-crop uses
# not_crops = ["Managed Wetland", "Urban", "Idle", "Mixed Pasture"]
# crops = cropmap[cropmap['Crop2014'].isin(not_crops)== False]


############################################################
# OPTIMIZATION #################################
############################################################



def SolveModel(scenario, feedstock = 'food_and_green', savedf = True, 
    counties = counties, landuse = rangelands, facilities = facilities,
    # Scenario settings
    disposal_rate = 1,   # percent of waste to include in run
    fw_reduction = 0,    # food waste reduced/recovered pre-disposal
    ignore_capacity = False, # toggle to ignore facility capacity info
    
    #Parameters
    landfill_ef = 315, #kg CO2e / m3 = emissions from waste remaining in county
    #compost_ef = 0,  
    kilometres_to_emissions = 0.37, # kg CO2e/ m3 - km for 35mph speed 
    kilometres_to_emissions_10 = 1, # TODO
    spreader_ef = 1.854, # kg CO2e / m3 = emissions from spreading compost
    seq_f = -108, # kg CO2e / m3 = sequestration rate
    # soil_emis = 68, # ignore now, included in seq?
    process_emis = 11, # kg CO2e/ m3 = emisisons at facility from processing compost
    waste_to_compost = 0.58, #% volume change from waste to compost
    c2f_trans_cost = .206, #$/m3-km # transit costs
    f2r_trans_cost = .206, #$/m3-km # transit costs
    spreader_cost = 5.8, #$/m3 # cost to spread
    detour_factor = 1.4, #chosen based on literature - multiplier on haversine distance
    ):


    # #Variables
    print("--setting constant parameters")


    # decision variables
    print("--defining decision vars")
    # proportion of county waste to send to a facility 
    c2f = {}
    for county in counties['COUNTY']:
        c2f[county] = {}
        cloc = Fetch(counties, 'COUNTY', county, 'county_centroid')
        for facility in facilities['SwisNo']:
            floc = Fetch(facilities, 'SwisNo', facility, 'geometry')
            c2f[county][facility] = {}
            c2f[county][facility]['quantity'] = cp.Variable()
            c2f[county][facility]['trans_emis'] = Distance(cloc,floc)*detour_factor*kilometres_to_emissions
            c2f[county][facility]['trans_cost'] = Distance(cloc,floc)*detour_factor*c2f_trans_cost

    # proportion of compost to send to rangeland 
    f2r = {}
    for facility in facilities['SwisNo']:
        f2r[facility] = {}
        floc = Fetch(facilities, 'SwisNo', facility, 'geometry')
        for rangeland in rangelands['OBJECTID']:
            rloc = Fetch(rangelands, 'OBJECTID', rangeland, 'centroid')
            f2r[facility][rangeland] = {}
            f2r[facility][rangeland]['quantity'] = cp.Variable()
            f2r[facility][rangeland]['trans_emis'] = Distance(floc,rloc)*detour_factor*kilometres_to_emissions
            f2r[facility][rangeland]['trans_cost'] = Distance(floc,rloc)*detour_factor*f2r_trans_cost

    ############################################################

    #BUILD OBJECTIVE FUNCTION: we want to minimize emissions (same as maximizing mitigation)
    obj = 0

    print("--building objective function")
    # emissions due to waste remaining in county
    for county in counties['COUNTY']:
        temp = 0
        for facility in facilities['SwisNo']:
            x    = c2f[county][facility]
            temp += x['quantity']
    #    temp = sum([c2f[county][facility]['quantity'] for facilities in facilities['SwisNo']]) #Does the same thing
        obj += landfill_ef*(1 - temp)

    for county in counties['COUNTY']:
        for facility in facilities['SwisNo']:
            x    = c2f[county][facility]
            # emissions due to transport of waste from county to facility 
            obj += x['quantity']*x['trans_emis']

    for county in counties['COUNTY']:
        for facility in facilities['SwisNo']:
            x    = c2f[county][facility]
            # emissions due to processing compost at facility
            obj += x['quantity']*process_emis

    # emissions due to waste remaining in facility
    # for facility in facilities['SwisNo']:
    #     temp = 0
    #     for rangeland in rangelands['OBJECTID']:
    #         x = f2r[facility][rangeland]
    #         temp += x['quantity']
    #     obj += compost_ef*(1 - temp)    


    for facility in facilities['SwisNo']:
        for rangeland in rangelands['OBJECTID']:
            x = f2r[facility][rangeland]
            applied_amount = x['quantity']
            # emissions due to transport of compost from facility to rangelands
            obj += x['trans_emis']* applied_amount
            # emissions due to application of compost by manure spreader
            obj += spreader_ef * applied_amount
            # emissions due to sequestration of applied compost
            obj += seq_f * applied_amount                             

    ############################################################

    #Constraints
    cons = []
    print("--subject to constraints")
    now = datetime.datetime.now()
    print(str(now))

    # change supply constraint by feedstock selected
    if feedstock == 'food_and_green':
        # Subset
        counties = counties[((counties['feedstock'] == "FOOD") | (counties['feedstock'] == "GREEN"))]
        # Adjust food waste disposal rates based on user input
        mask = counties.feedstock == "FOOD"
        column_name = 'disposal_wm3'
        # adjust food waste by defined reduction scenario
        counties.loc[mask, column_name] = (1-fw_reduction)*counties.loc[mask,column_name]
        # new column of sum of food and green waste
        counties['disposal'] = counties.groupby(['COUNTY'])['disposal_wm3'].transform('sum')
        # collapse counties
        counties = counties.drop_duplicates(subset = 'COUNTY')
    elif feedstock == 'food':
        # mask = counties.feedstock == "FOOD"
        # column_name = 'disposal_wm3'
        # # adjust food waste by defined reduction scenario
        # counties.loc[mask, column_name] = fw_reduction*counties.loc[mask,column_name]
        counties = counties[(counties['feedstock'] == "FOOD")]
        counties['disposal'] = (1-fw_reduction)* counties['disposal_wm3']
    elif feedstock == 'manure':
        counties = counties[(counties['feedstock'] == "MANURE")]
        counties['disposal'] = counties['disposal_wm3'] 

    counties['disposal_cap'] = (disposal_rate) * counties['disposal']

    #supply constraint
    for county in counties['COUNTY']:
        temp = 0
        for facility in facilities['SwisNo']:
            # print(facility)
            x    = c2f[county][facility]
            temp += x['quantity']
            cons += [0 <= x['quantity']]              #Quantity must be >=0
        cons += [temp <= Fetch(counties, 'COUNTY', county, 'disposal_cap')]   #Sum for each county must be <= county production

    # for scenarios in which we want to ignore existing infrastructure limits on capacity
    if ignore_capacity == False:
        # otherwise, use usual demand constraints
        for facility in facilities['SwisNo']:
            temp = 0
            for rangeland in rangelands['OBJECTID']:
                x = f2r[facility][rangeland]
                temp += x['quantity']
                cons += [0 <= x['quantity']]              #Each quantity must be >=0
            cons += [temp <= Fetch(facilities, 'SwisNo', facility, 'cap_m3')]  # sum of each facility must be less than capacity        

    # end-use  constraint capacity
    for rangeland in rangelands['OBJECTID']:
    	temp = 0
    	for facility in facilities['SwisNo']:
    		x = f2r[facility][rangeland]
    		temp += x['quantity']
            #TODO - is this constraint necessary - or repetitive of above
    		cons += [0 <= x['quantity']]				# value must be >=0
    	# rangeland capacity constraint (no more can be applied than 0.25 inches)
    	cons += [temp <= Fetch(rangelands, 'OBJECTID', rangeland, 'capacity_m3')]


    # balance facility intake to facility output
    for facility in facilities['SwisNo']:
    	temp_in = 0
    	temp_out = 0
    	for county in counties['COUNTY']:
    		x = c2f[county][facility]
    		temp_in += x['quantity']	# sum of intake into facility from counties
    	for rangeland in rangelands['OBJECTID']:
    		x = f2r[facility][rangeland]
    		temp_out += x['quantity']	# sum of output from facilty to rangeland
    	cons += [temp_out == waste_to_compost*temp_in]


    # #ALTERNATE OBJECTIVE FUNCTION IS TO MINIMIZE COST 
    # obj_cost = 0

    # # transport costs - county to facility
    # for county in counties['COUNTY']:
    #     for facility in facilities['SwisNo']:
    #         x    = c2f[county][facility]
    #         obj_cost += x['quantity']*x['trans_cost']


    # for facility in facilities['SwisNo']:
    #     for rangeland in rangelands['OBJECTID']:
    #         x = f2r[facility][rangeland]
    #         applied_amount = x['quantity']
    #         # emissions due to transport of compost from facility to rangelands
    #         obj_cost += x['trans_cost']* applied_amount
    #         # emissions due to application of compost by manure spreader
    #         obj_cost += spreader_cost * applied_amount

    ############################################################

    print("solving...")
    print("*********************************************")
    prob = cp.Problem(cp.Minimize(obj), cons)
    val = prob.solve(gp=False)
    print("Optimal object value (kg CO2eq) = {0}".format(val))

    ############################################################
    # print("{0:15} {1:15}".format("Rangeland","Amount"))
    # for facility in facilities['SwisNo']:
    #     for rangeland in rangelands['OBJECTID']:
    #         print("{0:15} {1:15} {2:15}".format(facility,rangeland,f2r[facility][rangeland]['quantity'].value))
    ############################################################

    #Calculate cost after solving!
    cost = 0

    cost_by_county = {}
    # transport costs - county to facility
    for county in counties['COUNTY']:
        cost_by_county[county] = {}
        temp = 0
        # cost_by_county[county]['COUNTY'] = county
        for facility in facilities['SwisNo']:
            x    = c2f[county][facility]
            cost += x['quantity'].value*x['trans_cost']
            temp += x['quantity'].value*x['trans_cost']
        cost_by_county[county]['cost'] = int(round(temp))

    for facility in facilities['SwisNo']:
        for rangeland in rangelands['OBJECTID']:
            x = f2r[facility][rangeland]
            applied_amount = x['quantity'].value
            # emissions due to transport of compost from facility to rangelands
            cost += x['trans_cost']* applied_amount
            # emissions due to application of compost by manure spreader
            cost += spreader_cost * applied_amount

    # alternately, calculate cost after maximizing CO2 mitigation
    print("COST ($) : ", cost)
    result = cost/val
    print("*********************************************")
    print("$/CO2e MITIGATED: ", -result)
    print("*********************************************")


    # # Disaggregated results I might want:
    # def SaveModelResults(scenario):

    # Quantity moved out of county
    county_output = {}
    print("{0:15} {1:15} {2:15}".format("County","Facility","Amount"))
    for county in counties['COUNTY']:
        temp = 0
        county_output[county] = {}
        for facility in facilities['SwisNo']:
            x = c2f[county][facility]['quantity'].value
            temp += x
            print("{0:15} {1:15} {2:15}".format(county,facility,x))
        county_output[county]['volume'] = int(round(temp))

    # Facility intake 
    fac_intake = {}
    for facility in facilities['SwisNo']:
        temp = 0
        fac_intake[facility] = {}
        fac_intake[facility]['SwisNo'] = facility
        for county in counties['COUNTY']:
            x = c2f[county][facility]['quantity'].value
            temp += x
        fac_intake[facility]['intake'] = int(round(temp))


    # Rangeland area covered (ha) & applied amount by rangeland
    rangeland_app = {}
    for rangeland in rangelands['OBJECTID']:
        applied_volume = 0
        area = 0
        rangeland_app[rangeland] = {}
        rangeland_app[rangeland]['OBJECTID'] = rangeland
        for facility in facilities['SwisNo']:
                x = f2r[facility][rangeland]
                applied_volume += x['quantity'].value
                area += int(round(applied_volume * (1/63.5)))
        rangeland_app[rangeland]['area_treated'] = area
        rangeland_app[rangeland]['volume'] = int(round(applied_volume))


    # turn above restults into dataframe for easier plotting later
    applied = pd.DataFrame.from_dict(rangeland_app, orient='index')
    output_df = pd.DataFrame.from_dict(county_output, orient='index')
    intake_df = pd.DataFrame.from_dict(fac_intake, orient='index')

    os.chdir("/Users/anayahall/projects/compopt/results")

    if savedf == True:
        # Save output for batch processing
        output_df.to_csv(str(scenario)+"_CountyOutput.csv")
        intake_df.to_csv(str(scenario)+"_FacIntake.csv")
        applied.to_csv(str(scenario)+"_LandApp.csv")

    return {'value': val, 'cost': cost,  'result': -result}, c2f, f2r


# r = pd.merge(rangelands, rdf, on = "OBJECTID")
# fac_df = pd.merge(facilities, fac_df, on = "SwisNo")






# scenario runs
# change transport emissions
# sensitivity runs - 





############################################################



