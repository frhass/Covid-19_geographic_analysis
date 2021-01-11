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


print("Version info.")
print (sys.version_info)

### PREPARE DATA ###

# set the filepath and load in a shapefile
shp = r"C:\path_fo_folder\ECDC_NUTS_Regions.shp"

shape_data = gpd.read_file(shp)


# check shapefile dataframe columns
print("Shapefile Dataframe Columns:",shape_data.columns.values)

## test the shapefile data to see how it looks in a cmap
#plot = shape_data.plot(column='CNTR_CODE', cmap='OrRd')
#fig = plot.get_figure()


# Load in csv to merge with geodata
# Weekly data here https://www.ecdc.europa.eu/en/publications-data/weekly-subnational-14-day-notification-rate-covid-19
df = pd.read_csv(r"C:\path_fo_folder\20201125_covid-19_EU_regions.csv", header=0, encoding="utf-8")
# check csv dataframe columns
print("Covid-Cases Dataframe Columns:",df.columns.values)
 
  
# #pivot table
cases = df.pivot_table(values='rate_14_day_per_100k', index='nuts_code', columns='year_week')
 
# Join shapefile dataframe and the individual pivotet data tables
merged = shape_data.set_index('ECDC_NUTS').join(cases) 
merged.fillna(0, inplace=True)

merged.columns = merged.columns.astype(str)


# Test plot
'''
### Plot a single map for test ###
ax = merged.plot(column='2020-W15', cmap='OrRd', figsize=(8,9), scheme='user_defined',
                 classification_kwds={'bins':[25,50,100,250,500,1000,2000]},
                 legend=True, linewidth=0.8, edgecolor='0.8')
 
description = 'Covid-19 cases per 100.000 inhabitants \nover the past two weeks'
info_text = 'Made by Frederik Hass - Aalborg University, Copenhagen \nCovid-19 data from ECDC - \nThe European Centre for Disease Prevention and Control '
ax.set_title('2020-08-01', fontdict={'fontsize': 24}, loc='left')
ax.annotate(description, xy=(0.3, 0.105), size=14, xycoords='figure fraction')
ax.annotate(info_text, xy=(0.3, 0.041), size=8, xycoords='figure fraction')
ax.set_axis_off()
ax.set_xlim([-25, 35.6])
ax.set_ylim([33, 71.3])
ax.get_legend().set_bbox_to_anchor((0.25, 0.13)) #(x,y)
ax.get_figure()
'''

### MAP STUFF ###

# Looping over all individual weeks and creates a map for each

# Define output folder for maps 
output_path = r"C:\path_fo_folder\Maps"
 
# create list of weeks - derived from merged dataframe 
merged_list = merged.columns.tolist()
list_of_weeks = []

year_list = ['2020'] 
# month_list = ['2020-03','2020-04','2020-05','2020-06','2020-07','2020-08']
for year in year_list:
     for week in merged_list:
         item = year
         if item in week:
             list_of_weeks.append(week)

list_of_weeks.remove('2020-W13') # week13 is empty in the case data, remove from list
#Renamen the week column from W to Week
week_names = [w.replace('W', 'Week') for w in list_of_weeks]


# loop to create one map per week
for week, week_name in zip(list_of_weeks, week_names):
    
    # create map
    ax = merged.plot(column=week, cmap='OrRd', figsize=(9,9), scheme='user_defined',
                 classification_kwds={'bins':[25,50,100,250,500,1000,3000]},
                 legend=True, linewidth=0.7, edgecolor='0.8')

    description = 'Covid-19 cases per 100.000 inhabitants \nover the past two weeks' # Title
    info_text = 'The map is created by Frederik Hass under supervision of Jamal Jokar Arsanjani as \npart of a research project at Department of Planning, Aalborg University called \n“AI4Covid: Artificial Intelligence for Covid-19 analysis” funded by the European Open Science Cloud.'
    ax.set_title(str(week_name), fontdict={'fontsize': 24}, loc='left')
    ax.annotate(description, xy=(0.335, 0.178), size=14, xycoords='figure fraction') #edit xy and size fo location and size of text
    ax.annotate(info_text, xy=(0.335, 0.125), size=8, xycoords='figure fraction')
    ax.set_axis_off()
    ax.set_xlim([-25, 35.6]) # x bottom and top mapview limits
    ax.set_ylim([33, 71.3]) # y bottom and top mapview limits
    ax.get_legend().set_bbox_to_anchor((0.25, 0.12)) # Specify legend placement (x,y)
    ax.get_figure()
     
    # this will save the figure as a png in the output path.
    filepath = os.path.join(output_path, week+'.png')
    chart = ax.get_figure()
    chart.savefig(filepath, dpi=150)

    
### MAKE GIF ###
images = []
for file in os.listdir(output_path):
    if file.endswith('.png'):
         file_path = os.path.join(output_path, file)
         images.append(imageio.imread(file_path))
imageio.mimsave(r"C:\path_fo_folder\EU_Covid-19_timeseries.gif", images, duration=0.85, subrectangles=True) # Duration = time per frame

