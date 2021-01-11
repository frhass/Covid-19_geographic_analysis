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

# set the filepath and load in a shapefile
fp = r"C:\path_fo_folder\world_iso_codes__from_ne_10m.shp"

shape_data = gpd.read_file(fp)
shape_data = shape_data.rename(columns={'iso31661a3': 'country_ISO'})

## test the shapefile data to see how it looks in a cmap
# plot = shape_data.plot(column='OBJECTID', cmap='OrRd')
# fig = plot.get_figure()


# Load in csv to merge with geodata
# Get Covid-19 data CSV file from here https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
df = pd.read_csv(r"C:\path_fo_folder\20201125_covid_countries.csv", header=0, encoding="utf-8")


# Convert dateRep to date format
df['date'] = pd.to_datetime(df['dateRep'], format='%d/%m/%Y')
df['date'] = df['date'].dt.date   # removing timestamp of date


# Calculate columative cases for each date per country 
df['Columative_Cases'] = df.sort_values('date')\
    .groupby(['countryterritoryCode']).cases.cumsum() - df.cases

# Add and calculate with cases per 100000 (prevalence)
df['Cases_per_100000'] = (df['Columative_Cases']/df['popData2019'])*100000


#pivot table
Cul_cases_prior14day_per100000 = df.pivot_table(values='Cumulative_number_for_14_days_of_COVID-19_cases_per_100000', index='countryterritoryCode', columns='date')


# Join shapefile dataframe and the individual pivotet data tables
data_table = Cul_cases_prior14day_per100000 
merged = shape_data.set_index('country_ISO').join(data_table) 
merged.fillna(0, inplace=True)

merged.columns = merged.columns.astype(str)

# Test plot
'''
### Plot a single map for test ###
ax = merged.plot(column='2020-08-01', cmap='OrRd', figsize=(16,9), scheme='user_defined',
                 classification_kwds={'bins':[25,50,100,200,300,400,500]},
                 legend=True, linewidth=0.8, edgecolor='0.8')
merged[merged.isna().any(axis=1)].plot(ax=ax, color='#fafafa', hatch='///')

description = 'Covid-19 cases per 100.00 inhabitants over the past 14 days'
info_text = 'Made by Frederik Hass - Aalborg University Copenhagen \nCovid-19 data from The European Centre for Disease Prevention and Control '
ax.set_title('2020-08-01', fontdict={'fontsize': 25}, loc='left')
ax.annotate(description, xy=(0.1, 0.11), size=20, xycoords='figure fraction')
ax.annotate(info_text, xy=(0.1, 0.045), size=12, xycoords='figure fraction')
ax.set_axis_off()
ax.set_xlim([-168, 180])
ax.set_ylim([-61, 89])
ax.get_legend().set_bbox_to_anchor((.14, .4))
ax.get_figure()
'''


### MAP STUFF ###

# Looping over all individual dates and creates a map for each

# Define output folder for maps 
output_path = r"C:\path_fo_folder\Maps"

# create list of dates - derived from merged dataframe 
merged_list = merged.columns.tolist()
list_of_dates = []

month_list = ['2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10','2020-11']
for month in month_list:
    for date in merged_list:
        item = month
        if item in date:
            list_of_dates.append(date)
        
#print("date list:", list_of_dates)


# start the for loop to create one map per date
for date in list_of_dates:
    
    # create map (org, figsize: 16,9)
    ax = merged.plot(column=date, cmap='OrRd', figsize=(13,6), scheme='user_defined',
                 classification_kwds={'bins':[25,50,100,250,500,1000,2000]},
                 legend=True, linewidth=0.55, edgecolor='0.8')
    merged[merged.isna().any(axis=1)].plot(ax=ax, color='#fafafa', hatch='///')

    description = 'Covid-19 cases per 100.00 inhabitants over the past 14 days' # Title
    info_text = 'Made by Frederik Hass - Aalborg University Copenhagen \nCovid-19 data from The European Centre for Disease Prevention and Control '
    info_text_en = 'The map is created by Frederik Hass under supervision of Jamal Jokar Arsanjani as part of a research project at \nDepartment of Planning, Aalborg University called “AI4Covid: Artificial Intelligence for Covid-19 analysis” funded by the European Open Science Cloud.'
    ax.set_title(str(date), fontdict={'fontsize': 23}, loc='left')
    ax.annotate(description, xy=(0.09, 0.09), size=17, xycoords='figure fraction') #edit xy and size fo location and size of text
    ax.annotate(info_text_en, xy=(0.09, 0.04), size=7, xycoords='figure fraction')
    ax.set_axis_off()
    ax.set_xlim([-168, 180]) # x bottom and top mapview limits
    ax.set_ylim([-61, 89]) # y bottom and top mapview limits
    ax.get_legend().set_bbox_to_anchor((.14, .42)) # Specify legend placement (x,y)
    ax.get_figure()
    
    # this will save the figure as a png in the output path.
    filepath = os.path.join(output_path, date+'.png')
    chart = ax.get_figure()
    chart.savefig(filepath, dpi=135)

    
### MAKE GIF ###
images = []
for file in os.listdir(output_path):
    if file.endswith('.png'):
        file_path = os.path.join(output_path, file)
        images.append(imageio.imread(file_path))
imageio.mimsave(r"C:\path_fo_folder\World_Covid-19_timeseries.gif", images, duration=0.23, subrectangles=True) # Duration = time per frame