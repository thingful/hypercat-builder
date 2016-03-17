import unittest
from xmlparser import build_hcitem
import xml.etree.ElementTree as ET
import hypercat_lib.hypercat_py.hypercat as hypercat

class buildHCItemTest(unittest.TestCase):
	def test_build_hcitem(self):

		doc = ET.parse('test/xml-data.xml')

		# get xml root
		root = doc.getroot()

		r = build_hcitem(root)

		expected = hypercat.Resource("DESCRIPTON GOES HERE",  "application/json")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:hasId", "1")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:createdAt", "2013-12-28 12:32:17")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:hasContent", "Lorem Ipsum dolor sit amet")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:hasTitle", "The Pilot")

		self.assertTrue(r.__dict__ == expected.__dict__)

if __name__ == '__main__':
	unittest.main()
