import os
import struct

NAMELEN   = 32
NAMECLIP  = '{:<' + str(NAMELEN) + '.' + str(NAMELEN) + '}'
NAMEFMT   = '{:d}s'.format(NAMELEN)

TABLESZ   = 256
PACKFMT   = '{:d}B'.format(TABLESZ)

def getFileInfo(filePath):
  """
  Gets information about IDL color tables in file

  Arguments:
    filePath (str): Full path to IDL color table

  Keyword arguments:
    None.

  Returns:
    tuple: ntables, names - the number of color tables in the file and the
      names of the color tables

  """

  if not os.path.isfile(filePath):						# If file not exist
    return 0, []								# Return zero and empty list
  elif os.stat(filePath).st_size == 0:
    return 0, []								# Return zero and empty list

  with open(filePath, 'rb') as lun:
    ntables = lun.read(1)							# Read number of tables
    ntables = struct.unpack('B', ntables)[0]					# Unpack byte

    lun.seek( ntables * TABLESZ * 3, 1 )					# Move past tables to read names; names at end
    names   = [lun.read( NAMELEN ).decode().strip() for i in range(ntables)]	# Read 32 bytes from file for each table; decode bytes to string and strip leading/trailing spaces

  return ntables, names

def read_IDL_Table(filePath, tableNum = 0):
  """
  Read in a color table from IDL color table file

  Arguments:
    filePath (str): Full path to IDL color table file

  Keyword arguments:
    tableNum (int): Index of the color table

  Returns:
    tuple: Red, green, blue values for color table

  """

  ntables, names = getFileInfo( filePath )                                      # Get information from file
  if tableNum < 0 or tableNum > ntables:                                        # If tableNum NOT between 0 and number of tables in file
    raise Exception( 'Table number must be between 0-{:d}'.format(ntables) )

  with open(filePath, 'rb') as lun:																						# Open file for reading
    lun.seek( tableNum * TABLESZ * 3 + 1 )					# Skip to table to read
    r       = struct.unpack( PACKFMT, lun.read(TABLESZ) )			# Read in red
    g       = struct.unpack( PACKFMT, lun.read(TABLESZ) )			# Read in green
    b       = struct.unpack( PACKFMT, lun.read(TABLESZ) )			# Read in blue

  return (r, g, b)

def write_IDL_Table(filePath, tableNum, tableName, rgb):
  """
  Write a color table to IDL color table file

  Arguments:
    filePath (str): Full path to IDL color table file
    tableNum (int): Color table index in the file
    tableName (str): Name of the color table in the file
    rgb (list): Red/Green/Blue values of the table

  Keyword Arguments:
    None.

  Returns:
    None.

  """

  ntables, names = getFileInfo(filePath)                                    # Get information about the file
  if ntables == 0:                                                          # If No color tables in file
    lun = open(filePath, 'wb')                                              # Open in write mode
  else:                                                                     # Else
    lun = open(filePath, 'r+b')                                             # open in append mode

  if tableNum >= ntables:                                                   # If table number is greater or equal to number of tables
    lun.write( struct.pack('B', tableNum+1) )                               # Write new number of tables to file
    lun.seek( ntables * TABLESZ * 3, 1 )                                    # Seek to end of all tables
    pad = tableNum - ntables                                                # Compute padding need to go from last table in file to requested table
    if pad > 0:                                                             # If pad is greater than zero (0) 
      names.extend( [''] * pad )                                            # Extend the list of names with empty strings 
      lun.write( b' ' * pad * TABLESZ * 3 )                                 # Pad until were table should be
    names.append( tableName )                                               # Append the requested table name to list of tables
    ntables = tableNum+1                                                    # Set ntables to tablenumber plus 1
  else:                                                                     # Else, just move to table number
    lun.seek( tableNum * TABLESZ * 3 + 1, 0 )                                  # Move to table number requested
    names[tableNum] = tableName                                             # Update the table name at table num

  for i in rgb:                                                             # Iterate over the r,g,b elements
    lun.write( struct.pack( PACKFMT, *i ) )                                 # Pack the data to bytes and write ti file

  lun.seek( ntables * TABLESZ * 3 + 1, 0 )                                  # Seek past all tables to update names
  for name in names:                                                        # Iterate over names
    tableName = NAMECLIP.format(name).encode()                              # Clip the table name to NAMELEN and convert to bytes
    lun.write( struct.pack( NAMEFMT, tableName ) )                          # Write the name
  lun.truncate()                                                            # Truncate to remove any extra data at end

  lun.close()                                                               # Close file
