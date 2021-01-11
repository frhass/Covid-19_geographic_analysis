# -*- coding: utf-8 -*-
"""
@author: Frederik Hass, Aalborg University - Copenhagen
email: frederiksh@plan.aau.dk
github repository: https://github.com/frhass/Covid-19_geographic_analysis 
"""


# load libraries
import pandas as pd
import geopandas as gpd
import imageio
import os
import sys


print("Version info.")
print (sys.version_info)

### PREPARE DATA ###

# load in a shapefile
fp = r"C:\path_to_folder\gadm36_DNK_2.shp"
 
shape_data = gpd.read_file(fp)


# Drop unnescessary columns
shape_data.drop(['GID_0', 'NAME_0', 'GID_1', 'NAME_1', 'GID_2', 'NL_NAME_1', 'VARNAME_2', 'NL_NAME_2', 'CC_2', 'HASC_2'], axis=1, inplace=True)


# Load in csv file with Covid case numbers
# Get Covid-19 data CSV file from here https://www.ssi.dk/sygdomme-beredskab-og-forskning/sygdomsovervaagning/c/covid19-overvaagning/arkiv-med-overvaagningsdata-for-covid19
df = pd.read_csv(r"C:\path_to_folder\20201207_Municipality_cases_time_series.csv", header=0, delimiter=";", encoding="utf-8")
df = df.reset_index()
df = df.rename(columns={'date_sample': 'date'})
df = df.set_index('date')


# 14 day calculation
df_14day = df.rolling(14, min_periods=1).sum()
df_14day = df_14day.T

merged = shape_data.set_index('NAME_2').join(df_14day) 
merged.fillna(0, inplace=True)
merged.drop(['TYPE_2', 'ENGTYPE_2'], axis=1, inplace=True)
print('merged dataframe:', merged)


# Test plot
'''
with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
    print(merged)



ax = merged.plot(column='2020-05-02', cmap='OrRd', figsize=(16,9), scheme='user_defined',
                 classification_kwds={'bins':[25,50,75,100,250,500,1000]},
                legend=True, linewidth=0.8, edgecolor='0.8')


description = 'Antal Covid-19 smittede\nakkumuleret over 14 dage'
info_text = 'Lavet af Frederik Hass\nAalborg Universit København\nCovid-19 data fra\nStatens Serums Institut'
ax.set_title('2020-05-02', fontdict={'fontsize': 25}, loc='left')
ax.annotate(description, xy=(0.87, 0.85), size=19, xycoords='figure fraction', ha='right')
ax.annotate(info_text, xy=(0.87, 0.51), size=10, xycoords='figure fraction', ha='right')
ax.set_axis_off()
ax.set_xlim([7.95, 15.3])
ax.set_ylim([54.5, 57.8])
ax.get_legend().set_bbox_to_anchor((0.881, 0.905))
ax.get_figure()


with pd.option_context('display.max_rows', None, 'display.max_columns', None): 
    print(merged['2020-05-02'], merged['geometry'])
'''
 

### MAP STUFF ###
# Looping over all individual dates and creates a map for each

# Define output folder for maps 
output_path = r"C:\path_to_folder\Maps"

# create a list of dates - derived from merged dataframe 
merged_list = merged.columns.tolist()
#print('Merged_list', merged_list)
list_of_dates = []

month_list = ['2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10', '2020-11','2020-12']
for month in month_list:
    for date in merged_list:
        item = month
        if item in date:
            list_of_dates.append(date)
            print(date)
        
#print("date list:", list_of_dates)



# start the for loop to create one map per date
for date in list_of_dates:
      
    # create map
    ax = merged.plot(column=date, cmap='OrRd', figsize=(15,8), scheme='user_defined',
                     classification_kwds={'bins':[10,25,50,100,250,500,1000,2000,4000]},
                     legend=True, linewidth=0.7, edgecolor='0.8')
        
        
    description = 'Covid-19 case numbers \nover the past two weeks'  # Title 
    info_text = 'The map is created by Frederik Hass under supervision of Jamal Jokar Arsanjani as part of a research project at \nDepartment of Planning, Aalborg University called “AI4Covid: Artificial Intelligence for Covid-19 analysis” funded by the European Open Science Cloud.'
    ax.set_title(str(date), fontdict={'fontsize': 25}, loc='left')
    ax.annotate(description, xy=(0.825, 0.85), size=19, xycoords='figure fraction', ha='right') #edit xy and size fo location and size of text
    ax.annotate(info_text, xy=(0.09, 0.07), size=9, xycoords='figure fraction', ha='left')
    ax.set_axis_off()
    ax.set_xlim([7.95, 15.3]) # x bottom and top mapview limits
    ax.set_ylim([54.5, 57.8]) # y bottom and top mapview limits
    ax.get_legend().set_bbox_to_anchor((0.910, 0.925)) # Specify legend placement (x,y)
    ax.get_figure()
    
    # this will save the figure as a png in the output path.
    filepath = os.path.join(output_path, date+'.png')
    chart = ax.get_figure()
    chart.savefig(filepath, dpi=145)

    
### MAKE GIF ###
images = []
for file in os.listdir(output_path):
    if file.endswith('.png'):
        file_path = os.path.join(output_path, file)
        images.append(imageio.imread(file_path))
imageio.mimsave(r"C:\path_to_folder\DK_Covid-19_timeseries_EN.gif", images, duration=0.23, subrectangles=True) # Duration = time per frame