from nose.tools import *
import csv
import os
import mock
import __builtin__
from hypercat import hypercat
from hypercat_builder.hypercat_builder import HypercatBuilder
from hypercat_builder.hypercat_builder import natural_sort

def test_get_catalogue_type():
  hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com', None)
  test_train = hc.get_catalogue_type('atcocodes_everything')
  test_bus = hc.get_catalogue_type('atcocodes-buses')
  test_ferry = hc.get_catalogue_type('atcocodes-all-ferries')
  test_tram = hc.get_catalogue_type('tram')
  test_err = hc.get_catalogue_type('wrong-file')
  test_err2 = hc.get_catalogue_type('atcocodes-ferr')

  assert_equal(test_train, 'train')
  assert_equal(test_bus, 'bus')
  assert_equal(test_ferry, 'ferry')
  assert_equal(test_tram, 'tram')
  assert_equal(test_err, False)

def test_build_hcitem_stops():
  hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com', None)

  with open('tests/data/test-ferry.csv') as data:
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

  assert_equal(r.__dict__, expected.__dict__)

def test_build_hcitem_station():
  hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com', None)

  with open('tests/data/test-station.csv') as data:
    reader = csv.reader(data, delimiter=';', quotechar='"')
    next(reader, None)

    for i, row in enumerate(reader):
      r = hc.build_hcitem_station(row, 'timetable')

      expected = hypercat.Resource('CROXLEY LT: Timetable Departures', 'application/json')
      expected.addRelation('urn:X-TransportAPI:rels:hasCRSCode', 'ZCO')
      expected.addRelation('urn:X-TransportAPI:rels:hasTiplocCode', 'CRXLEY')
      expected.addRelation("urn:X-TransportAPI:rels:isNodeType", "train_station")
      expected.addRelation("urn:X-TransportAPI:rels:hasDataCurrency", "timetable")

  assert_equal(r.__dict__, expected.__dict__)

def test_natural_sort():
  testcase = ['foo1', 'foo10', 'foo2']
  expected = ['foo1', 'foo2', 'foo10']

  assert_equal(natural_sort(testcase), expected)

def side_effect(arg):
  return iter(values[arg])

@mock.patch('hypercat_builder.hypercat_builder.os.path.exists')
def test_validate_input(mock_path):

  hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com', None)

  # set up mock 1
  mock_path.exists.return_value = False
  false_path = hc.validate_input_file_and_get_type('path/to/file')
  assert_false(false_path)

  # set up mock 2
  mock_path.exists.return_value = True
  valid = hc.validate_input_file_and_get_type('path/to/atcocodes_everything.csv')
  assert_equal(valid, 'train')

  wrong_filetype = hc.validate_input_file_and_get_type('path/to/atcocodes_everything')
  assert_false(wrong_filetype)

@mock.patch('os.listdir')
def test_index(mock_listdir):
  mock_listdir.side_effect = [['ferry', 'train'], ['live', 'timetable'], ['live', 'timetable']]

  hc = HypercatBuilder('input_dir', 'output_dir', 'http://transportapi.com', None)
  cat = hc.build_index('2016-01-01')

  expected = hypercat.Hypercat('TransportAPI Catalogue')
  expected.addRelation('urn:X-hypercat:rels:hasHomePage', 'http://www.transportapi.com/')
  expected.addRelation('urn:X-transportapi:rels:createdAt', '2016-01-01')
  r1_live = hypercat.Resource('TransportAPI - Ferry Live Catalogue', 'application/vnd.hypercat.catalogue+json')
  r1_timetable = hypercat.Resource('TransportAPI : Ferry Timetable Catalogue', 'application/vnd.hypercat.catalogue+json')
  r2_live = hypercat.Resource('TransportAPI - Train Live Catalogue', 'application/vnd.hypercat.catalogue+json')
  r2_timetable = hypercat.Resource('TransportAPI : Train Timetable Catalogue', 'application/vnd.hypercat.catalogue+json')
  expected.addItem(r1_live, 'http://transportapi.com/cat/ferry/live.json')
  expected.addItem(r1_timetable, 'http://transportapi.com/cat/ferry/timetable.json')
  expected.addItem(r2_live, 'http://transportapi.com/cat/train/live.json')
  expected.addItem(r2_timetable, 'http://transportapi.com/cat/train/timetable.json')

  assert_equal(expected.prettyprint(), cat)
