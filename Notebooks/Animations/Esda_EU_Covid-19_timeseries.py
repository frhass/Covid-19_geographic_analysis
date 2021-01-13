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
from splot.esda import moran_scatterplot, plot_moran, lisa_cluster
from matplotlib import colors
import matplotlib.lines as mlines


print("Version info.")
print (sys.version_info)

# load in a shapefile
shp = r"C:\path_to_folder\ECDC_NUTS_Regions.shp"

shape_data = gpd.read_file(shp)

# check shapefile dataframe head
print("Shapefile Dataframe Columns:",shape_data.columns.values)


# Load in csv to merge with geodata
# Weekly data here https://www.ecdc.europa.eu/en/publications-data/weekly-subnational-14-day-notification-rate-covid-19
df = pd.read_csv(r"C:\path_to_folder\20201125_covid-19_EU_regions.csv", header=0, encoding="utf-8")
# check shapefile dataframe head
print("Covid-Cases Dataframe Columns:",df.columns.values)
 
 
# #pivot table
cases = df.pivot_table(values='rate_14_day_per_100k', index='nuts_code', columns='year_week')

# Join shapefile dataframe and the individual pivotet data tables
merged = shape_data.set_index('ECDC_NUTS').join(cases) 
merged.fillna(0, inplace=True)

merged.columns = merged.columns.astype(str)
#print("Merged:",merged.columns.values)


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


#Loop over each week and weekname for spatial autocorrelation 
for week, week_name in zip(list_of_weeks, week_names):

    #copy case dataframe
    sa_df = merged.filter([week,'REG_NAME','geometry'], axis=1)
    #print(week + "Dataframe:", sa_df)    

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
    m_local = Moran_Local(y, w)
    lisa = m_local.Is
    
    
    # set CRS
    sa_df = sa_df.to_crs("EPSG:3857")

    #Plot map
    fig, ax = plt.subplots(figsize=(9,9))
    lisa_cluster(m_local, sa_df, p=0.05, figsize = (9,9),ax=ax)
    description = 'Weekly Covid-19 Spatial Autocorrelation'
    info_text = 'Hot- and coldspots indicates clusters of high and low infection rates. \nDonuts are regions with low infection-rates sorrounded by areas with high infection-rates. \nDiamonds are regions with high infection-rates sorrounded by regions with low infection-rates'
    ax.set_title(str(week_name), fontdict={'fontsize': 22}, loc='left')
    ax.annotate(description, xy=(0.325, 0.140), size=14, xycoords='figure fraction')
    ax.annotate(info_text, xy=(0.325, 0.090), size=8, xycoords='figure fraction')

    #Legend items
    item1 = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="red", markersize=12)
    item2 = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="orange", markersize=12)
    item3 = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="lightblue", markersize=12)
    item4 = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="blue", markersize=12)
    plt.legend((item1, item2, item3, item4), ('Hotspot', 'Diamonds','Donuts','Coldspot')).set_bbox_to_anchor((0.240, 0.086)) #(x,y)
    plt.savefig(filepath, dpi=150)
  
    
    # ### MAKE GIF ###
    images = []
    for file in os.listdir(output_path):
      if file.endswith('.png'):
          file_path = os.path.join(output_path, file)
          images.append(imageio.imread(file_path))
imageio.mimsave(r"C:\path_to_folder\ESDA_EU_Covid-19_timeseries.gif", images, duration=0.85, subrectangles=True) # Duration = time per frame

