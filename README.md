# interactive-us-city-map

This project is an interactive US city map website that allows you to watch the cities in the United States grow (or shrink) from 1790-2020. The data points are all based on U.S. Census data from each decennial. On the site, you have the option to use a slider which will pick the year for you. For each data point, you can see the name of the city and the state it was or is in.  

Visit the site here: https://interactive-us-city-map.vercel.app/

# Data Sources:

All data is stored in public/datafiles. 

Data displayed on the site is coming from the file us_city_populations_1790-2020, which is a compilation of three different sources:
* 1790-2010_MASTER.csv: a compilation of US Census data for incorporated cities, towns, and villages that have had a population greater than 2500 at any point from 1790-2010, plus 300 CDPs, MCDs, Townships, and historical places
    * The data is found here, provided by Erik Steiner and the Center for Spatial and Textual Analysis: https://github.com/cestastanford/historical-us-city-populations
* us2021census.csv: a compilation of 2020 census data, including incorporated cities, towns, and villages, and CDPs in Hawaii, along with associated counties and coordinates.   
    * Data can be found here: https://www.kaggle.com/datasets/darinhawley/us-2021-census-cities-populations-coordinates
* cdps_over_25k_2020.csv: a compilation of US Census data for CDPs, cut off at populations greater than 25000.
    * The population data is retrieved through the US census API by a python script, specifically python_scripts/2020placefinder.py. 

Data from cdps_over_25k_2020.csv is added to us2021census.csv, then in turn merged with 1790-2010_MASTER.csv with the file python_scripts/data_merger.py. 

# Notes about the Data: 

Some data is spotty and is being fixed, such as:
* Old or historic cities which may have coordinate position issues 
* Cities which were in states which changed over time (ie, Wheeling, West Virginia was part of Virginia before West Virginia split off)
* Incomplete data, such as some CDPs or MCDs that do not have listed data from prior to 2020 (or are the opposite, and missing 2020 data). 

CDPs that are included are either already included in 1790-2010_MASTER.csv (explained in the Data Sources section), or they are in the 2020 census data with a population greater than 25000. 
The reason for the cut off at 25000 is that CDPs are often less centrally organized, so it is not proper to represent them similarly to cities. However, with populations greater than 25000, they are more similar to modern U.S. equivalents of cities, which are often very suburb-based and have significant amounts of population. 25000 is just the number to strike the balance so the data presented to the user isn't overwhelmed by CDPs.  

# Citations:

Jonathan Schroeder, David Van Riper, Steven Manson, Katherine Knowles, Tracy Kugler, Finn Roberts, and Steven Ruggles. IPUMS National Historical Geographic Information System: Version 20.0 [dataset]. Minneapolis, MN: IPUMS. 2025. http://doi.org/10.18128/D050.V20.0

Darin Hawley, hugequiz.com

U.S. Census Bureau and Erik Steiner, Spatial History Project, Center for Spatial and Textual Analysis, Stanford University