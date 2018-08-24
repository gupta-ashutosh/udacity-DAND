#Wrangle OpenStreetMap Data#

**Author - Ashutosh Gupta**

**Date - 31st Jan, 2017**

##Area Selected##

I have selected area of [Delhi-NCR (national capital region), Delhi, India](https://en.wikipedia.org/wiki/National_Capital_Region_(India)) , where I live. I have choosen this area because of mainly 2 reasons, 
* I Know this area as I live here, so it will be easier for me to see the issues in street names, road names etc.
* Wanted to explore more about the area, in terms of numbers.

[Dataset](https://mapzen.com/data/metro-extracts/metro/new-delhi_india/).
This is the dataset of Delhi-NCR.


##Identifying Problem##

My datset new-delhi_india.osm is of size 746.7MB in size, I took out a sample datset sample.osm, from the main dataset using the [small_OSM_generator.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/small_OSM_generator.py) script.
The sample.osm is ~75MB in size.

The way I perform the analysis task was :
* Load the sample.osm data into python IDE rodeo by [yhat(newly launched)](https://www.yhat.com/products/rodeo) and analysed data manually line by line.
* Use the [audit_streetname.py](https://github.com/gupta-ashutosh/udacity-DAND/blob/master/P3_data_wrangling/audit_streetname.py) scipt to view the not so correct streetname. Also modified the audit_streetname file such that small mistakes are corrected by audit file only(detailed of correction shared below).

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
mapping = {
    "Rd" : "Road",
    #this is part of mapping array
    "up" :"UP",
    "delhi":"Delhi",
    "Delhi.":"Delhi",
    "delhi": "Delhi",
    "noida":"Noida",
    "Noida," : "Noida",
    "NOIDA" : "Noida",
...

...
split_name = name.split(" ")
new_name = []
for split in split_name:
    if split in mapping:
        new_name.append(mapping[split])
    else:
        new_name.append(split)
name = " ".join(new_name)
    
return name
```
###Inconsistent use of sector, in NCR region places are divided into sector numbers, they are written as "Sector <sector number>". ..
But this pattern is written inconsistently across the dataset, 
like sector-14 or Sec-14, sec14. I want to remove any hyphen between them and keep a single space between them. Like "Sector <Number>"
Corrected code below

```python
sectorpattern = re.compile(r'\s*(Sector)\s*(-)\s*', re.IGNORECASE)
sectorsubpattern1 = re.compile(r'(Sector-)\w*', re.IGNORECASE)
sectorsubpattern2 = re.compile(r'(Sector)\s(-)\w*', re.IGNORECASE)
sectorsubpattern3 = re.compile(r'(Sector)\s(-)\s\w*', re.IGNORECASE)
sectorsubpattern4 = re.compile(r'(Sector-)\s\w*', re.IGNORECASE)
sectorsubpattern5 = re.compile(r'(Sector)\s(-)\w*$', re.IGNORECASE)

if re.search(sectorpattern, name):
        if re.search(sectorsubpattern1, name):
            name = name.replace("Sector-", "Sector ")
        elif re.search(sectorsubpattern2, name):
            name = name.replace("Sector -", "Sector ")
        elif re.search(sectorsubpattern3, name):
            name = name.replace("Sector - ", "Sector ")
        elif re.search(sectorsubpattern5, name):
            name = name.replace("Sector -", "Sector ")
        else:
            name = name.replace("Sector- ", "Sector ")

...

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

#### problem with postcode
There were problems with postcodes as well, In India we have 6 digit postcodes, without any space or gap between any of the digits, some of postcodes were having space between digits,
ex : 110 067 and 110 021, they need to be put like this, 
110 067  =>  110067
110 021  =>  110021

below code is used to correct the defect above

```python
postcode = re.sub(r'(\d+)\s+(?=\d)', r'\1', postcode)
```

There were some postcode that were not of 6 digit length, like :
2242, 10089

To correct them I need to scan through the OSM file and look for this postcode's street and other details and based on these details have to figure out the correct postcode.

```
<tag k="addr:street" v="Palam Vihar" />
<tag k="addr:country" v="IN" />
<tag k="addr:postcode" v="122001" />
<tag k="addr:housenumber" v="2445" />

<tag k="addr:street" v="Palam Vihar" />
<tag k="addr:country" v="IN" />
<tag k="addr:postcode" v="2242" />
<tag k="addr:housenumber" v="2409" />
```
As we can see in the example above the postcode "2242" might be written as housenumber.
We can see the correct postcode is "122001"

```
2242  =>  122001
```

Similarly other such postcodes were corrected, 
``` 10089  =>  110085```

There were one postcode which was having one extra character 'v' attached in the end
110031v, they should have been changed to:
``` 110031v  =>  110031 ```




## Parsing OSM and converting to CSV
After Identifying issues and there solutions above, it was time to convert the corrected OSM data into CSV file.

During convertion from OSM to CSV I have made the above mentioned corrections and then saved the data into CSV file for further exploration.

audit_streetname.py is the python script which contains the auditing and correction functions and write_data.py is the script which contains the writing to CSV file code, I have imported the audit_streetname into write_data and used its audit and cleaning function and then saved the OSM data into CSV data.

Below is the few line of code snippet

```python
import audit_streetname as audit
for tag in element.iter("tag"):
  node_tags = {}
  tag_key = tag.attrib["k"]
  value = tag.attrib["v"]
  ...
  
  if audit.is_street_name(tag):
    value = audit.update_name(value, audit.getStreetMapping())
           
  if audit.is_postal(tag):
    value = audit.update_postcode(value, audit.getPostCodeMapping())
  ...  
```


##Exporting to Sqlite3 Database
After converting the OSM data to csv files, I have created a database, "newdelhi_ncr_osm.db".

I have written a python script to directly connect to this databse and create 5 required tables and import the CSV files into required tables. "create_tables_sqlite3.py" is the name of the script which will do all the task.

Also this can be done through manual coding also.
Exact steps are provided in "DB_instructions.txt" file.
Code for exporting csv data to Sqlite3 database
```sql
>.mode csv
>.import nodes.csv nodes
```

##DataBase details : 
After importing into Sqlite3, 5 tables were created:
* nodes -- 3386572 rows
* nodes_tags -- 38577 rows
* ways -- 690993 rows
* ways_tags -- 753356 rows
* ways_nodes -- 4191145 rows

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
```
"ICICI Bank",15
"HDFC Bank",14
"State Bank of India",13
"Punjab National Bank",9
"Axis Bank",6
```

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
1. More wheel chairs are required at public places like, supermarkets, shops, metros, hospitals etc.
2. More wheelchairs are available but no one has made that enrty in the data, thats why we are getting
    the low count
    
The benefit of availing this would be that differently abled people won't face problem in dealing at public places. 
Since there are not enough services available for them, they are not coming to these places or we can say they are dependent on other people for their work, if we provide more such services, such people can also become self sufficient and can do some amount of their own work by themselves.

The challenges availing these services are that:
1. one need to know exact amount of differently-abled or elderly people in all the areas and accordingly provide services.
2. Also for availing these services all the hospitals, banks, shopping complexes etc need extra staff.
3. Government and other NGO's have to take responsibility for providing funds. 

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
```
We can see that the populations are not correct. And the people entering these informtion might not have the exact number or they have entered it by mistake.


##Conslusion
Delhi-NCR OSM data is a big data, since so many users have contributed to it and are still contributing, it has become messy. Messy in terms of keeping consistency in names of amenities, names of streets and etc. 
Same thing enetered by different users will have different version, which we need to handle
programatically. But the data is very useful and clean enough for our exploration purpose, and even after I live in this area I learned so many new things about my locality.

I learned a great about OSM data, its structure and what is the relation between nodes, ways, and tags.
Also I learned how to go about auditing your data and convert it into database tables.

And lastly I learned what kind of problems are faced by programmers who work with real life data like OSM data, which is generated and entered by real users. Now onwards I would also like to contribute to OSM and any such open source data.
>>>>>>> c1011bdfa23e349aaa7d503cb9a7a08a9ffa6a62
