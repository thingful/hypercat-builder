import unittest
import json
import lib.hypercat_lib.hypercat_py.hypercat as hypercat
from hypercat_builder import HypercatBuilder
import sys, os

class buildHCItemTest(unittest.TestCase):

	def test_get_catalogue_type(self):
		hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com')
		test_train = hc.get_catalogue_type('atcocodes_everything')
		test_bus = hc.get_catalogue_type('atcocodes-buses')
		test_ferry = hc.get_catalogue_type('atcocodes-ferries')
		test_tram = hc.get_catalogue_type('atcocodes-tram')
		test_err = hc.get_catalogue_type('wrong-file')

		self.assertTrue(test_train == 'train')
		self.assertTrue(test_bus == 'bus')
		self.assertTrue(test_ferry == 'ferry')
		self.assertTrue(test_tram == 'tram')
		self.assertTrue(test_err == False)

if __name__ == '__main__':
	unittest.main(buffer=True)