#Wrangle OpenStreetMap Data#

**Author - Ashutosh Gupta**

**Date - 25th Dec, 2016**

##Area Selected##

I have selected area of [Delhi-NCR (national capital region), Delhi, India](https://en.wikipedia.org/wiki/National_Capital_Region_(India)) , where I live. I have choosen this area because of mainly 2 reasons, 
1. I Know this area as I live here, so it will be easier for me to see the issues in street names, road names etc.
2. Wanted to explore more about the area, in terms of numbers.

[Dataset](https://mapzen.com/data/metro-extracts/metro/new-delhi_india/).
This is the dataset of Delhi-NCR.


##Identifying Problem##

My datset new-delhi_india.osm is of size 746.7MB in size, I took out a sample datset sample.osm, from the main dataset using the [small_OSM_generator.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/small_OSM_generator.py) script.
The sample.osm is ~75MB in size.

The way I perform the analysis task was :
1. Load the sample.osm data into python IDE rodeo by [yhat(newly launched)](https://www.yhat.com/products/rodeo) and analysed data manually line by line.
2. Use the [audit_streetname.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/audit_streetname.py) scipt to view the not so correct streetname. Also modified the aidit_streetname file such that small mistakes are corrected by audit file only(detailed of correction shared below).

## Issued found during analysis of dataset##

#### Varying use of State and City names :
There are several cities that comes under Delhi-NCR region.
All city names are written differently by different users, they need to be synchronised. Like,
delhi, DELHI, delhi. all need to be written as Delhi,
noida, NOIDA all need to be written as Noida. 
Also there is a regional term for market place, here we call it 
as _Bazaar_, but since this is originating in Hindi, which is native language in Delhi-NCR, varying and different spelling of 
_Bazaar_ exists, like Bazar or Bzar I want to keep this as _Bazaar_.

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
#### Inconsistent use of sector
In NCR region places are divided into sector numbers, they are written as "Sector <sector number>"
But this pattern is written inconsistently across the dataset, 
like sector-14 or Sec-14, sec14. I want to remove any hyphen between them and keep a single space between them. 
Like "Sector <Number>"

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

####Inconsistent use No., at some place No. is written as Number<number>, number<number>, No.<number>, all need to be consistent as No. <number> 
* number | Number => No.
* No | no | No. => No.
```python
numberPattern = re.compile( r'No(\.)?\s*[0-9]{1,2}\s*$' ,re.IGNORECASE)

if re.search(numberPattern, name):
    name = re.sub(r'No\.*\s*([0-9]{1,2})\s*$', r'No. \1', name, flags = re.I)
...

```

#### Inconsistent address: 
* "C - 99, Sector - 4, Sector 4 Noida, Block C, Sector 4, Noida => C"  ""99, Block C, Sector 4,Noida"
```python
matches = re.findall("Sector", name, re.DOTALL)
if len(matches) == 3 and ("Sector 4 Noida" in name or "Sector 4, Noida," in name):
    name = "C - 99, Sector 4, Block C, Noida"
    
```

#### There were some issue regarding spelling and use of upper case for name of town or proper name of places
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
#### non-ASCII charcter problem:
* One particular sector was having non ascii character which was causing problem, I have to convert it first into unicharacter and then convert back to ASCII.
```python
name = re.sub(unichr(8211), "-", name)
name = name.encode('ascii','ignore')
```

## Parsing OSM and converting to CSV
After handling few issues, I started converting OSM data file into CSV files using a [script]().
Below is the main converting function used in the script : 

```python
    NODES_PATH = "nodes.csv"
    NODE_TAGS_PATH = "nodes_tags.csv"
    WAYS_PATH = "ways.csv"
    WAY_NODES_PATH = "ways_nodes.csv"
    WAY_TAGS_PATH = "ways_tags.csv"

    # Make sure the fields order in the csvs matches the column order in the sql table schema
    NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
    NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
    WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
    WAY_NODES_FIELDS = ['id', 'node_id', 'position']

    if element.tag == 'node':
        idd = element.attrib['id']
        lat = element.attrib['lat']
        lon = element.attrib['lon']
        user = element.attrib['user']
        uid = element.attrib['uid']
        version = element.attrib['version']
        changeset = element.attrib['changeset']
        timestamp = element.attrib['timestamp']
    
        node_attribs["id"] = idd
        node_attribs["lat"] = lat
        node_attribs["lon"] = lon
        node_attribs["user"] = user
        node_attribs["uid"] = uid
        node_attribs["version"] = version
        node_attribs["changeset"] = changeset
        node_attribs["timestamp"] = timestamp
        
        for tag in element.iter("tag"):
            node_tags = {}
            value = tag.attrib["v"]
            if re.search(PROBLEMCHARS, tag.attrib["k"]):
                continue
            
            key_split = tag.attrib["k"].split(":")
            if len(key_split) == 1:
                key = tag.attrib["k"]
                type_t = default_tag_type
            else:
                type_t = key_split[0]
                del key_split[0]
                key = ":".join(key_split)
                # key = key_split
                
            node_tags['id'] = idd
            node_tags['key'] = key
            node_tags['value'] = value
            node_tags['type'] = type_t
            
            tags.append(node_tags)
        
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        idd = element.attrib["id"]
        way_attribs["id"] = idd
        way_attribs["user"] = element.attrib["user"]
        way_attribs["uid"] = element.attrib["uid"]
        way_attribs["version"] = element.attrib["version"]
        way_attribs["changeset"] = element.attrib["changeset"]
        way_attribs["timestamp"] = element.attrib["timestamp"]
        
        for tag in element.iter("tag"):
            way_tags = {}
            value = tag.attrib["v"]
            if re.search(PROBLEMCHARS, tag.attrib["k"]):
                continue
            
            key_split = tag.attrib["k"].split(":")
            if len(key_split) == 1:
                key = tag.attrib["k"]
                type_t = default_tag_type
            else:
                type_t = key_split[0]
                del key_split[0]
                key = ":".join(key_split)
                
            way_tags['id'] = idd
            way_tags['key'] = key
            way_tags['value'] = value
            way_tags['type'] = type_t
            
            tags.append(way_tags)
        
        nd_index = 0
        for nd in element.iter("nd"):
            way_nd = {}
            way_nd['id'] = idd
            way_nd['node_id'] = nd.attrib['ref']
            way_nd['position'] = nd_index 
            nd_index += 1
            
            way_nodes.append(way_nd)
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

```
The full code with file is uploaded also.

##Exporting to Sqlite3 Database
After converting the OSM data to csv files, I have created a database, "new_delhi_ncr.db", and created 5 tables.

Followed by importing the csv file into required tables.
Exact steps are provided in [DB_instructions.txt]() file.
Code for exporting csv data to Sqlite3 database
```sql
>.mode csv
>.import nodes.csv nodes
```

##DataBase details : 
After importing into Sqlite3, 5 tables were created:
1. nodes -- 3386572 rows
2. nodes_tags -- 38577 rows
3. ways -- 690993 rows
4. ways_tags -- 753356 rows
5. ways_nodes -- 4191145 rows

query to get the row count :
```sql
SELECT count(*) FROM nodes;
```

###Data Details:
```sql
*new-delhi_india.osm - 746.6MB
*newdelhi_ncr_osm.db - 475.2MB
*nodes.csv - 282.MB
*nodes_tags.csv - 1.4MB
*ways.csv - 41.9MB
*ways_nodes.csv - 100.MB
*ways_tags.csv - 25.2MB
```
###Number of unique users:
```sql
SELECT COUNT(DISTINCT(temp.uid)) FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) temp;
```
1200

###Number of nodes:
```sql
SELECT COUNT(*) FROM nodes;
```
3386572

###Number of ways:
```sql
SELECT COUNT(*) FROM ways;
```
690993

###Top 5 contibuting users:
```sql
SELECT temp.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) temp
GROUP BY temp.user
ORDER BY num DESC
LIMIT 5;
```

```
Oberaffe,254699
premkumar,164963
saikumar,160132
Naresh08,137145
anushap,134226
```

###Date when last update was made:
```sql
SELECT timestamp FROM nodes UNION SELECT timestamp From ways ORDER BY timestamp desc LIMIT 1;
```
2016-12-21T12:35:31Z

###When and who made the first update:
```sql
SELECT user,timestamp FROM nodes UNION SELECT user,timestamp From ways ORDER BY timestamp LIMIT 1;
```
H_S_Rai,2007-09-23T02:35:38Z

###Different religion's worship places and their count:
India is multi cultured and multi region country, same applies for Delhi-NCR too, lets see how 
many different types of worship places are here:

```sql
SELECT temp.value, COUNT(*) AS worship_place_count FROM (SELECT key,value FROM nodes_tags WHERE key="religion" UNION ALL SELECT key,value FROM ways_tags WHERE key="religion") temp
group by temp.value order by worship_place_count DESC;
```

```
hindu,147
muslim,50
christian,34
sikh,32
jain,6
buddhist,3
bahai,1
zoroastrian,1
```
Results are as expected, In India ~80% people practice Hindusim ([wiki page](https://en.wikipedia.org/wiki/Religion_in_India)), followed by ~14% Islam, and 3rd comes Christianity (~6%). 

###Most famous banks:
Delhi-NCR is a very big city, it will have several banks and each bank will have several branches,
lets explore the banks and there numbers.
```sql
select nt.value, count(*) from nodes_tags nt join
(select id,key,value from nodes_tags where value="bank") temp
on temp.id=nt.id
where nt.key="name"
group by nt.value 
order by count(*) desc
LIMIT 5;
```
"ICICI Bank",15
"HDFC Bank",14
"State Bank of India",13
"Punjab National Bank",9
"Axis Bank",6

The data above displayed the banks and their branch counts, but this seems very odd that the most popular bank has only 15 branches.
To explore more I removed the Limit 5 condition,
```sql
select nt.value, count(*) from nodes_tags nt join
(select id,key,value from nodes_tags where value="bank") temp
on temp.id=nt.id
where nt.key="name"
group by nt.value 
order by count(*) desc
```
```
"ICICI Bank",15
"HDFC Bank",14
"State Bank of India",13
"Punjab National Bank",9
"Axis Bank",6
"Standard Chartered Bank",4
HDFC,3
HSBC,3
"Bank of India",2
"Deutsche Bank",2
ICICI,2
"Indian bank",2
"State Bank Of India",2
"Union Bank of India",2
"Vijaya Bank",2
"ABN Amro",1
"AXIS Bank",1
"Andhra Bank",1
Axis,1
"Bank Of Baroda",1
"Bank Of India",1
"Bank of Baroda",1
"Bank of Baroda, Mayur Vihar Phase 3",1
"Bank of Maharashtra, Mayur Vihar Phase 3",1
"Barclays Bank",1
"CITI Bank",1
"Canara Bank, Bhagwan Das Road",1
"Canara Bank, Patparganj Branch",1
"Canara bank",1
"Central Bank of India",1
"Central bank of india",1
Citibank,1
"DCB Bank",1
"Federal Bank",1
"HDFC Bank & ATM",1
"HDFC Bank ATM",1
"HDFC Bank and ATM",1
"HDFC Bank atm",1
"HDFC Bank, Bilaspur",1
"HDFC bank",1
"Hdfc bank",1
"ICICI Bank Ltd",1
"ICICI, SBI, Citibank,",1
ICICI-alaknanda,1
"IDBI Bank",1
"Indian Bank",1
"Indian Overseas Bank",1
IndusInd,1
"IndusInd Bank",1
"Kotak Bank",1
"Kotak Mahindra Bank",1
"Lord Krishna Bank",1
"OBC Bank",1
"Okhla Industrial Estate, Phase 3 Branch",1
...

```
After removing the limit 5 condition, we can see that bank names are written in many ways thats 
why we were getting very less count. This is one improvement that this OSM data required.
All the bank names need to be same.
Such improvements can be done during auditing phase when we are progrmatically reading the OSM file,
and it can be done when data already exported to database.





###Wheelchair accessibilities:
```sql
select count(*) from nodes_tags;
```
38577

```sql
select count(*) from nodes_tags where key="wheelchair" AND value="yes";
```
57

```python 
57/80 = 0.001477
```
We can see that wheelchairs are available around 0.14% which seems very low, there are 2 sides of
it,
1. More wheel chairs are required at pblic places like, supermarkets, shops, metros, hospitals etc.
2. More wheelchairs are available but no one has made that enrty in the data, thats why we are getting
    the low count

###Postal Codes
```sql
SELECT * FROM nodes_tags WHERE key LIKE "%post%";
```
```
245765005,postal_code,121004,regular
245765268,postal_code,121001,regular
245765445,postal_code,203202,regular
245765633,postal_code,110030,regular
245766462,postal_code,124507,regular
245766747,postal_code,201206,regular
245767001,postal_code,201204,regular
245767302,postal_code,250500,regular
266599701,postcode,122001,addr
308894056,postcode,110003,addr
312921216,postcode,110030,addr

...
```

This returns all the records where key is postcode, but it also returns records where 
key is postal_code. This means postcode is written incorrectly at some places.

To check is there any other different name used for postcode
```sql
SELECT key, count(*) FROM nodes_tags WHERE key LIKE "%post%" GROUP BY key;
```
```
postal_code,21
postcode,539
```
We can see there is one another name for postcode which postal_code, we need to update the "postal_code" to "postcode".
Corrections made:
```sql
UPDATE nodes_tags set key = "postcode" where key = "postal_code";
SELECT * FROM nodes_tags WHERE key LIKE "%post%";
```
```
245765005,postcode,121004,regular
245765268,postcode,121001,regular
245765445,postcode,203202,regular
245765633,postcode,110030,regular
245766462,postcode,124507,regular
245766747,postcode,201206,regular
245767001,postcode,201204,regular
245767302,postcode,250500,regular
266599701,postcode,122001,addr
308894056,postcode,110003,addr
312921216,postcode,110030,addr

...
```
We can see that correction are updated.

Further exploration in the postcode gives some more unexpected errors, 
like : one of the postcode was only 3 digit "2242", and it was repeated at several places.

```
735999858,postcode,122001,addr
735999859,postcode,2242,addr
735999861,postcode,122001,addr
735999862,postcode,2242,addr
735999863,postcode,122001,addr
735999864,postcode,122001,addr
735999866,postcode,2242,addr
735999867,postcode,122001,addr
...
```
By using the id of one of the row with postcode = 2242

```sql
SELECT * FROM nodes_tags WHERE id = 735999866;
```
The result was : 
```
735999866,city,Gurgaon,addr
735999866,street,"Palam Vihar",addr
735999866,country,IN,addr
735999866,postcode,2242,addr
735999866,housenumber,2486,addr
```
So postcode should remain same for same street, like for street "Palam Vihar", postcode would be same.


```sql
select * from nodes_tags where id in
(select id from nodes_tags where key = "street" and value = "Palam Vihar") 
AND key = "postcode";
```
```
734837126,postcode,122001,addr
734837127,postcode,122001,addr
734837873,postcode,122001,addr
734837875,postcode,122001,addr
734837877,postcode,122001,addr
```
Using above query I found the real postcode value for Palam Vihar, which was 122001

```sql
UPDATE nodes_tags SET VALUE = "122001" WHERE key = "postcode" AND value = "2242";
```
Above query will update the required postcode.


##Additional Ideas/Information:
*In the above section we saw some interesting queries. I want to draw attention to few of the queries like, wheelchair count.
Wheelchairs are necessary at places like hospitals, supermarkets, railway stations, metro stations.
What we see from the data is that there are very few number of wheelchairs available, which seems 
very unfair. But this could be due to the fact that people haven't made any enrty regarding wheelchairs.
So we need to make sure 2 things:
1. Correctly add the number of wheelchair status at various places
2. Increase the wheelchairs at required spots and make them available to needy people.

For first point a survey could be made asking about the various facilities including wheelchairs and
then adding those records in the OSM data.
For second point government officials need to see these stats and work on it.


*While Exploring I noticed, one user has entered name of the Delhi in 124 different languages/ways, 
which is quite amazing that people so many names of a single city in different languages.
```sql
select count(*) from nodes_tags where id = 16173236 and type = "name";
```
124

```sql

name of the user
select user from nodes where id = 16173236;
```
andi2911

*Also I noticed in the dataset that population is correctly enetered. Like the population of delhi is given 249998, which is totally
wrong.
We need some way of connecting OSM data to wikipedia or some similar resource so that these information get updated regularly.
```sql
SELECT nodes_tags.value, temp.value FROM nodes_tags join (SELECT * FROM nodes_tags WHERE key = "population")temp ON temp.id = nodes_tags.id 
AND nodes_tags.key="name";
```

```
"New Delhi",249998
Ballabgarh,1000
Faridabad,100000
Sikandarabad,50000
Bahadurgarh,5000
Muradnagar,5000
Sohna,5000
Kharkhauda,1000
Pataudi,1000
Baghpat,5000
Bhiwadi,104800
Ghaziabad,500000
Delhi,11008000
Kharkhoda,18758
"Sector B, Pocket 7",750
"Bilaspur Chowk",2000
Dharuhera,45000
"Industrial Modern Township Manesar",2000
"Safeda Basti",3000
```
We can see that the populations are not correct.


##Conslusion
Delhi-NCR OSM data is a big data, since so many users have contributed to it and are still contributing,
it has become messy. Messy in terms of keeping consistency in names of amenities, names of 
streets and etc. Same thing enetered by different users will have different version, which we need to handle
programatically. But the data is very useful and clean enough for our exploration purpose, and even after I
live in this area I learned so many new things about my locality.

I learned a great about OSM data, its structure and what is the relation between nodes, ways, and tags.
Also I learned how to go about auditing your data and convert it into database tables.

And lastly I learned what kind of problems are faced by programmers who work with real life data like OSM data,
which is generated and entered by real users. Now onwards I would also like to contribute to OSM and 
any such open source data.