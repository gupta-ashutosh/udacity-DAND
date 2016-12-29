import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

# OSMFILE = 'sample.osm'
OSMFILE = 'new-delhi_india.osm'

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", 
            "Lane", "Road", "Trail", "Parkway", "Commons", "College", "School", 
            "University","Delhi", "Enclave", "footpath","Marg", "nagar", "Chowk", "Bagh",
            "Complex", "Estate", "Expressway", "Flyover", "Ghaziabad", "road", "Vihar",
            "gurgaon", "hotel", "garden","colony", "Nagar", "Lok", "Market", "Sector"]

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


sectorpattern = re.compile(r'\s*(Sector)\s*(-)\s*', re.IGNORECASE)
sectorsubpattern1 = re.compile(r'(Sector-)\w*', re.IGNORECASE)
sectorsubpattern2 = re.compile(r'(Sector)\s(-)\w*', re.IGNORECASE)
sectorsubpattern3 = re.compile(r'(Sector)\s(-)\s\w*', re.IGNORECASE)
sectorsubpattern4 = re.compile(r'(Sector-)\s\w*', re.IGNORECASE)
sectorsubpattern5 = re.compile(r'(Sector)\s(-)\w*$', re.IGNORECASE)


mapping = {
    "Rd" : "Road",
    "delhi":"Delhi",
    "Delhi.":"Delhi",
    "delhi": "Delhi",
    "11'" : "11",
    "sec" : "Sector",
    "Sec" : "Sector",
    "extn" : "Extension",
    "sector":"Sector",
    "UP)" : "UP",
    "Rohini,Delhi" : "Rohini",
    "Pritampura" : "Pitampura",
    "noida":"Noida",
    "Noida," : "Noida",
    "NOIDA" : "Noida",
    "NAGAR" : "Nagar",
    "nagar" : "Nagar",
    "Bazar" : "Bazaar",
    "no" : "No",
    "south" : "South",
    "city" : "City",
}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
    
def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        if re.search(lower,element.attrib["k"]):
            keys["lower"] += 1
        elif re.search(lower_colon,element.attrib["k"]):
            keys["lower_colon"] += 1
        elif re.search(problemchars,element.attrib["k"]):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
        
    return keys 
    
def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    pprint.pprint(keys)
    
    
def update_name(name, mapping):
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
            
    split_name = name.split(" ")
    new_name = []
    for split in split_name:
        if split in mapping:
            new_name.append(mapping[split])
        else:
            new_name.append(split)
            
    name = " ".join(new_name)
    
    return name
    
def main():
    # print "printing "
    # process_map(OSMFILE)
    
    print "printing street names : "
    st_types = audit(OSMFILE)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, " => ", better_name
    
if __name__ == "__main__":
    main()