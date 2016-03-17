# -*- coding: utf-8 -*-
# for mor einfo about how to use python to parse xml docs see https://docs.python.org/2/library/xml.etree.elementtree.html

import hypercat_lib.hypercat_py.hypercat as hypercat
import csv
import os
import errno

PROVIDER_NAME = "PROVIDER_NAME"

DBDUMP_PATH = 'data/db-dump.csv'

# generate rel val pairs 
# use string <node.tag> to access a node by name
# use dict <node.attrib[attribute-name]> to access a node by attribute
# use <node.text> to get the node value
def build_hcitem(csvRow):
	"""loops through a single xml node and generates a hypercat item"""

	# instantiate new item
	r = hypercat.Resource("DESCRIPTON GOES HERE",  "application/vnd.hypercat.catalogue+json")

	r.addItemMetadata("urn:X-{:s}:rels:hasId".format(PROVIDER_NAME), csvRow[0])

	return r

# parse xml and build hypercat catalogue
# use <iter('node_name')> to extract loop over top level nodes 
def parse_csv():
	"""loops trough the csv document and returns a hypercat catalogue"""

	# create new hypercat catalogue
	h = hypercat.Hypercat("{:s} Catalogue".format(PROVIDER_NAME))

	# load csv file
	with open(DBDUMP_PATH, 'rb') as csvfile:
		dbreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for i, row in enumerate(dbreader):
			r = build_hcitem(row)
			h.addItem(r, 'http://resource-{:d}'.format(i))

	return h # the actual XML hypercat catalogue

def generate_hypercat_file():
	"""builds a hypercat catalogue a saves it to a file"""

	h = parse_csv()

	output_content = h.prettyprint() 

	file_name = 'output/hypercat-lib3.json' # the file name
	
	# save output to file
	if not os.path.exists(os.path.dirname(file_name)):
	    try:
	        os.makedirs(os.path.dirname(file_name))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise

	with open(file_name, "w") as f:
	    f.write(output_content)

	# print message if file was saved
	if os.path.isfile(file_name):
		print 'File successfully saved.'
	else:
		print 'File not saved.'

if __name__ == '__main__':
	generate_hypercat_file()