'''
Copyright (C) 2019 Aman Agarwal

This file is used for downloading the planet image tiles.

Arguments
-k: api key for Planet Labs.
-g: path to the geojson file containing a single geometry.
-cc: maximum cloud cover in the image.
-d: directory to save images in.
-n: maximum number of images to download.

Ex: python download_planet_image.py -k api-key -g map.geojson
''' 

import os
import json
import argparse
from planet import api

def download_image():

  client = api.ClientV1(api_key=API_KEY)

  # defining the Area of Interest
  aoi = {
    "type": "Polygon",
    "coordinates": GEOMETRY,
  }

  # build a filter for the AOI
  query = api.filters.and_filter(
    api.filters.geom_filter(aoi),
    api.filters.range_filter('cloud_cover', gt=0),
    api.filters.range_filter('cloud_cover', lt=CLOUD_COVER)
  )
    
  # we are requesting PlanetScope 3 Band imagery
  item_types = ['PSScene3Band']
  request = api.filters.build_search_request(query, item_types)

  # this will cause an exception if there are any API related errors
  results = client.quick_search(request)

  # creates the output directory if not already exists
  if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

  # items_iter returns an iterator over API response pages
  for item in results.items_iter(NUM_IMG):
      # each item is a GeoJSON feature
      print('downloading tile {}'.format(item['id']))
      assets = client.get_assets(item).get()
      activation = client.activate(assets['visual'])

      callback = api.write_to_file(directory=SAVE_DIR)
      body = client.download(assets['visual'], callback=callback)
      body.await()

if __name__ == '__main__':
  # construct the argument parse and parse the arguments
  ap = argparse.ArgumentParser()
  ap.add_argument("-k", "--api_key", required=True, \
                help="api key for Planet Labs")
  ap.add_argument("-g", "--geometry", required=False, default=None, \
                help="path to the geojson file containing a single geometry")
  ap.add_argument("-cc", "--cloud_cover", required=False, default=0.1, \
                type=float, help="maximum cloud cover in the image")
  ap.add_argument("-d", "--save_dir", required=False, default='planet_image',\
                help="directory to save images in")
  ap.add_argument("-n", "--num_images", required=False, default=5, type=int, \
                help="maximum number of images to download")
  args = vars(ap.parse_args())

  API_KEY = args['api_key']
  CLOUD_COVER = args['cloud_cover']
  SAVE_DIR = args['save_dir']
  NUM_IMG = args['num_images']
  
  GEOMETRY = [[[114.08, 22.31],
               [114.08, 22.36],
               [114.16, 22.36],
               [114.16, 22.31],
               [114.08, 22.31],
              ]]
  
  try:
    if args['geometry']:
      with open(args['geometry'], 'r') as f:
        geom = json.load(f)
      GEOMETRY = geom['features'][0]['geometry']['coordinates']      
  except:
    print('Make sure you have provided the correct geojson file.')
    exit()

  download_image()