# Compost Sites for Project Grapevine
# Anaya Hall
# this script loads and cleans data files containing composting facilities in California

# Origninally created for nrt poster using Waterboard data (compostsites.csv) - September 2018
# February 2019 -- amended to utilize EPA Region 9 composting facilities from ExcessFoodMap 
# and CalRecycle's Solid Waste Inventory Data <- preferred data source

rm(list = ls())
# load libraries
library(ggplot2)
library(ggmap)
library(maps)
library(mapdata)
library(tidyverse)
library(dplyr)
library(raster)
library(maptools)
library(reshape)
library(ncdf4)
library(rgeos)
library(sp)
library(rgdal)

#set project wd
setwd("/Users/anayahall/projects/grapevine")

# grab state maps for plotting later
states <- map_data("state")
counties <- map_data(map = "county", region = "california") #, region == "california")
# just want CA
CA <- subset(states, region =="california")  

# ###############################################################################################################
# WaterBoard Data - old
###############################################################################################################
# 
# # load first run of data from CA waterboard
# comp_sites <- read_csv("data/WB_compostsites.csv", skip=1,
#                        col_names = c("name", "id", "type", "status", "address", "city", "lat", "long"))
# 
# # filter to only open/active 
# open_sites <- subset(comp_sites, status != "OPEN - CLOSED/WITH MONITORING")
# ###############################################################################################################
# EPA Excess FoodMap Data (old)
###############################################################################################################
# 
# 
# # Load EPA DATA (EXCESSFOODMAP) 
# allFacilities <- readxl::read_excel('data/EXCESSFOODPUBLIC_USTER_2015_R9.GDB/ExcelTables/Composting Facilities.xlsx', 
#                                     sheet = 2)
# CAfacilities <- allFacilities %>% filter(State == "CA")
# 
# # Need to GEOCODE
# #https://www.r-bloggers.com/batch-geocoding-with-r-and-google-maps/
# 
# # FIRST Register w Google maps and set up API Key
#   # devtools::install_github("dkahle/ggmap")
#   # register_google("AIzaSyDMg1LIYzqPk8sAZD0OKqMTBjhZmlEzLig")
#   # ggmap_credentials()
# 
# # street_addresses <- CAfacilities$Address
# # cities <- CAfacilities$City
# # 
# # full_addresses <- paste0(street_addresses, ", ", cities)
# # 
# # # get lat long and bind to df
# # epa_sites_geo <- cbind(CAfacilities, geocode(full_addresses))
# 
# #save as separate csv for late
# #write_csv(epa_sites_geo, "data/epa_facilities_geocoded.csv")
# 
# epa_sites_geo <- read_csv("data/epa_facilities_geocoded.csv")

###############################################################################################################
# CalRecycle's SWIS Inventory  ** Preferred source! 
# This dataset is already geotagged and also contains information on CAPACITY

library(readxl)    

#function to load all sheets
read_excel_allsheets <- function(filename, tibble = FALSE) {
  # I prefer straight data.frames
  # but if you like tidyverse tibbles (the default with read_excel)
  # then just pass tibble = TRUE
  sheets <- readxl::excel_sheets(filename)
  x <- lapply(sheets, function(X) readxl::read_excel(filename, sheet = X))
  if(!tibble) x <- lapply(x, as.data.frame)
  names(x) <- sheets
  x
}

#load all three sheets of Cal Recycle's SWIS dataset
swis_raw <- read_excel_allsheets("data/SWIS.xls")

# Join
swis_joined <- inner_join(x= swis_raw$Site, y = swis_raw$Unit)

# keep only needed vars
swis_clean <- swis_joined %>% select(SwisNo, Name, County, Location, Place, Latitude, Longitude, 
                                     Category, Activity, OperationalStatus, AcceptedWaste, Throughput, 
                                     ThroughputUnits, Capacity, CapacityUnits, Acreage, RemainingCapacity)
#save as csv
write_csv(swis_clean, "data/swis_clean.csv")

