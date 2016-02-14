import unittest
import json
import hypercat_lib.hypercat_py.hypercat as hypercat
from jsonparser import build_hcitem

class buildHCItemTest(unittest.TestCase):
	def test_build_hcitem(self):
		with open('test/json-data.json') as data:
			doc = json.load(data)

		r = build_hcitem(doc[0])

		expected = hypercat.Resource("DESCRIPTON GOES HERE",  "application/json")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:hasId", 1)
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:hasTitle", "The Pilot")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:hasContent", "Hello World")
		expected.addItemMetadata("urn:X-PROVIDER_NAME:rels:createdAt", "2013-12-28 12:32:17")

		self.assertTrue(r.__dict__ == expected.__dict__)

if __name__ == '__main__':
	unittest.main()
