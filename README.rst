Hypercat Builder
================

hypercat_builder.py is a simple tool for building Hypercat 3 compatible
catalogues for the TransportAPI. It generates static Hypercat catalogues
generated from a CSV dump of bus/tram stop, train station, or ferry port data
pulled from the TransportAPI's database. These catalogues can then be hosted as
simple static files via the main TransportAPI's webserver.


Usage
-----

By default the script reads csv files located in the /data folder inside the
root folder (IE where the script is located) and saves hypercat catalogues in
the /output folder.

To use the script run:

``./hypercat_builder.py --input=<input folder>``

Input files within the input folder should be named as follows:
 - atcocodes-bus.csv
 - atcocodes-ferry.csv
 - atcocodes-tram.csv
 - crs_codes-everything.csv

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
a HyperCat catalogue containing references to individual sub-catalogues.

Run ``./hypercat_builder.py --help`` for more info about usage and available options.

Flags
-----

The script default behaviours can be modified using optional flags:

--input=<path_name>
Folder containing the input CSV files for processing. It can be a folder or an individual CSV file.
Defaults to ./data folder

--output=<directory_name>
Directory the output JSON should be written to.
Defaults to ./output folder

--fcc
Output API links to the Future Cities Catapult version of the TransportAPI.
If omitted catalogue links will point to the main TransportAPI website.

---legacy
use transportapi.com/v3/uk/bus/... url for ferry, trams and buses.
By default each type has its own base url (ie transportapi.com/v3/uk/tram/... for trams)


## Version
1.0


## Copyright
Thingful Ltd.
