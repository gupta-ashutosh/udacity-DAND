import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict


OSMFILE = 'sample.osm'
# OSMFILE = 'new-delhi_india.osm'

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

postals_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Road", "College", "School", "University","Delhi", 
            "Enclave", "footpath","Marg", "nagar", "Chowk", "Bagh",
            "Complex", "Estate", "Expressway", "Flyover", "Ghaziabad", "road", "Vihar",
            "gurgaon", "hotel", "garden","colony", "Nagar", "Lok", "Market"]

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

sectorpattern = re.compile(r'\s*(Sector|Sec)\s*', re.IGNORECASE)

numberPattern = re.compile(r'N\.?\s*[0-9]{1,2}\s*$' ,re.IGNORECASE)

def getStreetMapping():
    """ function to return the mapping list for streetname, this is the list of corrections/changes which is frequently occuring in dataset"""

    mapping = {
        "Rd" : "Road",
        "up" :"UP",
        "delhi":"Delhi",
        "Delhi.":"Delhi",
        "delhi": "Delhi",
        "noida":"Noida",
        "Noida," : "Noida",
        "NOIDA" : "Noida",
        "gurgaon" : "Gurgaon",
        "NAGAR" : "Nagar",
        "nagar" : "Nagar",
        "Bazar" : "Bazaar",
        "no" : "No",
        "number" : "No",
        "south" : "South",
        "north" : "North",
        "city" : "City",
        "11'" : "11",
        "sec" : "Sector",
        "Sec" : "Sector",
        "sector":"Sector",
        "SECTOR":"Sector",
        "UP)" : "UP",
        "Rohini,Delhi" : "Rohini",
        "Pritampura" : "Pitampura",
        "extn" : "Extension",
        "i.p.extension" : "I.P. Extension",
        "I. P. Extension" : "I.P. Extension",
        "Extn" : "Extension",
        "street" : "Street",
        "Mg" : "Marg",
        "Pahargan" : "Pahar Ganj",
        "gali" : "Gali",
        "lothian" : "Lothian",
        "bangali" : "Bangali"
    }
    return mapping


def getPostCodeMapping():
    """ function to return the mapping list for postalcode, this is the list of corrections/changes which is frequently occuring in dataset"""
    postcode_mapping = {
        "110031v" : "110031", #removed the extra v in the end
        "2242" : "122001", # manually scanned the OSM file for pincode for same place
        "10089" : "110085", #checked manually on internet
        "1100002" : "110002",
        "1100049" : "110049",
        "2010" : "201010",
        "1100016" : "110016"
    }
    return postcode_mapping


def audit_street_type(street_types, street_name):
    """ checking whether streetname is present in expected list
    argument :
    street_types -- array to be filled if value not in expected array
    street_name -- street name 
    
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def audit_postcodes(postals, code, node_id):
    """ checking whether postcode is present in expected list

    argument :
    postals -- array to be filled if value not in expected array
    code -- postcode
    node_id -- id of node whose tag we are parsing
    """

    m = postals_re.search(code)
    if m:
        postal = m.group()
        if postal not in expected:
            postals[node_id].add(code)


def is_street_name(elem):
    """ checks for whether the tag currently checking while parsing is streetname tag
    argument : 
    elem -- tag to be parsed
    return : boolean value, if tag is streetname then returns true otherwise false
    """

    return (elem.attrib['k'] == "addr:street")

def is_postal(elem):
    """ checks for whether the tag currently checking while parsing is postalcode tag
    argument : 
    elem -- tag to be parsed
    return boolean value, if tag is postcode then returns true otherwise false
    """
    return (elem.attrib['k'] == "addr:postcode")

def audit(osmfile, postal = False):
    """ audit the OSM file by taking all the nodes and ways from the dataset
    and collecting all the unique values based on keys,
    like addr:street = "Rohini"
    here addr:street is the key and "Rohini" is the street value

    arguments:
    osmfile -- input osm file path which is to be parsed
    postal -- whether parse for streetname or postalcode, if yes parse for postal otherwise streetname,
        default streetname
    """
    osm_file = open(osmfile, "r")
    if postal is False:
        street_types = defaultdict(set)
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])
        return street_types                
    else:
        postals = defaultdict(set)
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_postal(tag):
                        # print "id : " , elem.attrib["id"]
                        node_id = elem.attrib["id"]
                        audit_postcodes(postals, tag.attrib['v'], node_id)
        # print postals                
        return postals                               
    osm_file.close()


def update_postcode(postcode, mapping):
    """ updates the postcodes of the streets and cities

    arguments:
    postcode -- postcode to be corrected
    mapping -- mapping array, contains very common corrections needed at many postcodes in dataset.

    """
    if postcode in mapping:
        postcode = mapping[postcode]

    postcode = re.sub(r'(\d+)\s+(?=\d)', r'\1', postcode)
    return postcode

def update_name(name, mapping):
    """updates the street name based on rules defined by me

    arguments : 
    name -- street_name
    mapping -- mapping array, some very common corrections needed at many streetnames in the dataset.

    return :
    it returns the updated street name

    """
    
    ## updating names based in mapping that we have created above
    split_name = name.split(" ")
    new_name = []
    for split in split_name:
        if split in mapping:
            new_name.append(mapping[split])
        else:
            new_name.append(split)
    name = " ".join(new_name)
    
    
    #updating names with pattern "No.<number>", wanted like this "No.<space><number>"
    if re.search(numberPattern, name):
        name = re.sub(r'No\.*\s*([0-9]{1,2})\s*$', r'No. \1', name, flags = re.I)
    
    
    #ASCII character problem Sector - 39
    name = re.sub(unichr(8211), "-", name)
    name = name.encode('ascii','ignore')
    
    #updating sector names, wanted results in the form "Sector<space><number>"
    if re.search(sectorpattern, name):
        name = name.lower().title()
        if "-" in name:
            name = re.sub('-',' ',name)
            name = re.sub(' +',' ',name)
        else:
            name = re.sub("Sector|sec", "Sector ", name, flags=re.I)
        
    matches = re.findall("Sector", name, re.DOTALL)
    if len(matches) == 3 and ("Sector 4 Noida" in name or "Sector 4, Noida," in name):
        name = "C - 99, Sector 4, Block C, Noida"
            
    return name
    
def main():
    """ main function calls other functions """

    print "printing street names : "
    st_types = audit(OSMFILE)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, getStreetMapping())
            print name, " => ", better_name

    print "postal code : "
    postals = audit(OSMFILE, postal = True)
    for postal, ways in postals.iteritems():
        for code in ways:
            if len(code) != 6:
                corrected_code = update_postcode(code, getPostCodeMapping())
                print code , " => " , corrected_code


if __name__ == "__main__":
    """ start of the script """
    main()