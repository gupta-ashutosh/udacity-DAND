#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

# OSM_PATH = "example.osm"
#OSM_PATH = "sample.osm"
OSM_PATH = "new-delhi_india.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
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

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
