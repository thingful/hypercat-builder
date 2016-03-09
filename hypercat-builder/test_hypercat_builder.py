import unittest
import mock # not included in with python < 3.3
import csv, os
from hypercat import hypercat
from hypercat_builder import HypercatBuilder
import __builtin__
import json
import datetime

class catalogueTypeTest(unittest.TestCase):

	def test_get_catalogue_type(self):
		hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com')
		test_train = hc.get_catalogue_type('atcocodes_everything')
		test_bus = hc.get_catalogue_type('atcocodes-buses')
		test_ferry = hc.get_catalogue_type('atcocodes-all-ferries')
		test_tram = hc.get_catalogue_type('tram')
		test_err = hc.get_catalogue_type('wrong-file')
		test_err2 = hc.get_catalogue_type('atcocodes-ferr')

		self.assertTrue(test_train == 'train')
		self.assertTrue(test_bus == 'bus')
		self.assertTrue(test_ferry == 'ferry')
		self.assertTrue(test_tram == 'tram')
		self.assertIs(test_err, False)

class buildHypercatItemTest(unittest.TestCase):

	def test_build_hcitem_stops(self):
		hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com')

		with open('test/test-ferry.csv') as data:
			reader = csv.reader(data, delimiter=';', quotechar='"')
			next(reader, None) 

			for i, row in enumerate(reader):
				r = hc.build_hcitem_stops(row, 'ferry', 'live')

				expected = hypercat.Resource('Ardleish Pier: Live Departures', 'application/json')
				expected.addRelation('urn:X-TransportAPI:rels:hasATCOCode', '9300ADL')
				expected.addRelation('http://www.w3.org/2003/01/geo/wgs84_pos#lat', '56.29944')
				expected.addRelation('http://www.w3.org/2003/01/geo/wgs84_pos#long', '-4.70125')
				expected.addRelation("urn:X-TransportAPI:rels:isNodeType", "ferry_stop")
				expected.addRelation("urn:X-TransportAPI:rels:hasDataCurrency", "live")

		self.assertTrue(r.__dict__ == expected.__dict__)

	def test_build_hcitem_station(self):
		hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com')

		with open('test/test-station.csv') as data:
			reader = csv.reader(data, delimiter=';', quotechar='"')
			next(reader, None) 

			for i, row in enumerate(reader):
				r = hc.build_hcitem_station(row, 'timetable')

				expected = hypercat.Resource('CROXLEY LT: Timetable Departures', 'application/json')
				expected.addRelation('urn:X-TransportAPI:rels:hasCRSCode', 'ZCO')
				expected.addRelation('urn:X-TransportAPI:rels:hasTiplocCode', 'CRXLEY')
				expected.addRelation("urn:X-TransportAPI:rels:isNodeType", "train_station")
				expected.addRelation("urn:X-TransportAPI:rels:hasDataCurrency", "timetable")

		self.assertTrue(r.__dict__ == expected.__dict__)


class buildIndexTest(unittest.TestCase):

	def side_effect(arg):
		return iter(values[arg])

	@mock.patch('hypercat_builder.os.path')
	def test_validate_input(self, mock_path):

		hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com')

		# set up mock 1
		mock_path.exists.return_value = False
		false_path = hc.validate_input_file_and_get_type('path/to/file')
		self.assertIs(false_path, False)

		# set up mock 2
		mock_path.exists.return_value = True
		valid = hc.validate_input_file_and_get_type('path/to/atcocodes_everything.csv')
		self.assertIs(valid, 'train')

		wrong_filetype = hc.validate_input_file_and_get_type('path/to/atcocodes_everything')
		self.assertIs(wrong_filetype, False)

	@mock.patch('os.listdir')
	def test_index(self, mock_listdir):
		mock_listdir.side_effect = [['ferry', 'train'], ['live', 'timetable'], ['live', 'timetable']]

		hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com')

		cat = hc.build_index('2016-01-01')

		expected = hypercat.Hypercat('TransportAPI Catalogue')
		expected.addRelation('urn:X-hypercat:rels:hasHomePage', 'http://www.transportapi.com/')
		expected.addRelation('urn:X-transportapi:rels:createdAt', '2016-01-01')
		r1_live = hypercat.Resource('Ferry: Departures Catalogue - Live', 'application/vnd.hypercat.catalogue+json')
		r1_timetable = hypercat.Resource('Ferry: Departures Catalogue - Timetable', 'application/vnd.hypercat.catalogue+json')
		r2_live = hypercat.Resource('Train: Departures Catalogue - Live', 'application/vnd.hypercat.catalogue+json')
		r2_timetable = hypercat.Resource('Train: Departures Catalogue - Timetable', 'application/vnd.hypercat.catalogue+json')
		expected.addItem(r1_live, 'http://transportapi.com/cat/ferry/live')
		expected.addItem(r1_timetable, 'http://transportapi.com/cat/ferry/timetable')
		expected.addItem(r2_live, 'http://transportapi.com/cat/train/live')
		expected.addItem(r2_timetable, 'http://transportapi.com/cat/train/timetable')

		self.assertEqual(expected.prettyprint(), cat)


if __name__ == '__main__':
	unittest.main(buffer=True)
