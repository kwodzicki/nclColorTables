import logging

LOG  = logging.getLogger(__name__)
LOG.setLevel( logging.DEBUG )
LOG.addHandler( logging.StreamHandler() )
LOG.handlers[0].setLevel( logging.INFO )

URL    = 'https://www.ncl.ucar.edu/Document/Graphics/color_table_gallery.shtml'
CT_URL = 'https://www.ncl.ucar.edu/Document/Graphics/ColorTables/Files/{}.rgb'