#filter to composting (may come back to this to select all other sites as well)
comp_swis <- swis_clean %>% filter(str_detect(Activity, "Compost") | str_detect(Activity, "Chip") & OperationalStatus != "Closed")
#comp_sites <- swis_clean %>% filter(str_detect(Category, "Compost") & OperationalStatus == "Active")

write_csv(comp_swis, "data/swis_compost.csv")

###############################################################################################################
# Check against compost/active list (which has 182 entries, but no capacity units) - 
# join with larger SWIS databses and change UNITS to be consistent
# (alternate download from swis database: CompostActive_FacilityDirectory-- is this different???)
###############################################################################################################
# comp_act_dir <- read_excel("data/CompostActive_FacilityDirectory.xlsx")
# names(comp_act_dir)[1] <- "SwisNo"
# coIDlist <- c(unique(comp_act_dir$SwisNo))

# THIS IS NOT WORKING! ARRRG - only finding 9 that overlap???? 
# swis_check <- swis_open %>% filter(SwisNo %in% coIDlist)


###############################################################################################################
# CLEAN CAPACITY UNITS!!!!!
###############################################################################################################
comp_swis <- read_csv("data/swis_compost.csv")

# subset out stuff measured in tons - convert to cu yards
# 1 ton = 2.24 cu yards compost

# CR_sites %>% filter(str_detect(CapacityUnits, "day")) %>% mutate(Capacity = Capacity * 365) %>% rbind(CR_sites)
# 
# 
# ton_sub <- CR_sites %>% filter(str_detect(CapacityUnits, "Tons")) %>%
#   mutate(Capacity = (Capacity * 2.24), CapacityUnits = "Cubic Yards")
# 
# rest <- CR_sites %>% filter(str_detect(CapacityUnits, "Yards"))
# bm_cap_B <- sum(rest$Capacity)
# bm_cap_A <- sum(ton_sub$Capacity)
# bm_cap <- bm_cap_A + bm_cap_B # cubic yards
# 
# bm_cap / 2.24


#subset out by type
units_list <- unique(swis_clean$CapacityUnits)
# summary(swis_clean$CapacityUnits == "Tons/day")

# funciton to convert units into all same
clean_capacity <- function(inputdata, arg2) {
  nsites <- nrow(inputdata)
  cleaned 
  for(i in 1:nsites){
    #print(i)
    print(inputdata[i,"CapacityUnits"])
    # if swis_clean$CapacityUnits == "Tons/day"
    #   capacity_y3 ==

  }
  #return(final_df)
}

#RUN FUNCITON
clean_capacity(inputdata =comp_swis)

###############################################################################################################
# MAKE SPATIAL
###############################################################################################################
coordinates(comp_swis)=~Longitude+Latitude

# Convert to your regular km system by first telling it what CRS it is, and then spTransform to the destination.

proj4string(comp_swis)=CRS("+init=epsg:4326") # set it to lat-long
comp_sp = spTransform(comp_swis,
                        CRS("+proj=aea +lat_1=33.11213321093334 +lat_2=40.89742770321884 +lon_0=-119.59716796875"))

writeOGR(comp_sp, "data/compost_spatial",driver = "ESRI Shapefile" , 
         layer = "compost", overwrite_layer = TRUE)


###############################################################################################################
# PLOT TO COMPARE DATA SOURCES

png("plots/model_overview.png", width = 1000, height = 1200, units = "px")

g <- ggplot(data = CA, mapping = aes(x = long, y = lat)) +
  coord_fixed(1.3) +
  geom_polygon(color = "black", fill = "white") +
 #  geom_polygon(data = counties, aes(fill=region), color = "grey", fill = "white") +
  geom_point(data = open_sites, mapping = aes(x = long, y = lat), color = "orange1", size = 5, alpha=.5) +
  geom_point(data = epa_sites_geo, aes(x=lon, y=lat), color = "blue", size = 5, alpha=.5) +
  geom_point(data = CR_sites, aes(x = Longitude, y = Latitude), color = "green", size = 5, alpha=.5) +
  theme_minimal()

# NOTE : UniqueID == CPL01135 is on Catalina Island!
# print map
g

dev.off()

