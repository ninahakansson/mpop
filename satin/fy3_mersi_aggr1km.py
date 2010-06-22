#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010.

# SMHI,
# Folkborgsvägen 1,
# Norrköping, 
# Sweden

# Author(s):
 
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of mpop.

# mpop is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# mpop is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# mpop.  If not, see <http://www.gnu.org/licenses/>.

"""Interface to 1km agregated MERSI hdf5 level 1 format.
"""


from ConfigParser import ConfigParser
from satin import BASE_PATH
import os.path
import numpy as np
from satin.logger import LOG

import _pyhl

def load(satscene):
    """Read data from file and load it into *satscene*.
    """    
    conf = ConfigParser()
    conf.read(os.path.join(BASE_PATH, "etc", satscene.fullname + ".cfg"))
    options = {}
    for option, value in conf.items(satscene.instrument_name+'-level2', raw = True):
        options[option] = value
    CASES[satscene.instrument_name](satscene, options)


def load_1km_aggregated_mersi(satscene, options):
    """Read 1km agregated mersi data from file and load it into *satscene*.
    """
    # Example: FY3A_MERSI_GBAL_L1_20100308_0915_1000M_MS.HDF
    filename = satscene.time_slot.strftime("FY3A_MERSI_GBAL_L1_%Y%m%d_%H%M_1000M_MS.HDF")
    filename = os.path.join(options["dir"], filename)
    
    a = _pyhl.read_nodelist(filename)
    b = a.getNodeNames()
    # Should only select/fetch the datasets needed. FIXME!
    a.selectAll()
    a.fetch()

    # MERSI Channel 1-4: EV_250_Aggr.1KM_RefSB
    # MERSI Channel 5: EV_250_Aggr.1KM_Emissive
    # MERSI Channel 6-20: EV_1KM_RefSB

    datasets = ['/EV_250_Aggr.1KM_RefSB',
                '/EV_250_Aggr.1KM_Emissive',
                '/EV_1KM_RefSB']

    for nodename in datasets:
        print "Nodename: ",nodename
        band_data = a.getNode(nodename).data()
        valid_range = a.getNode('%s/valid_range' % (nodename)).data()
        band_names = a.getNode('%s/band_name' % (nodename)).data().split(",")
        # Special treatment of the situation where the bandnames are stored
        # as '6~20' (quite inconvenient):
        if '6~20' in band_names:
            band_names = ['6','7','8','9','10','11','12','13',
                          '14','15','16','17','18','19','20']
            
        for (i, band) in enumerate(band_names):
            print "i,band: ",i,band
            #print "Shape = ",band_data[i].shape
            #print "valid_range = ",valid_range
            satscene[band] = np.ma.masked_outside(band_data[i],
                                                  valid_range[0],
                                                  valid_range[1],
                                                  copy = False)

def get_lat_lon(satscene, resolution):
    """Read lat and lon.
    """
    del resolution
    
    conf = ConfigParser()
    conf.read(os.path.join(BASE_PATH, "etc", satscene.fullname + ".cfg"))
    options = {}
    for option, value in conf.items(satscene.instrument_name+'-level2', raw = True):
        options[option] = value
        
    return LAT_LON_CASES[satscene.instrument_name](satscene, options)

def get_lat_lon_1km_aggregated_mersi(satscene, options):
    """Read latitude and longitude for each (aggregated) pixel.
    """
    # Example: FY3A_MERSI_GBAL_L1_20100308_0915_1000M_MS.HDF
    filename = satscene.time_slot.strftime("FY3A_MERSI_GBAL_L1_%Y%M%D_%H%M_1000M_MS.HDF")
    filename = os.path.join(options["dir"], filename)

    a = _pyhl.read_nodelist(filename)
    b = a.getNodeNames()
    # Should only select/fetch the datasets needed. FIXME!
    a.selectAll()
    a.fetch()

    lat = a.getNode("/Latitude").data()
    lon = a.getNode("/Longitude").data()

    return lat, lon

CASES = {
    "mersi": load_1km_aggregated_mersi
    }

LAT_LON_CASES = {
    "mersi": get_lat_lon_1km_aggregated_mersi
    }
