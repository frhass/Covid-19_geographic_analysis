# -*- coding: utf-8 -*-
"""
@author: Frederik Hass, Aalborg University - Copenhagen
email: frederiksh@plan.aau.dk
github repository: https://github.com/frhass/Covid-19_geographic_analysis 
"""

# load libraries
import pandas as pd
import numpy as np
import geopandas as gpd
import os
import sys
import imageio
import matplotlib.pyplot as plt
from pysal.lib  import weights
from esda.moran import Moran, Moran_Local
import esda
from splot.esda import moran_scatterplot, plot_moran, lisa_cluster


print("Version info.")
print (sys.version_info)

# set the filepath and load in a shapefile
shp = r"C:\path_to_folder\ECDC_NUTS_Regions.shp"

shape_data = gpd.read_file(shp)

# Load in csv to merge with geodata
# Weekly Covid-19 data here https://www.ecdc.europa.eu/en/publications-data/weekly-subnational-14-day-notification-rate-covid-19
df = pd.read_csv(r"C:\path_to_folder\20201125_covid-19_EU_regions.csv", header=0, encoding="utf-8")
# check shapefile dataframe head
print("Covid-Cases Dataframe Columns:",df.columns.values)
  
# #pivot table
cases = df.pivot_table(values='rate_14_day_per_100k', index='nuts_code', columns='year_week')

# Join shapefile dataframe and the individual pivotet data tables
merged = shape_data.set_index('ECDC_NUTS').join(cases) 
merged.fillna(0, inplace=True)

merged.columns = merged.columns.astype(str)


### SPATIAL AUTOCORRELATION ###

# list of weeks - derived from merged dataframe 
merged_list = merged.columns.tolist()
list_of_weeks = []
 
year_list = ['2020'] 
for year in year_list:
     for week in merged_list:
         item = year
         if item in week:
             list_of_weeks.append(week)

# Remove week-13, where no data is reported
list_of_weeks.remove('2020-W13')
#Renamen the week column from W to Week
week_names = [w.replace('W', 'Week') for w in list_of_weeks]

#copy case dataframe
spacetime_df = merged.filter(['REG_NAME','geometry'], axis=1)

#Loop over each week and weekname for spatial autocorrelation 
for week, week_name in zip(list_of_weeks, week_names):

    #copy case dataframe
    sa_df = merged.filter([week,'REG_NAME','geometry'], axis=1)   

    # Create output path and files
    output_path = r"C:\path_to_folder\Maps"
    filepath = os.path.join(output_path, week+'.png')    


    #Spatial Weights - select one
    #w = weights.Queen.from_dataframe(sa_df, idVariable="region_name") # Queen Contiguity Matrix
    #w = weights.Rook.from_dataframe(sa_df, idVariable="region_name")  # Rook contiguity Matrix
    w = weights.distance.KNN.from_dataframe(sa_df, ids="REG_NAME", k=6) # K-Nearest Neighbors

    w.transform = "R"
    
    sa_df["lag_infections"] = weights.lag_spatial(w, sa_df[week])
    
    # Global spatial autocorrelation
    y = sa_df[week]
    moran = Moran(y, w)
    
    # Local spatial autocorrelation
    li = esda.moran.Moran_Local(y, w)

    #lisa = m_local.Is
    sig = 1 * (li.p_sim < 0.05)
    hotspot = 1 * (sig * li.q==1)
    coldspot = 3 * (sig * li.q==3)
    doughnut = 2 * (sig * li.q==2)
    diamond = 4 * (sig * li.q==4)
    spots = hotspot + coldspot + doughnut + diamond
    
    spot_labels = [ '0 ns', '1 hot spot', '2 doughnut', '3 cold spot', '4 diamond']
    labels = [spot_labels[i] for i in spots]
    spacetime_df[week] = labels
    
#####
    
# spacetime_df have spatial autocorrelation results each week, calculate emerging hotspots in new column
nr_weeks = len(list_of_weeks)
week_max = int(len(list_of_weeks) * 0.75)
week_min = int(nr_weeks - week_max)


em_hs_list = []
for index, row in spacetime_df.iterrows():      
    index_list = []
    for week in list_of_weeks:
        #print(row[week])
        index_list.append(row[week])

    ## Set up rules and append to list
    # Hotspots
    if( index_list[-1] == '1 hot spot' and '1 hot spot' not in index_list[:-1] ):
       print(str(index), 'New Hotspot')
       em_hs_list.append('New Hotspot')
    elif( index_list.count('1 hot spot') < week_min and index_list.count('1 hot spot') >= 1 and '3 cold spot' not in index_list):
        print(str(index), 'Sporadic Hotspot')
        em_hs_list.append('Sporadic Hotspot')
    elif( index_list[-1] == '1 hot spot' and index_list.count('3 cold spot') > 1 and index_list.count('1 hot spot') < week_max):
        print(str(index), 'Oscillating Hotspot')
        em_hs_list.append('Oscillating Hotspot')
    elif( '1 hot spot' not in index_list[-1] and index_list.count('1 hot spot') > week_max):
        print(str(index), 'Historical Hotspot')
        em_hs_list.append('Historocal Hotspot')
    elif( index_list.count('1 hot spot') > week_max and index_list[-1] == '1 hot spot' ):
        print(str(index), 'Intensifying Hotspot')
        em_hs_list.append('Intensifying Hotspot')
    elif( index_list.count('1 hot spot') > week_max ):
        print(str(index), 'Persistent Hotspot')
        em_hs_list.append('Persistent Hotspot')
    # Coldspots
    elif( index_list[-1] == '3 cold spot' and '3 cold spot' not in index_list[:-1] ):
       print(str(index), 'New Coldspot')
       em_hs_list.append('New Coldspot')
    elif( index_list.count('3 cold spot') < week_min and index_list.count('3 cold spot') >= 1 and '1 hot spot' not in index_list ):
        print(str(index), 'Sporadic Coldspot')
        em_hs_list.append('Sporadic Coldspot')
    elif( index_list[-1] == '3 cold spot' and index_list.count('1 hot spot') > 1 and index_list.count('3 cold spot') < week_max):
        print(str(index), 'Oscillating Coldspot')
        em_hs_list.append('Oscillating Coldspot')
    elif( '3 cold spot' not in index_list[-1] and index_list.count('3 cold spot') > week_max):
        print(str(index), 'Historical Coldspot')
        em_hs_list.append('Historocal Coldspot')
    elif( index_list.count('3 cold spot') > week_max and index_list[-1] == '3 cold spot' ):
        print(str(index), 'Intensifying Coldspot')
        em_hs_list.append('Intensifying Coldspot')
    elif( index_list.count('3 cold spot') > week_max ):
        print(str(index), 'Persistent Coldspot')
        em_hs_list.append('Persistent Coldspot')
    
    else:
        em_hs_list.append('Not Significant')

 
#print(em_hs_list)
print('em_hs_list length:', len(em_hs_list))
        
print('nr of weeks: ',nr_weeks)
print('upper threshold of weeks:', week_max)
print('lower threshold of weeks:', week_max)

spacetime_df['Emer_Spots'] = em_hs_list
gdf = gpd.GeoDataFrame(spacetime_df, geometry='geometry')
out_path = r"C:\path_to_folder\SpaceTime_DF.shp"
gdf.to_file(out_path, driver='ESRI Shapefile')
