## compostoptimization.py

import cvxpy as cp
import numpy as np
import os
import datetime
from os.path import join as opj
import json


import pandas as pd
import shapely as shp
import geopandas as gpd
import scipy as sp

from biomass_preprocessing import MergeInventoryAndCounty
#from swis_preprocessing import LoadAndCleanSWIS #TODO

DATA_DIR = "/Users/anayahall/projects/compopt/data"
RESULTS_DIR = "/Users/anayahall/projects/compopt/results"



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


def SaveModelVars(c2f, f2r):

    c2f_values = {}

    for county in c2f.keys():
        # print("COUNTY: ", county)
        c2f_values[county] = {}
        for facility in c2f[county].keys():
            # print("FACILITY: ", facility)
            c2f_values[county][facility] = {}
            x = c2f[county][facility]['quantity'].value
            c2f_values[county][facility] = (round(int(x)))


    f2r_values = {}

    for facility in f2r.keys():
        f2r_values[facility] = {}
        for rangeland in f2r[facility].keys():
            f2r_values[facility][rangeland] = {}
            x = f2r[facility][rangeland]['quantity'].value
            f2r_values[facility][rangeland] = (round(int(x)))

    return c2f_values, f2r_values


############################################################

# bring in biomass data
gbm_pts, tbm_pts = MergeInventoryAndCounty(
    gross_inventory     = opj(DATA_DIR, "raw/biomass.inventory.csv"),
    technical_inventory = opj(DATA_DIR, "raw/biomass.inventory.technical.csv"),
    county_shapefile    = opj(DATA_DIR, "raw/CA_Counties/CA_Counties_TIGER2016.shp"),
    counties_popcen     = opj(DATA_DIR, "counties/CenPop2010_Mean_CO06.txt")
)

# mini gdfs of county wastes (tbm - location and MSW for 2014) 
# counties = gpd.read_file(opj(DATA_DIR, "clean/techbiomass_pts.shp"))
# counties = counties.to_crs(epsg=4326)
counties = tbm_pts # could change to GBM

############################################################
# NEW COUNTY SHAPE


# counties = pd.read_csv("../data/counties/CenPop2010_Mean_CO06.txt") # NEW - population weighted means!
# # rename lat and lon for easier plotting
# counties.rename(columns = {'LATITUDE': 'lat', 'LONGITUDE': 'lon', 'COUNAME': 'NAME'}, inplace=True)


# filter by YEAR up here, then refine by  feedstock inside the function
counties = counties[((counties['feedstock'] == "FOOD") | 
    (counties['feedstock'] == "GREEN") | (counties['feedstock'] == "MANURE")) & 
    (counties['year'] == 2014)].copy()
# counties = counties[(counties['feedstock'] == "FOOD") & (counties['year'] == 2014)].copy()

############################################################
# COMPOSTING/PROCESSING FACILITIES
############################################################


# Load facility info
facilities = gpd.read_file(opj(DATA_DIR, "clean/clean_swis.shp"))
facilities.rename(columns={'County':'COUNTY'}, inplace=True)
# facilities = facilities.to_crs(epsg=4326)

# facilities = facilities[['SwisNo', 'AcceptedWa', 'COUNTY', 'cap_m3', 'geometry']].copy()


############################################################
# RANGELANDS 
############################################################
# Import rangelands
rangelands = gpd.read_file(opj(DATA_DIR, "raw/CA_FMMP_G/gl_bycounty/grazingland_county.shp"))
rangelands = rangelands.to_crs(epsg=4326) # make sure this is read in degrees (WGS84)

# Fix county names in RANGELANDS! 
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
# # SUBSET out four counties
# counties = counties[(counties['COUNTY'] == "Los Angeles") | (counties['COUNTY'] == "San Diego") |
#     (counties['COUNTY'] == "Orange")| (counties['COUNTY'] == "Imperial")]
# # counties = counties[0:15]

# # # SUBSET out four counties
# facilities = facilities[(facilities['COUNTY'] == "San Diego") | (facilities['COUNTY'] == "Orange") | 
#     (facilities['COUNTY'] == "Imperial")].copy()
# # too many, just select first 5
# # facilities = facilities[0:10]

# # # # SUBSET
# subset = ["los", "slo", "sbd"]
# rangelands = rangelands[rangelands['county_nam'].isin(subset)]
# rangelands = rangelands[0:15]

############################################################
# raise Exception("data loaded - pre optimization")
############################################################

############################################################
# CROPLANDS
#############################################################
 
# # Import croplands
# cropmap = gpd.read_file(opj(DATA_DIR, 
#   "raw/Crop__Mapping_2014/Crop__Mapping_2014.shp"))

