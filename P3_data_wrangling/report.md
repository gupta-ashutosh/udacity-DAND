#Wrangle OpenStreetMap Data#

**Author - Ashutosh Gupta**

**Date - 25th Dec, 2016**

##Area Selected##

I have selected area of [Delhi-NCR (national capital region), Delhi, India](https://en.wikipedia.org/wiki/National_Capital_Region_(India)) , where I live. I have choosen this area because of maily 2 reasons, 
1. I Know this area as I live here, so it will be easier for me to see the issues in street names, road names etc.
2. Wanted to explore more about the area I live so that I have knowledge about it.

[Dataset](https://mapzen.com/data/metro-extracts/metro/new-delhi_india/).
This is the dataset of Delhi-NCR.


##Identifying Problem##

My datset new-delhi_india.osm is of size 746.7MB in size, i took out a sample datset sample.osm, from the main dataset using the [small_OSM_generator.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/small_OSM_generator.py) script.
The sample.osm is 251.7MB.

The way I perform the analysis task was :
1. Load the sample.osm data into python IDE rodeo by [yhat(newly launched)](https://www.yhat.com/products/rodeo) and analysed data manually.
2. Use the [audit_streetname.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/audit_streetname.py) scipt to view the not so correct streetname. Also modified the aidit_streetname file such that small mistakes are corrected by audit file only(detailed of correction shared below).

##Issued found during analysis of dataset##

###varying use of State name :###
There are several cities that comes under Delhi-NCR region.
All city names are written differently by different users, they need to be synchronised. Like,
delhi, DELHI, delhi. all need to be written as Delhi,
noida, NOIDA all need to be written as Noida.
