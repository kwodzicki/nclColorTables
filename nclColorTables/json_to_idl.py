#!/usr/bin/env python3

import os, json
import numpy as np

from . import loadct

OFFSET = 0.5

def interpRGB(n, rgb):
  """
  Interpolate color table to be 256 colors wide

  Many of the NCL color tables do not have 256 colors
  so this function will expand them to be 256 colors.

  Arguments:
    n (int): Number of colors in the color table
    rgb (list,tuple): Red/Green/Blue values for the table

  Keyword arguments:
    None.
  
  Returns:
    (list,tuple) : Update array with 256 colors

  """

  if n != 256:                                                                  # If not 256 colors
    rgb = list(rgb)                                                             # Convert RGB to list
    dn  = n / 256                                                               # Color indexes for current colors
    xp  = np.arange( n )                                                        # Current color indices for interpolation
    x   = np.round( dn*(np.arange(256) + OFFSET) - OFFSET )                     # Indices to interpolate to
    for i in range( 3 ):                                                        # Iterate over RGB values
      rgb[i] = np.interp(x, xp, rgb[i]).astype(np.uint8)                        # Iterpolate each color channel
  return rgb                                                                    # Return colors

def json_to_IDL(inFile, outDir=None):
  """
  Convert JSON file to IDL color table files

  Arguments:
    inFile (str): File to convert

  Keyword Arguments:
    outDir (str): Directory to place IDL color tables in.
      Default is same directory as inFile

  Returns:
    None.

  """

  with open(inFile, 'rb') as fid:                                               # open json file and load data
    data = json.load(fid)
 
  inDir, inFile = os.path.split( inFile )                                       # Get input file directory path and file name
  outName = os.path.splitext( inFile )[0] + '.tbl'                              # Create IDL color table file name

  if outDir is None: outDir = inDir                                             # If outDir is None, use inDir

  outPath = os.path.join( outDir, outName )                                     # Build path to IDL file
  os.makedirs( outDir, exist_ok = True )                                        # Make sure output directory exists

  i = 0                                                                         # Color table index
  for key, val in data.items():                                                 # Iterate over key/value pairs
    rgb = interpRGB( val['n'], val['rgb'] )                                     # Make sure ther are 256 colors
    loadct.write_IDL_Table(outPath, i, key, rgb)                                # Write data to file
    i += 1                                                                      # Increment color table index

