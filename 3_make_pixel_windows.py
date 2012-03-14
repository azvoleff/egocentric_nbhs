#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system. This code must be run on 
# a 64bit python installation to have enough memory if window_size is greater 
# than about 125 pixels.

import sys
import os
import csv

# Note the below is needed for the debugging code only
from osgeo import gdal, gdal_array
from osgeo.gdalconst import GDT_Float32

import matplotlib.pyplot as plt

import numpy as np

#data_dir = '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
data_dir = 'M:/Data/Ghana/Egocentric_NBH_Data/'

if not os.path.exists(data_dir):
    raise IOError("Error accessing %s"%data_dir)

# Window size in pixels (2.4 meter pixels for QuickBird multispectral). The 
# window size is the number of pixels included on each side of the center 
# pixel. So a window_size of one gives a square window that is 3 pixels per 
# size. For a 12 meter window on QuickBird multispectral data, use a window 
# size of 2 (giving a window that is 5 pixels per side). The window size 
# determines the maximum buffer radius that can be considered.
window_size = 425 # 425 will allow max radius of 1020 meters with QB imagery
window_width = (window_size*2)

###############################################################################
# Uncomment these two lines to run on VIS image.
base_filename = data_dir + 'VIS_%ipixels_'%window_size
image_filename = data_dir + 'VIS_image.npz'

###############################################################################
# Uncomment one of the two following sets of two lines to run on an NDVI image.
#base_filename = data_dir + '2002NDVI_%ipixels_'%window_size
#image_filename = data_dir + 'Quickbird_2002_NDVI_thresholded.npz'

#base_filename = data_dir + '2010NDVI_%ipixels_'%window_size
#image_filename = data_dir + 'Quickbird_2010_NDVI_thresholded.npz'

###############################################################################
# Main code starts here
def main(argv=None):
    data_filename = base_filename + 'windows.npy'
    hh_filename = base_filename + 'hh.npy'
    nbh_extent_filename = base_filename + 'NBH_extents.csv'
    debug_image_filename = base_filename + 'image_debug.tif'

    if os.path.exists(data_filename):
        raise IOError('File "%s" already exists. Manually delete file to have script regenerate it.'%data_filename)
    if os.path.exists(hh_filename):
        raise IOError('File "%s" already exists. Manually delete file to have script regenerate it.'%hh_filename)

    print("***Loading image data...")
    image_data_array = np.load(image_filename)
    image = image_data_array['image']
    cols = image_data_array['cols']
    rows = image_data_array['rows']
    min_x = image_data_array['origin_x']
    max_y = image_data_array['origin_y']
    pixel_width = image_data_array['pixel_width']
    pixel_height = image_data_array['pixel_height']

    hh_coords = np.recfromcsv(data_dir + "WHSA_hh_UTM30.csv")
    # Drop all hh where their coords are outside the raster boundary.
    max_x = min_x + cols * pixel_width
    min_y = max_y + rows * pixel_height # remember pixel_height is negative
    initial_shape = hh_coords.shape[0]
    hh_coords = hh_coords[(hh_coords.x > min_x) & (hh_coords.x < max_x),]
    hh_coords = hh_coords[(hh_coords.y > min_y) & (hh_coords.y < max_y),]
    final_shape = hh_coords.shape[0]
    np.savetxt(hh_filename, hh_coords, fmt=['%s', '%f', '%f'])
    print("\tDropped %s households outside raster extent."%(initial_shape-final_shape))

    # To allow the buffers to "run-off the page" where households are close to 
    # the sides of the image, pad the array on top, bottom, left, and right 
    # with zeros to expand it so that household buffers will not run off the 
    # page.
    vert_padding = np.zeros((window_size, image.shape[1]))
    image = np.vstack((vert_padding, image, vert_padding))
    horiz_padding = np.zeros((image.shape[0], window_size))
    image = np.hstack((horiz_padding, image, horiz_padding))
    # Account for padding:
    min_x -= window_size * pixel_width
    max_y -= window_size * pixel_height # remember pixel_height is negative

    # Save a GeoTIFF of the padded image for debugging
    driver = gdal.GetDriverByName('GTiff')
    out = driver.Create(debug_image_filename, image.shape[1], image.shape[0], 1, GDT_Float32)
    out.SetGeoTransform([min_x, (max_x - min_x)/image.shape[0], 0, min_y, 0, (max_y - min_y)/image.shape[1]])
    gdal_array.BandWriteArray(out.GetRasterBand(1), image)

    def convert_to_img_coords(x, y):
        # Need to correct here for the zero padding added to the matrix.
        img_x = int((x - min_x)/pixel_width)
        img_y = int((y - max_y)/pixel_height)
        return img_x, img_y

    print("***Extracting windows...")
    # Extract a window surrounding each household pixel, where the window has an 
    # edge length (in pixels) of: (window_size*2)*1.
    data = np.zeros((window_width, window_width, len(hh_coords.x)), dtype='int8')
    nbh_extents = [] # used to write extents to CSV for debugging
    for hh_num in xrange(len(hh_coords.x)):
        woman_id = hh_coords.woman_id[hh_num]
        x = hh_coords.x[hh_num]
        y = hh_coords.y[hh_num]
        # Round off to the nearest center of a cell
        x = round((x - min_x) / pixel_width, 0)*pixel_width + min_x + pixel_width/2
        y = round((y - min_y) / np.abs(pixel_height), 0)*np.abs(pixel_height) + min_y + np.abs(pixel_height)/2
        center_x, center_y = convert_to_img_coords(x, y)
        # In the below lines ul means "upper left", lr means "lower right"
        ul_x, ul_y = center_x-window_size, center_y-window_size # here window_size is positive but remember y increases going down in the image
        lr_x, lr_y = center_x+window_size, center_y+window_size
        #box = image[ul_x:lr_x, lr_y:ul_y] <<--OLD BUG IN CODE
        box = image[ul_y:lr_y, ul_x:lr_x]
        data[:,:,hh_num] = box
        nbh_extents.append([woman_id, ul_x, ul_y, lr_x, lr_y])
    np.save(data_filename, data)
    out_file = open(nbh_extent_filename, "w")
    csv_writer = csv.writer(out_file)
    csv_writer.writerows(nbh_extents)
    out_file.close()

if __name__ == "__main__":
    sys.exit(main())
