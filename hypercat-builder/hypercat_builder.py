#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hypercat Builder
----------------------------------------------------------------
hypercat_builder.py is a simple tool for building HyperCat 2 compatible
catalogues for the TransportAPI. It generates static HyperCat catalogues
generated from a CSV dump of either bus stop, train station, or ferry port data
pulled from the TransportAPI's database. These catalogues can then be hosted as
simple static files via the main TransportAPI's webserver.
----------------------------------------------------------------
Input files within that folder should be named as follows:
  atcocodes-bus.csv
  atcocodes-ferry.csv
  atcocodes-tram.csv
  crs_codes-everything.csv

The script will then output the following JSON catalogues to the output folder:
  cat.json
  bus/live.json
  bus/timetabled.json
  tram/live.json
  tram/timetabled.json
  ferry/live.json
  ferry/timetabled.json
  train/live.json
  train/timetabled.json

The top level cat.json contains the entry point to the catalogue, which must be
a HyperCat catalogue containing references to the individual sub-catalogues.

The script also has an additional flag called --fcc which causes it to output
API links to the Future Cities Catapult version of the TransportAPI. Omitting
this flag generates links to the main TransportAPI website.
----------------------------------------------------------------

Usage:
  hypercat_builder.py [--input=<path>] [--output=<directory>] [--fcc] [--legacy]
  hypercat_builder.py -h | --help
  hypercat_builder.py --version

Options:
  -h, --help                Show this screen.
  --version                 Show version.
  --input=<path>            Folder containing the input CSV files for processing.
                            It can be a folder or an individual file [default: ./data].
  --output=<directory>      Directory the output JSON should be written to
                            [default: ./output].
  --fcc                     Future City Catapult flag.
  --legacy                  use transportapi.com/v3/uk/bus/... url for ferry, trams and
                            buses. By default each type has its own base url 
                            (ie transportapi.com/v3/uk/tram/... for trams)