# # exclude non-crop uses
# not_crops = ["Managed Wetland", "Urban", "Idle", "Mixed Pasture"]
# crops = cropmap[cropmap['Crop2014'].isin(not_crops)== False]

# leave IDLE , delete managed wetland, urban, and riparian
## SAVE AS SHAPE!

############################################################
# OPTIMIZATION MODEL       #################################
############################################################


def SolveModel(scenario_name = None, feedstock = 'food_and_green', savedf = True, 
    counties = counties, landuse = rangelands, facilities = facilities,
    
    # Scenario settings
    disposal_rate = 1,   # percent of waste to include in run
    fw_reduction = 0,    # food waste reduced/recovered pre-disposal
    ignore_capacity = False, # toggle to ignore facility capacity info
    capacity_multiplier = 1, # can inflate capacity 
    
    #Parameters
    landfill_ef = 315, #kg CO2e / m3 = avoided emissions from waste going to landfill
    #compost_ef = 0,  
    kilometres_to_emissions = 0.37, # kg CO2e/ m3 - km for 35mph speed 
    kilometres_to_emissions_10 = 1, # TODO
    spreader_ef = 1.854, # kg CO2e / m3 = emissions from spreading compost
    seq_f = -108, # kg CO2e / m3 = sequestration rate
    # soil_emis = 68, # ignore now, included in seq?
    process_emis = 11, # kg CO2e/ m3 = emisisons at facility from processing compost
    waste_to_compost = 0.58, #% volume change from waste to compost
    c2f_trans_cost = 0.412, #$/m3-km # transit costs (alt is 1.8)
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
            dist = Distance(cloc,floc)
            c2f[county][facility]['trans_emis'] = dist*detour_factor*kilometres_to_emissions
            c2f[county][facility]['trans_cost'] = dist*detour_factor*c2f_trans_cost

    # proportion of compost to send to rangeland 
    f2r = {}
    for facility in facilities['SwisNo']:
        f2r[facility] = {}
        floc = Fetch(facilities, 'SwisNo', facility, 'geometry')
        for rangeland in rangelands['OBJECTID']:
            rloc = Fetch(rangelands, 'OBJECTID', rangeland, 'centroid')
            f2r[facility][rangeland] = {}
            f2r[facility][rangeland]['quantity'] = cp.Variable()
            dist = Distance(floc,rloc)
            f2r[facility][rangeland]['trans_emis'] = dist*detour_factor*kilometres_to_emissions
            f2r[facility][rangeland]['trans_cost'] = dist*detour_factor*f2r_trans_cost

    ############################################################

    #BUILD OBJECTIVE FUNCTION: we want to minimize emissions (same as maximizing mitigation)
    obj = 0

    print("--building objective function")
    # emissions due to waste remaining in county
    for county in counties['COUNTY']:
        # total_waste = Fetch(counties, 'COUNTY', county, 'disposal_cap')
        temp = 0
        for facility in facilities['SwisNo']:
            x    = c2f[county][facility]
            temp += x['quantity']
    #    temp = sum([c2f[county][facility]['quantity'] for facilities in facilities['SwisNo']]) #Does the same thing
        obj += landfill_ef*(1 - temp)
        # obj += landfill_ef*(total_waste - temp)

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

    # Set disposal cap for use in constraints
    counties['disposal_cap'] = (disposal_rate) * counties['disposal']

    #Constraints
    cons = []
    print("--subject to constraints")
    now = datetime.datetime.now()
    print(str(now))

    #supply constraint
    for county in counties['COUNTY']:
        temp = 0
        for facility in facilities['SwisNo']:
            # print(facility)
            x    = c2f[county][facility]
            temp += x['quantity']
            cons += [0 <= x['quantity']]              #Quantity must be >=0
        cons += [temp <= Fetch(counties, 'COUNTY', county, 'disposal_cap')]   #Sum for each county must be <= county production

    facilities['facility_capacity'] = capacity_multiplier * facilities['cap_m3']

    # for scenarios in which we want to ignore existing infrastructure limits on capacity
    if ignore_capacity == False:
        # otherwise, use usual demand constraints
        for facility in facilities['SwisNo']:
            temp = 0
            for rangeland in rangelands['OBJECTID']:
                x = f2r[facility][rangeland]
                temp += x['quantity']
                cons += [0 <= x['quantity']]              #Each quantity must be >=0
            cons += [temp <= Fetch(facilities, 'SwisNo', facility, 'facility_capacity')]  # sum of each facility must be less than capacity        

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

    ############################################################

    print("-solving...")
    print("*********************************************")
    prob = cp.Problem(cp.Minimize(obj), cons)
    val = prob.solve(gp=False)
    CO2mit = -val/(10**9)
    now = datetime.datetime.now()
    print(str(now))
    print("Optimal object value (Mt CO2eq) = {0}".format(CO2mit))

    ############################################################
    # print("{0:15} {1:15}".format("Rangeland","Amount"))
    # for facility in facilities['SwisNo']:
    #     for rangeland in rangelands['OBJECTID']:
    #         print("{0:15} {1:15} {2:15}".format(facility,rangeland,f2r[facility][rangeland]['quantity'].value))
    ############################################################

    # Rangeland area covered (ha) & applied amount by rangeland
    rangeland_app = {}
    for rangeland in rangelands['OBJECTID']:
        r_string = str(rangeland)
        applied_volume = 0
        area = 0
        temp_transport_emis = 0
        temp_transport_cost = 0
        rangeland_app[r_string] = {}
        rangeland_app[r_string]['OBJECTID'] = r_string
        rangeland_app[r_string]['COUNTY'] = Fetch(rangelands, 'OBJECTID', rangeland, 'COUNTY')
        for facility in facilities['SwisNo']:
                x = f2r[facility][rangeland]
                applied_volume += x['quantity'].value
                temp_transport_emis += applied_volume* x['trans_emis']
                temp_transport_cost += applied_volume *x['trans_cost']
                area += int(round(applied_volume * (1/63.5)))
        rangeland_app[r_string]['area_treated'] = area
        rangeland_app[r_string]['volume'] = int(round(applied_volume))
        rangeland_app[r_string]['application_cost'] = int(round(applied_volume))*spreader_cost
        rangeland_app[r_string]['application_emis'] = int(round(applied_volume))*spreader_ef
        rangeland_app[r_string]['trans_emis'] = temp_transport_emis
        rangeland_app[r_string]['trans_cost'] = temp_transport_cost
        rangeland_app[r_string]['sequestration'] = applied_volume*seq_f

    # # Quantity moved out of county
    county_results = {}
    # print("{0:15} {1:15} {2:15}".format("COUNTY","Facility","Amount"))
    for county in counties['COUNTY']:
        output = 0
        # temp_volume = 0
        temp_transport_emis = 0
        temp_transport_cost = 0
        county_results[county] = {}
        for facility in facilities['SwisNo']:
            x = c2f[county][facility]
            output += x['quantity'].value
            # temp_volume += x['quantity'].value
            temp_transport_emis += output * x['trans_emis']
            temp_transport_cost += output * x['trans_cost']
            # print("{0:15} {1:15} {2:15}".format(county,facility,output))
        county_results[county]['output'] = int(round(output))
        county_results[county]['ship_emis'] = int(round(temp_transport_emis))
        county_results[county]['TOTAL_emis'] = temp_transport_emis
        county_results[county]['ship_cost'] = int(round(temp_transport_cost))
        county_results[county]['TOTAL_cost'] = temp_transport_cost

    # # Facility intake 
    fac_intake = {}
    for facility in facilities['SwisNo']:
        temp_volume = 0
        fac_intake[facility] = {}
        fac_intake[facility]['SwisNo'] = facility
        fac_intake[facility]['COUNTY'] = Fetch(facilities, 'SwisNo', facility, 'COUNTY')
        for county in counties['COUNTY']:
            x = c2f[county][facility]
            # t = c2f[county][facility]['quantity'].value
            temp_volume += x['quantity'].value
        fac_intake[facility]['intake'] = int(round(temp_volume))
        fac_intake[facility]['facility_emis'] = temp_volume*process_emis

    ####################################
    # print(county_results)
    # county_results = {}
    for k,v in rangeland_app.items():
        county = v['COUNTY']
        # print('county', county)
        if county in county_results:

            if 'TOTAL_emis' in county_results[county].keys():
                county_results[v['COUNTY']]['TOTAL_emis'] = county_results[v['COUNTY']]['TOTAL_emis']
            else: 
                county_results[v['COUNTY']]['TOTAL_emis'] = 0

            # SUM VOLUME OF RANGELAND IN COUNTY
            if 'volume_applied' in county_results[county].keys():
                county_results[v['COUNTY']]['volume_applied'] = county_results[v['COUNTY']]['volume_applied'] + v['volume']
            else:
                county_results[county]['volume_applied'] = v['volume']
            
            # Sum of cost of applying compost in the county
            if 'application_cost' in county_results[county].keys():
                county_results[v['COUNTY']]['application_cost'] = county_results[v['COUNTY']]['application_cost'] + v['application_cost']
            else:
                county_results[county]['application_cost'] = v['application_cost']
            
            # sum of emissions from applying compost in county
            if 'application_emis' in county_results[county].keys():
                county_results[v['COUNTY']]['application_emis'] = county_results[v['COUNTY']]['application_emis'] + v['application_emis']
                county_results[v['COUNTY']]['TOTAL_emis'] = county_results[v['COUNTY']]['TOTAL_emis'] + v['application_emis']

            else:
                county_results[county]['application_emis'] = v['application_emis']
                county_results[v['COUNTY']]['TOTAL_emis'] =  v['application_emis']

            
            # sum of transportation emissions for hauling compost to county's rangelands
            if 'trans_emis' in county_results[county].keys():
                county_results[v['COUNTY']]['trans_emis'] = county_results[v['COUNTY']]['trans_emis'] + v['trans_emis']
                county_results[v['COUNTY']]['TOTAL_emis'] = county_results[v['COUNTY']]['TOTAL_emis'] + v['trans_emis']

            else:
                county_results[county]['trans_emis'] = v['trans_emis']
                county_results[v['COUNTY']]['TOTAL_emis'] = v['trans_emis']

            
            # sum of transportation costs for hauling compost to county's rangelands
            if 'trans_cost' in county_results[county].keys():
                county_results[v['COUNTY']]['trans_cost'] = county_results[v['COUNTY']]['trans_cost'] + v['trans_cost']
            else:
                county_results[county]['trans_cost'] = v['trans_cost']
            
            # total sequestration potential from applying compost in county
            if 'sequestration' in county_results[county].keys():
                county_results[v['COUNTY']]['sequestration'] = county_results[v['COUNTY']]['sequestration'] + v['sequestration']
                county_results[v['COUNTY']]['TOTAL_emis'] = county_results[v['COUNTY']]['TOTAL_emis'] - v['sequestration']

            else:
                county_results[county]['sequestration'] = v['sequestration']
                county_results[v['COUNTY']]['TOTAL_emis'] = v['sequestration']

        else:
            county_results[county] = {}
            county_results[county]['volume_applied'] = v['volume']
            county_results[county]['trans_cost'] = v['trans_cost']
            county_results[county]['trans_emis'] = v['trans_emis']
            county_results[county]['application_emis'] = v['application_cost']
            county_results[county]['application_emis'] = v['application_emis']
            county_results[county]['sequestration'] = v['sequestration']
            county_results[county]['TOTAL_emis'] = v['application_emis']+ v['trans_emis']

    for k,v in fac_intake.items():
        # print('k: ', k)
        # print('v: ', v)
        # print('V.COUNTY: ', v['COUNTY'])
        county = v['COUNTY']
        # print('county', county)
        if county in county_results:
            if 'county_fac_intake' in county_results[county].keys(): 
                county_results[v['COUNTY']]['county_fac_intake'] = county_results[v['COUNTY']]['county_fac_intake'] + v['intake']
                # print('got in here...')
            else:
                county_results[county]['county_fac_intake'] = v['intake']
            if 'county_fac_emis' in county_results[county].keys(): 
                county_results[v['COUNTY']]['county_fac_emis'] = county_results[v['COUNTY']]['county_fac_emis'] + v['facility_emis']
                # print('got in here...')
            else:
                county_results[county]['county_fac_emis'] = v['facility_emis']
        else:
            county_results[county] = {}
            county_results[county]['county_fac_intake'] = v['intake']
            county_results[county]['county_fac_emis'] = v['facility_emis']
        # print(county_results)

#########################################

    #Calculate cost after solving!
    project_cost = 0

    cost_dict = {}
    # transport costs - county to facility
    for county in counties['COUNTY']:
        cost_dict[county] = {}
        ship_cost = 0
        # cost_dict[county]['COUNTY'] = county
        for facility in facilities['SwisNo']:
            x    = c2f[county][facility]
            project_cost += x['quantity'].value*x['trans_cost']
            ship_cost += x['quantity'].value*x['trans_cost']
        cost_dict[county]['cost'] = int(round(ship_cost))

    for facility in facilities['SwisNo']:
        for rangeland in rangelands['OBJECTID']:
            x = f2r[facility][rangeland]
            applied_amount = x['quantity'].value
            # project_cost due to transport of compost from facility to rangelands
            project_cost += x['trans_cost']* applied_amount
            # project_cost due to application of compost by manure spreader
            project_cost += spreader_cost * applied_amount


    cost_millions = (project_cost/(10**6))    
    print("COST (Millions $) : ", cost_millions)
    result = project_cost/val
    abatement_cost = (-result*1000)
    print("*********************************************")
    print("$/tCO2e MITIGATED: ", abatement_cost)
    print("*********************************************")


    c2f_values, f2r_values = SaveModelVars(c2f, f2r)


    return c2f_values, f2r_values, rangeland_app
    # return rangeland_app, cost_dict, county_results, fac_intake

# r = pd.merge(rangelands, rdf, on = "COUNTY")
# fac_df = pd.merge(facilities, fac_df, on = "SwisNo")


############################################################



