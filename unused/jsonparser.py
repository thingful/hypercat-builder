# -*- coding: utf-8 -*-
# for mor einfo about how to use python to parse json docs see https://docs.python.org/2/library/json.html
import hypercat_lib.hypercat_py.hypercat as hypercat
import json
import os
import errno

PROVIDER_NAME = "transportapi"

DBDUMP_PATH = 'data/db-dump.json'

def build_hcitem(jsonObj):
	# instantiate new item
	r = hypercat.Resource("DESCRIPTON GOES HERE",  "application/json")

	r.addItemMetadata("urn:X-hypercat:rels:isContentType", "applications/json")

	r.addItemMetadata("urn:X-{:s}:rels:hasId".format(PROVIDER_NAME), jsonObj['ID']) # get id

	r.addItemMetadata("urn:X-{:s}:rels:hasTitle".format(PROVIDER_NAME), jsonObj['post_title']) # get name

	r.addItemMetadata("urn:X-{:s}:rels:hasContent".format(PROVIDER_NAME), jsonObj['post_content']) # get content

	r.addItemMetadata("urn:X-{:s}:rels:createdAt".format(PROVIDER_NAME), jsonObj['post_date']) # get date

	if 'person' in jsonObj:
		if 'name' in jsonObj['person']:
			r.addItemMetadata("urn:X-{:s}:rels:name".format(PROVIDER_NAME), jsonObj['person']['name']) # get nested val

	return r

# load JSON file
def parse_json():
	"""loops trough the json document and returns a hypercat catalogue"""

	# create new hypercat catalogue
	h = hypercat.Hypercat("{:s} Catalogue".format(PROVIDER_NAME))

	# read JSON file
	with open(DBDUMP_PATH) as data:
		doc = json.load(data)

	# extract data from JSON file
	for i, obj in enumerate(doc):
		r = build_hcitem(obj)
		h.addItem(r,  'http://resource-{:d}'.format(i))

	return h # the actual JSON hypercat catalogue

# save output to file
def generate_hypercat_file():
	"""builds a hypercat catalogue a saves it to a file"""

	h = parse_json()

	output_content = h.prettyprint() 

	file_name = 'output/hypercat-lib2.json' # the file name

	if not os.path.exists(os.path.dirname(file_name)):
	    try:
	        os.makedirs(os.path.dirname(file_name))
	    except OSError as exc: # guard against race condition
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
