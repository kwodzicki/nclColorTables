import logging
import os, re, json
from urllib.request import urlopen

from bs4 import BeautifulSoup as BS

import numpy as np

from . import URL, CT_URL

pattern = re.compile( r'(\d+(?:\.\d+)?)' )

def parseColors( data ):
  """
  Parse red/green/blue information from HTML data

  Arguments:
    data (bytes): Byte data from website

  Keyword arguments:
    None.

  Returns:
    dict: Color table information

  """

  log = logging.getLogger(__name__)                                             # logger
  log.debug( 'Parsing a color table' )                                          # Log debug info
  colors = {'n' : 0, 'rgb' : [ [], [], [] ]}                                    # Initialize color dict
  for line in data.decode('utf-8').splitlines():                                # Iterate over lines in decoded data
    vals = pattern.findall( line )                                              # Get values using regex
    if len(vals) >= 3:                                                          # If 3 or more values
      colors['n'] += 1                                                          # Increment number of colors in table
      for i in range( 3 ):                                                      # Iterate over 3 colors
        colors[ 'rgb' ][i].append( float(vals[i]) )                             # Append to RGB array as float
  tmp = np.asarray( colors['rgb'] )                                             # Convert RGB data to numpy array
  if tmp.max() <= 1.0: tmp *= 255                                               # If maximum color values is <= 1, then convert to 255 range
  colors['rgb'] = np.clip(tmp, 0, 255).astype(np.uint8).tolist()                # Clip data to 0-255, convert to uint8, then convert to list

  return colors

################################################################################
def getColorTableNames( ):
  """
  Get names of color tables from NCL website

  Arguments:
    None.

  Keyword arguments:
    None.

  Returns:
    dict: Color table name information

  """

  names  = {}                                                                   # Initialize dict
  html   = urlopen( URL ).read()                                                # Get HTML data
  parsed = BS(html, 'lxml')                                                     # Parse the data
  for table in parsed.find_all('table'):                                        # Iterate over all tables
    for row in table.find_all('tr'):                                            # Iterate over all rows in a table
      for col in row.find_all('td'):                                            # Iterate over all columns in the row
        text  = col.get_text()                                                  # Get text in the column
        if 'colors' in text:                                                    # If 'colors' in column text
          ctName = table.findPrevious('h2')                                     # Get table name as previous instance of header in column
          if ctName is not None:                                                # If ctName is NOT None (i.e., header was found)
            ctName = ctName.get_text()                                          # Get text
            ctName = ctName.replace(' color tables', '')                        # Replace instance of ' color tables'
            if ctName not in names: names[ctName] = {}                          # If color table NOT in names; create new sub dict
          for line in text.splitlines():                                        # Iterate over lines in text
            if (line != '') and ('colors' not in line):                         # If not match this (not sure why)
              names[ctName][line] = None                                        # Set line to None
  return names

def jsonFilename( outdir, name ):
  """
  Generate path to JSON file

  Format the name of the NCL color table family to be a 'good'
  file name.

  Arguments:
    outdir (str): File directory path
    name (str): Base name for the file; this is NCL color table family

  Keyword arguments:
    None.

  Returns:
    str: JSON file path

  """

  if not os.path.isdir( outdir ): os.makedirs( outdir )                         # If outdir not exist, create it
  file = '{}.json'.format( '_'.join( name.split() ) )                           # Split name on space, join on underscore, and add .json extension
  file = file.replace('/', '-')                                                 # Replace any '/' with '-'
  return os.path.join( outdir, file )                                           # Return path
  
def createJson( outdir, name, tables ): 
  """
  Store color table data in JSON file

  Arguments:
    outdir (str): File directory path
    name (str): Name of the NCL color table family
    tables (dict): Information for color tables in the family

  Keyword arguments:
    None.

  Returns:
    str: Path to the JSON file

  """
  path = jsonFilename( outdir, name )                                           # Build path to file
  with open(path, 'w') as fid:                                                  # Open file for writing
    json.dump( tables, fid, indent = 2 )                                        # Dump data
  return path                                                                   # Return path

def getColorTable(ctName = None, JSON = None):
  """
  Scrape color table data from NCL website
  """

  tables = getColorTableNames()
  files  = []
  names  = list(tables.keys())
  for name in names:
    if ctName and name != ctName:
      tables.pop(name)
      continue
    if JSON:
      path = jsonFilename(JSON, name) 
      if os.path.isfile(path):
        with open(path, 'r') as fid:
          data = json.load(fid)
      else:
        data = None  

    if data is None:
      for table in tables[name].keys():
        url  = CT_URL.format( table )
        data = urlopen( URL ).read()
        tables[name][ table ] = parseColors( data )
        files.append( createJson( JSON, name, tables[name] ) )
    else:
      tables[name] = data
      files.append( path )

  return tables, files
