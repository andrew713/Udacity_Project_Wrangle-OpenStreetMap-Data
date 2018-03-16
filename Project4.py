
# coding: utf-8

# In[1]:


import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict


# In[2]:


inputname = ("Houston.osm")
output_filename =("Output.osm")


# In[3]:


lower = re.compile(r'([a-z]|_)*$')                            #lowercase letters
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')          # colon in their name
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.  \t\r\n]') # problem characters


# In[ ]:





# ### Iterative Parsing

# ### In the code below it goes through osm file and find all the tags type  and place them into a dictionary and if it seen again it increase and finaly give a return of how many of each tags is in the dictionary.

# In[4]:



def count_tags(filename):
    tags ={}
    for _,elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag]+=1
        else:
            tags[elem.tag]=1
    

    return tags



# In[5]:


count_tags(inputname)


# 

# ### Tag Type

# ### In the code below it search through all the tags and see if the key have any problem like lowercase, special character, and colon or other. Then it return how many problem it found.

# In[6]:


def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys["lower"]+=1
        elif lower_colon.search(element.attrib['k']):
            keys["lower_colon"]+=1
        elif problemchars.search(element.attrib['k']):
            keys["problemchars"]+=1
        else:
            keys["other"]+=1
    return keys


# In[7]:


def process_map(filename):
    keys = {"lower":0, "lower_colon":0 , "problemchars":0 , "other":0}
    for _,element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


# In[8]:


process_map(inputname)


# ### Exploring File

# ### In the code below we search through all of the file find the uid and returing the uid 

# In[9]:


def proc_(filename):
    user = set()
    for _,element in ET.iterparse(filename):
        if "uid" in element.attrib:
            user.add(element.attrib["uid"])
    
    return user


# In[10]:


proc_(inputname)


# ### Street Type 

# ### In the code below it goes throught the file and look at addr:street  and value and print the type of road that in the file

# In[11]:




osm_file = open("Houston.osm",'r',encoding="utf-8")


street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()

        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print ("%s: %d" % (k, v)) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)    

if __name__ == '__main__':
    audit()
  



# In[ ]:





# ### Improving Street Name

# ### In the code Below it goes into the osm file are replace the street abbreviation with the full street name 

# In[12]:



OSMFILE = "Houston.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Way","West","South","Plaza","Freeway","East"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "Ave.":"Avenue",
            "Ave": "Avenue",
            "Blvd":"Boulevard",
            "Blvd.":"Boulevard",
            "E":"East",
            "Fwy":"Freeway",
            "Dr":"Drive",
            "Rd":"Road",
            "S":"South"
            
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
    osm_file = open(osmfile, "r",encoding = "utf-8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
  #print("name:{}".format(name))
  m = street_type_re.search(name)
  #print("m:{}".format(m))
  if m:
      street_type = m.group()
      print('Street Type : {}'.format(street_type))
      
  better_type =street_type
  
  for k,v in mapping.items():
      if street_type == k:
          better_type = v
  
  better_name = name.replace(street_type, better_type)
  #print("better_name:{}".format(better_name))
  
  
  return better_name


   
    
   


st_types = audit(OSMFILE)
#pprint.pprint(dict(st_types))

for st_type, ways in st_types.items():
    for name in ways:
        better_name = update_name(name, mapping)
        print (name, "=>", better_name)




# In[ ]:





# #### Improving

# #### In the cell below find key highway and fix the value with a uppercase value 

# In[13]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "Houston.osm"



# UPDATE THIS VARIABLE
mapping = {
           "residential":"Residential",
           "service":"Service",
           "motorway_link":"Motorway_Link",
           "secondary":"Secondary",
           "primary_link":"Primary_Link",
           "trunk_link":"Trunk_Link",
           "tertiary_link":"Tertiary_Link",
           "track":"Track",
           "tertiary":"Tertiary",
           "footway":"Footway",
           "unclassified":"Unclassified",
           "secondary":"Secondary",
           "chain_link":"Chain_Link"
            }



v_attrib = {}


def audit2(osmfile):
    att={}
    osm_file = open(osmfile, "r",encoding ="utf-8")
   
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k']== 'highway':
                   # print ("name",tag.attrib['v']) 
                    v_attrib[elem] = tag.attrib['v']
                    if v_attrib[elem] in mapping: 
                            #print(mapping[v_attrib[elem]])
                            #print(v_attrib[elem])
                            att[v_attrib[elem]]=mapping[v_attrib[elem]]
                        

    return att
                           
                        
    osm_file.close()
    #return att
#rint(att)



st_types2 = audit2("Houston.osm")
#print(st_types2)

for k,v in st_types2.items():
    print('{} -->  {}'.format(k,v))
   
        


        



# In[ ]:





# ### Database 

# ### In the cell below create the Database and place the infromation into NODES_PATH, NODES_TAGS_PATH, WAYS_NODES_PATH, WAYS_PATH, and WAY_TAGS_PATH

# In[14]:


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "Houston.osm"

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


def load_new_tag(element, secondary, default_tag_type):
    """
    Load a new tag dict to go into the list of dicts for way_tags, node_tags
    """
    new = {}
    new['id'] = element.attrib['id']
    if ":" not in secondary.attrib['k']:
        new['key'] = secondary.attrib['k']
        new['type'] = default_tag_type
    else:
        post_colon = secondary.attrib['k'].index(":") + 1
        new['key'] = secondary.attrib['k'][post_colon:]
        new['type'] = secondary.attrib['k'][:post_colon - 1]
    new['value'] = secondary.attrib['v']
    
    return new


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    if element.tag == 'node':
        for attrib, value in element.attrib.items():
            if attrib in node_attr_fields:
                node_attribs[attrib] = value
        

        for secondary in element.iter():
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    continue
                else:
                    new = load_new_tag(element, secondary, default_tag_type)
                    tags.append(new)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for attrib, value in element.attrib.items():
            if attrib in way_attr_fields:
                way_attribs[attrib] = value
                
        counter = 0
        for secondary in element.iter():
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is  None:
                    
                
                    new = load_new_tag(element, secondary, default_tag_type)
                    tags.append(new)
            if secondary.tag == 'nd':
                newnd = {}
                newnd['id'] = element.attrib['id']
                newnd['node_id'] = secondary.attrib['ref']
                newnd['position'] = counter
                counter += 1
                way_nodes.append(newnd)
        
       
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
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



# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', encoding="utf-8") as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w', encoding="utf-8") as nodes_tags_file,          codecs.open(WAYS_PATH, 'w',encoding="utf-8") as ways_file,          codecs.open(WAY_NODES_PATH, 'w',encoding="utf-8") as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w', encoding="utf-8") as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    
    process_map(OSM_PATH, validate=True)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




