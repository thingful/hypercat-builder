# -*- coding: utf-8 -*-
# for mor einfo about how to use python to parse xml docs see https://docs.python.org/2/library/xml.etree.elementtree.html

import hypercat_lib.hypercat_py.hypercat as hypercat
import csv
import os
import errno

PROVIDER_NAME = "transportapi"

DBDUMP_PATH = 'data/crs_codes-everything.csv'

# generate rel val pairs 
# use string <node.tag> to access a node by name
# use dict <node.attrib[attribute-name]> to access a node by attribute
# use <node.text> to get the node value
def build_hcitem(csvRow):
	"""loops through a single xml node and generates a hypercat item"""

	# instantiate new item
	r = hypercat.Resource("{:s} station: live data".format(csvRow[3]),  "application/json")

	# lat
	r.addItemMetadata("http://www.w3.org/2003/01/geo/wgs84_pos#lat", csvRow[7])

	# lon
	r.addItemMetadata("http://www.w3.org/2003/01/geo/wgs84_pos#long", csvRow[8])

	# CRS
	r.addItemMetadata("urn:X-{:s}:rels:hasCRSCode".format(PROVIDER_NAME), csvRow[5])

	# tiploc
	r.addItemMetadata("urn:X-{:s}:rels:hasTiplocCode".format(PROVIDER_NAME), csvRow[1])

	# name
	r.addItemMetadata("urn:X-{:s}:rels:hasName".format(PROVIDER_NAME), csvRow[3])

	# created at
	r.addItemMetadata("urn:X-{:s}:rels:hasCreatedAt".format(PROVIDER_NAME), csvRow[14])

	# type
	r.addItemMetadata("urn:X-{:s}:rels:isNodeType".format(PROVIDER_NAME), "train_station")

	# currency
	r.addItemMetadata("urn:X-{:s}:rels:hasDataCurrency".format(PROVIDER_NAME), "live")

	return r

# parse xml and build hypercat catalogue
# use <iter('node_name')> to extract loop over top level nodes 
def parse_csv():
	"""loops trough the xml document and returns a hypercat catalogue"""

	# create new hypercat catalogue
	h = hypercat.Hypercat("{:s} stations catalogue".format(PROVIDER_NAME))

	# load csv file
	with open(DBDUMP_PATH, 'rb') as csvfile:
		dbreader = csv.reader(csvfile, delimiter=';', quotechar='"')
		for i, row in enumerate(dbreader):
			if i == 0 :
				continue

			r = build_hcitem(row)
			h.addItem(r, 'http://fcc.transportapi.com/v3/uk/train/station/{:s}/live.json'.format(row[5]))

	return h # the actual XML hypercat catalogue

def generate_hypercat_file():
	"""builds a hypercat catalogue a saves it to a file"""

	h = parse_csv()

	output_content = h.prettyprint() 

	file_name = 'output/stations-live.json' # the file name
	
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