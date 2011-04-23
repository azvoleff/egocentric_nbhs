#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import sys
import os

import numpy as np

from osgeo import gdal

# Window size in pixels (2.4 meter pixels for QuickBird multispectral). The 
# window size is the number of pixels included on each side of the center 
# pixel. So a window_size of one gives a square window that is 3 pixels per 
# size. For a 12 meter window on QuickBird multispectral data, use a window 
# size of 2 (giving a window that is 5 pixels per side). The window size 
# determines the maximum buffer radius that can be considered.
#window_size = 0 # Single 2.4m pixel
#window_size = 2 # Window that is 12 meters per side
window_size = 50 # Window that is 12 meters per side
window_width = (window_size*2) + 1

data_filename = 'VIS_%spixels_windows.npy'%window_size
results_filename = 'VIS_%spixels_results.npy'%window_size

if not os.path.exists(data_filename):
    print("***Loading household coordinate data...")
    #ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
    ds = gdal.Open("/media/G-Tech_Data/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
    #ds = gdal.Open("R:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
    #ds = gdal.Open("F:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    gt = ds.GetGeoTransform()
    # Format of ds.GetGeoTransform is:
    # (upper left x, x-size, rotation1, upper left y, rotation2, y-size)
    # upper left is the origin for GDAL
    origin_x = gt[0]
    origin_y = gt[3]
    pixel_width = gt[1]
    pixel_height = gt[5]

    def convert_to_img_coords(x, y):
        img_x = int((x - origin_x)/pixel_width)
        img_y = int((y - origin_y)/pixel_height)
        return img_x, img_y

    hh_coords = np.recfromcsv("WHSA_hh_UTM30.csv")
    # TODO: Fix this. For now drop all hh where their coords are outside the raster 
    # boundary, or where their coords are close enough to the raster boundary that 
    # any part of a window_size sized window would fall outside the raster 
    # boundary.
    lower_right_x = origin_x + cols * pixel_width
    lower_right_y = origin_y + rows * pixel_height
    min_x = origin_x + window_size * pixel_width
    max_x = lower_right_x - (window_size + 1) * pixel_width
    max_y = origin_y - (window_size + 1) * np.abs(pixel_height)
    min_y = lower_right_y + window_size * np.abs(pixel_height)
    initial_shape = hh_coords.shape[0]
    hh_coords = hh_coords[(hh_coords.x > min_x) & (hh_coords.x < max_x),]
    hh_coords = hh_coords[(hh_coords.y > min_y) & (hh_coords.y < max_y),]
    final_shape = hh_coords.shape[0]
    print("Dropped %s households outside raster extent"%(initial_shape-final_shape))

    # Extract a window surrounding each household pixel, where the window has an 
    # edge length (in pixels) of: (window_size*2)*1.
    # The HHID column will be prepended to the output columns to identify the 
    # household ID of each data row, and allow merging of the spectral data with 
    # the household-level data.
    image = ds.ReadAsArray().transpose()
    HHID = []
    first_run = True
    n=0
    for x, y in zip(hh_coords.x, hh_coords.y):
        print n,
        n+=1
        center_x, center_y = convert_to_img_coords(x, y)
        # In the below lieves ul means "upper left", lr means "lower right"
        ul_x, ul_y = center_x-window_size, center_y+window_size+1
        lr_x, lr_y = center_x+window_size+1, center_y-window_size
        box = image[ul_x:lr_x, lr_y:ul_y]
        if first_run==True:
            data = np.array(box, dtype='int8')
            first_run = False
        else:
            data = np.dstack((data, box))
    print("\nSaving data...")
    np.save(data_filename, data)
else:
    print("***Loading data...")
    data = np.load(data_filename)

# Calculate the distance matrix, storing in a matrix the distance of each cell 
# from the center point of the matrix (where the matrix is a square matrix with 
# (window_size*2)*1 rows and columns). The distances in the matrix are 
# expressed directly in distance by multiplying by the resolution of the raster 
# (this converts the distances from being expressed in number of pixels to 
# number of meters).
x_dist = np.arange(-window_size, window_size+1, 1) * np.ones((window_width, 1))
y_dist = x_dist.transpose()
# Use the distance formula (where the center point has a (x,y) location of 
# (0,0):
dists = np.sqrt(x_dist**2+y_dist**2)
 
print("***Running class calculations...")
first_run = True
for max_dist in np.arange(0,window_size,10):
    masked = np.dot(dists < max_dist, data)
    print("Current dist: %s"%max_dist)
    for class_num in xrange(0,5):
        print("\tClass: %s"%class_num)
        this_result = np.sum(np.sum(masked == class_num, 1), 0)
        if first_run==True:
            results = np.array(this_result, dtype='int8')
            first_run = False
        else:
            results = np.dstack(results, this_result)
np.save(results_filename, results)
