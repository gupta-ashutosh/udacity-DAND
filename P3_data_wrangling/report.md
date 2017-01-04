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
The sample.osm is ~75MB in size.

The way I perform the analysis task was :
1. Load the sample.osm data into python IDE rodeo by [yhat(newly launched)](https://www.yhat.com/products/rodeo) and analysed data manually line by line.
2. Use the [audit_streetname.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/audit_streetname.py) scipt to view the not so correct streetname. Also modified the aidit_streetname file such that small mistakes are corrected by audit file only(detailed of correction shared below).

##Issued found during analysis of dataset##

###Varying use of State and City names :###
There are several cities that comes under Delhi-NCR region.
All city names are written differently by different users, they need to be synchronised. Like,
delhi, DELHI, delhi. all need to be written as Delhi,
noida, NOIDA all need to be written as Noida. Also there is a regional term for market place, here we call it 
as _Bazaar_, but since this is originating in Hindi, which is native language in Delhi-NCR, varying and different spelling of 
_Bazaar_ exists, like Bazar or Bzar I want to this as _Bazaar_.

```python
    #this is part of mapping array
    "up" :"UP",
    "delhi":"Delhi",
    "Delhi.":"Delhi",
    "delhi": "Delhi",
    "noida":"Noida",
    "Noida," : "Noida",
    "NOIDA" : "Noida",
    "NAGAR" : "Nagar",
    "nagar" : "Nagar",
    "Bazar" : "Bazaar",
    "Rohini,Delhi" : "Rohini",
    "Pritampura" : "Pitampura",
    "south" : "South",
    "city" : "City",
    
...

split_name = name.split(" ")
new_name = []
for split in split_name:
    if split in mapping:
        new_name.append(mapping[split])
    else:
        new_name.append(split)
name = " ".join(new_name)
    
```
###Inconsistent use of sector, in NCR region places are divided into sector numbers, they are written as "Sector <sector number>". ..
But this pattern is written inconsistently across the dataset, 
like sector-14 or Sec-14, sec14. I want to remove any hyphen between them and keep a single space between them. Like "Sector <Number>"
Corrected code below

```python
sectorpattern = re.compile(r'\s*(Sector|Sec)\s*', re.IGNORECASE)

#updating sector names, wanted results in the form "Sector<space><number>"
if re.search(sectorpattern, name):
    name = name.lower().title()
    if "-" in name:
        name = re.sub('-',' ',name)
        name = re.sub(' +',' ',name)
    else:
        name = re.sub("Sector|sec", "Sector ", name, flags=re.I)
...
```

###Inconsistent use No., at some place No. is written as Number<number>, number<number>, No.<number>, all need to be consistent as No. <number> 

```python
numberPattern = re.compile( r'No(\.)?\s*[0-9]{1,2}\s*$' ,re.IGNORECASE)

if re.search(numberPattern, name):
    name = re.sub(r'No\.*\s*([0-9]{1,2})\s*$', r'No. \1', name, flags = re.I)
...

```

### Inconsistent address: "C - 99, Sector - 4, Sector 4 Noida, Block C, Sector 4, Noida => C" =>  ""99, Block C, Sector 4,Noida"
```python
matches = re.findall("Sector", name, re.DOTALL)
if len(matches) == 3 and ("Sector 4 Noida" in name or "Sector 4, Noida," in name):
    name = "C - 99, Sector 4, Block C, Noida"
    
```

### There were some issue regarding spelling and use of upper case for name of town or proper name of places
* "south" : "South"
* "extn" : "Extension"
* "Mg" : "Marg"
* "Pahargan" : "Pahar Ganj"
* "gali" : "Gali"
* "lothian" : "Lothian"
* "bangali" : "Bangali"

Such problem were resolved using mapping dicitonary only

```python 
split_name = name.split(" ")
new_name = []
for split in split_name:
    if split in mapping:
        new_name.append(mapping[split])
    else:
        new_name.append(split)
name = " ".join(new_name)

```