"""

from docopt import docopt
from hypercat import hypercat
import csv
import os
import sys
import errno
import ntpath
import datetime
import re
from glob import glob

PROVIDER_NAME = "TransportAPI"

PROVIDER_WEBSITE = "http://www.transportapi.com/"

MAX_CATALOGUE_LENGTH = 10000

class HypercatBuilder():
	
	def __init__(self, input_file, output_dir, base_url):
		self.input_path = input_file
		self.output_dir = output_dir
		self.base_url = base_url
		self.file_name = '' # the name of the file currently being processed
		self.current_dataset = ''
		self.current_datatype = ''
		
	def build_hcitem_stops(self, csvRow, data_type, data_currency):
		"""Extracts data from a single csv row and generates rel val 
		pairs for bus stops, and ferries"""

		node_type = '{:s}_stop'.format(data_type)

		try :
			lat = (float)(csvRow[8])/100000.0
		except:
			lat = csvRow[8]

		try:
			lon = (float)(csvRow[9])/100000.0
		except:
			lon = csvRow[9]

		# instantiate new item
		r = hypercat.Resource('{:s}: {:s} Departures'.format(csvRow[7], data_currency.title()), 'application/json')

		# ATCO
		r.addRelation('urn:X-{:s}:rels:hasATCOCode'.format(PROVIDER_NAME), csvRow[1])

		# lat
		if lat != '':
			r.addRelation('http://www.w3.org/2003/01/geo/wgs84_pos#lat', str(lat) )

		# lon
		if lon != '':
			r.addRelation('http://www.w3.org/2003/01/geo/wgs84_pos#long', str(lon))

		# type
		r.addRelation('urn:X-{:s}:rels:isNodeType'.format(PROVIDER_NAME), node_type)

		# currency
		r.addRelation('urn:X-{:s}:rels:hasDataCurrency'.format(PROVIDER_NAME), data_currency)

		return r

	def build_hcitem_station(self, csvRow, data_currency):
		"""Extracts data from a single csv row generate rel val 
		pairs for train stations"""

		# instantiate new item
		r = hypercat.Resource('{:s}: {:s} Departures'.format(csvRow[3], data_currency.title()),  'application/json')

		# lat
		if csvRow[7] != '':
			r.addRelation('http://www.w3.org/2003/01/geo/wgs84_pos#lat', csvRow[7])

		# lon
		if csvRow[8] != '':
			r.addRelation('http://www.w3.org/2003/01/geo/wgs84_pos#long', csvRow[8])

		# CRS
		r.addRelation('urn:X-{:s}:rels:hasCRSCode'.format(PROVIDER_NAME), csvRow[5])

		# tiploc
		r.addRelation('urn:X-{:s}:rels:hasTiplocCode'.format(PROVIDER_NAME), csvRow[1])

		# type
		r.addRelation('urn:X-{:s}:rels:isNodeType'.format(PROVIDER_NAME), 'train_station')

		# currency
		r.addRelation('urn:X-{:s}:rels:hasDataCurrency'.format(PROVIDER_NAME), data_currency)

		return r

	def parse_csv(self, file_to_parse, catalogue_type, index):
		"""loops trough the CSV input file and returns a hypercat catalogue.
		If the number of rows exceed the MAX_CATALOGUE_LENGTH multiple files
		will be generated until the end of the file is reached"""

		# create new hypercat catalogue for live items
		live_h = hypercat.Hypercat('{:s} - {:s} Live Catalogue'.format(PROVIDER_NAME, catalogue_type.title()))
		live_h.addRelation('urn:X-hypercat:rels:hasHomePage', PROVIDER_WEBSITE)
		live_h.addRelation('urn:X-transportapi:rels:createdAt', datetime.datetime.utcnow().isoformat())

		# create new hypercat catalogue for timetable items
		timetable_h = hypercat.Hypercat('{:s} - {:s} Timetable Catalogue'.format(PROVIDER_NAME, catalogue_type.title()))
		timetable_h.addRelation('urn:X-hypercat:rels:hasHomePage', PROVIDER_WEBSITE)
		timetable_h.addRelation('urn:X-transportapi:rels:createdAt', datetime.datetime.utcnow().isoformat())

		# loop flag
		loop_again = False

		# load csv file
		try:
			with open(file_to_parse, 'rb') as csvfile:
				reader = csv.reader(csvfile, delimiter=';', quotechar='"')
				next(reader, None) 
				for i, row in enumerate(reader):

					# continue to nth line if iterating
					if i <= MAX_CATALOGUE_LENGTH * (index-1):
						continue

					# break if catalogue limit has been reached
					if i > MAX_CATALOGUE_LENGTH * index:
						loop_again = True
						break

					if catalogue_type == 'train':
						
						live_r = self.build_hcitem_station(row, 'live')
						live_h.addItem(live_r, '{:s}v3/uk/train/station/{:s}/live.json'.format(self.base_url, row[5]))

						timetable_r = self.build_hcitem_station(row, 'timetable')
						timetable_h.addItem(timetable_r, '{:s}/v3/uk/train/station/{:s}/timetable.json'.format(self.base_url, row[5]))

					else:
						# check for legacy flag
						if arguments['--legacy']:
							c_type = 'bus'
						else :
							c_type = catalogue_type

						live_r = self.build_hcitem_stops(row, catalogue_type, 'live')
						live_h.addItem(live_r, '{:s}/v3/uk/{:s}/stop/{:s}/live.json'.format(self.base_url, c_type, row[1]))

						timetable_r = self.build_hcitem_stops(row, catalogue_type, 'timetable')
						timetable_h.addItem(timetable_r, '{:s}/v3/uk/{:s}/stop/{:s}/timetable.json'.format(self.base_url, c_type, row[1]))
		except:
			print("ERROR: something went wrong when opening a file.")
			return

		self.build_live_catalogue(live_h, catalogue_type, index, loop_again)
		self.build_timetable_catalogue(timetable_h, catalogue_type, index, loop_again)

		# need to loop again?
		if loop_again:
			self.parse_csv(file_to_parse, catalogue_type, index+1)

	def build_live_catalogue(self, json_data, cat_type, index, add_file_count) :
		output_content = json_data.prettyprint()
		output_base_dir= self.sanitize_output(self.output_dir)

		if index > 1 or add_file_count == True :
			file_name = '{:s}/cat/{:s}/live-{:d}.json'.format(output_base_dir, cat_type, index)
		else :
			file_name = '{:s}/cat/{:s}/live.json'.format(output_base_dir, cat_type)
		
		if not os.path.exists(os.path.dirname(file_name)):
			try:
				os.makedirs(os.path.dirname(file_name))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise

		with open(file_name, "w") as f:
			f.write(output_content)

		if os.path.isfile(file_name):
			print '{:s} ===> {:s}'.format(file_name, 'successfully saved')
		else:
			print '{:s} ===> error! File not saved'.format(file_name)

	def build_timetable_catalogue(self, json_data, cat_type, index, add_file_count) :
		output_content = json_data.prettyprint()
		output_base_dir= self.sanitize_output(self.output_dir)

		if index > 1 or add_file_count == True:
			file_name = '{:s}/cat/{:s}/timetable-{}.json'.format(output_base_dir, cat_type, index)
		else :
			file_name = '{:s}/cat/{:s}/timetable.json'.format(output_base_dir, cat_type)
		
		if not os.path.exists(os.path.dirname(file_name)):
			try:
				os.makedirs(os.path.dirname(file_name))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise

		with open(file_name, "w") as f:
			f.write(output_content)

		if os.path.isfile(file_name):
			print '{:s} ===> {:s}'.format(file_name, 'successfully saved')
		else:
			print '{:s} ===> error! File not saved'.format(file_name)

	def validate_input_folder(self):
		if len(os.listdir(self.input_path)) == 0:
			print '\nWARNING: input folder {:s} is empty.'.format(self.input_path)
			return False

		return True

	def validate_input_file_and_get_type(self, input_file):
		"""validates input files and returns the catalogue type"""

		# this will ensure that if a path was used as input
		# we validate against the file name only
		self.file_name = ntpath.basename(input_file)

		#print os.path.normpath(os.path.join(os.path.dirname(__file__), input_file))
		path = os.path.abspath(os.path.join(os.path.dirname(__file__), input_file))

		if os.path.exists(path) == False: # the input path does not exist
			print('\nWARNING: please ensure the input path is correct.\nUse <hypercat_builder.py --help> for help.\n')
			return False

		elif not input_file.endswith('.csv'): # file is not of csv type
			print('\nPlease choose a valid input file. Use <hypercat_builder.py --help> for help. \n')
			return False

		file_type = self.get_catalogue_type(self.file_name)
		return file_type

	def get_catalogue_type(self, input_file):
		if re.search(r'bus', input_file):
			return 'bus'
		elif re.search(r'tram', input_file):
			return 'tram'
		elif re.search(r'ferr', input_file):
			return 'ferry'
		elif re.search(r'everything', input_file) or re.search(r'train', input_file):
			return 'train'
		else:
			print('\nWARNING: {:s} was not recognized'.format(input_file))	
			print('\nPlease ensure your input file is labelled correctly.\nUse <hypercat_builder.py --help> for a list of valid file names.\n') 
			return False

	def sanitize_output(self, output_path):
		"""removes forward slashes from the beginning and the end of the output path"""
		otp_path = output_path.strip('/')

		return otp_path 

	def build_index(self, timestamp):
		# create a new hypercat catalogue
		index = hypercat.Hypercat('{:s} Catalogue'.format(PROVIDER_NAME))
		index.addRelation('urn:X-hypercat:rels:hasHomePage', PROVIDER_WEBSITE)
		index.addRelation('urn:X-transportapi:rels:createdAt', timestamp)

		cat_dir = os.path.join(self.output_dir, 'cat/')

		for current_folder in os.listdir(cat_dir):
			try:
				available_files = os.listdir(os.path.join(cat_dir, current_folder))
			except OSError:
				continue

			for current_file in natural_sort(available_files):
				# remove extension from file name 
				f = os.path.splitext(current_file)[0]

				subcat = hypercat.Resource('{:s}: Departures Catalogue - {:s}'.format(current_folder.title(), f.title()), 'application/vnd.hypercat.catalogue+json')
				index.addItem(subcat, '{:s}/cat/{:s}/{:s}.json'.format(self.base_url, current_folder, f))

		return index.prettyprint()

	def save_index(self, catalogue):
		with open('{:s}/cat.json'.format(self.output_dir), "w") as f:
			f.write(catalogue)

	def generate_hypercat_file(self): 
		"""loops thorugh the available input files
		and starts the catalogue generation process"""

		# parse input
		if os.path.isdir(self.input_path) and self.validate_input_folder(): # input is a directory
			for current_file in os.listdir(self.input_path):

				path_to_file = os.path.join(self.input_path, current_file)

				if not current_file.startswith('.') and os.path.isfile(path_to_file) and self.validate_input_file_and_get_type(path_to_file): # file is valid
					self.current_dataset = current_file
					self.current_datatype = self.validate_input_file_and_get_type(path_to_file)
					h = self.parse_csv(os.path.join(self.input_path, current_file), self.current_datatype, 1)
				else:
					continue

		else: # input is a file
			if self.validate_input_file_and_get_type(self.input_path):
				self.current_dataset = self.input_path
				self.current_datatype = self.validate_input_file_and_get_type(self.input_path)
				h = self.parse_csv(self.input_path, self.current_datatype, 1)
			else:
				return

		cat = self.build_index(datetime.datetime.utcnow().isoformat())
		self.save_index(cat)

# natural_sort function below taken from
# http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
def natural_sort(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)
    	
def main(arguments):
	"""checks if any of the default arguments have been over-written
	   and starts the catalogue(s) building process"""

	if arguments['--fcc']:
		base_url = 'http://fcc.transportapi.com'
	else:
		base_url = 'http://transportapi.com'

	hypercat = HypercatBuilder(arguments['--input'], arguments['--output'], base_url)
	hypercat.generate_hypercat_file()


if __name__ == '__main__':
	arguments = docopt(__doc__, version='Hypercat Builder 1.0')

	# we will never call this unless arguments parse successfully
	main(arguments)
