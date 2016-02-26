# Hypercat Builder
hypercat_builder.py is a simple tool for building HyperCat 2 compatible
catalogues for the TransportAPI. It generates static HyperCat catalogues
generated from a CSV dump of either bus stop, train station, or ferry port data
pulled from the TransportAPI's database. These catalogues can then be hosted as
simple static files via the main TransportAPI's webserver.

## Usage
By deafult the script reads csv files located in the root folded (IE where the script is located) and saves hypercat catalogues in the /output folder.

To use the script run
```python hypercat_builder.py run```

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
a HyperCat catalogue containing references to the individual sub-catalogues.

## Flags
The script default behaviour can be modified using optionl flags:

```--input=<path_name>```
Folder containing the input CSV files for processing. It can be a folder or an individual CSV file.

```--output=<directory_name>```
Directory the output JSON should be written to

```--fcc```
Output API links to the Future Cities Catapult version of the TransportAPI.
Omitting


## Version
1.0

## Copyright
Thingful Ltd.
