# Covid-19 - Tools and Notebooks for Geographic Analysis

## Animation of Infection Rates
Visualizing Covid-19 infection rates over time can be done in a single animation. The animation is made by loading a CSV file as a pandas dataframe and plotting each column with a world shapefile, the maps can then be combined in to a single gif. <br>
Infection data for the world animation is *the daily number of new reported COVID-19 cases and deaths worldwide* from the [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide)
![](Images/World_Covid-19_timeseries.gif)

Similar animations can likewise be made for regions in the European union or municipalities on a country level. 
![](Images/EU_Covid-19_timeseries.gif)   |  ![](Images/DK_Covid-19_timeseries_EN.gif)
:---:|:---:

Bi-weekly infection rates for the European Regions are from the *Data on the weekly subnational 14-day notification rate of new COVID-19 cases* from the [ECDC](https://www.ecdc.europa.eu/en/publications-data/weekly-subnational-14-day-notification-rate-covid-19). 
Data on daily municipal infection rates in Denmark are from [Statens Serum Institut (SSI)](https://covid19.ssi.dk/overvagningsdata/download-fil-med-overvaagningdata) <br> 

To ensure a fixed legend a dummy feature is included in the data and in the shapefile outside the mapview. Find shapefiles and CSV-files in the *Data* folder, the animation scripts are located in the *Notebook/Animations* folder.

## Exploratory Data Analysis (ESDA) - Spatial Autocorrelation
![](Images/EU_Hot_&_Cold_Spots.png)

![](Images/EU_Hot_&_Cold_Spots.png) | ![](Images/EU_Hot_&_Cold_Spots.png)
:---:|:---:

## Emerging Hotspot Analysis

## Machine Learning Prediction
