#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system. This code must be run on 
# a 64bit python installation to have enough memory if window_size is greater 
# than about 125 pixels.

import os

import numpy as np

# Window size in pixels (2.4 meter pixels for QuickBird multispectral). The 
# window size is the number of pixels included on each side of the center 
# pixel. So a window_size of one gives a square window that is 3 pixels per 
# size. For a 12 meter window on QuickBird multispectral data, use a window 
# size of 2 (giving a window that is 5 pixels per side). The window size 
# determines the maximum buffer radius that can be considered.
#window_size = 0 # Single 2.4m pixel
#window_size = 2 # Window that is 12 meters per side
window_size = 500
window_width = (window_size*2) + 1

data_filename = 'data/VIS_%spixels_windows.npy'%window_size
dists_filename = 'data/VIS_%spixels_dists.npy'%window_size
data_filename = 'data/NDVI_%spixels_windows.npy'%window_size
dists_filename = 'data/NDVI_%spixels_dists.npy'%window_size

if os.path.exists(data_filename):
    raise IOError('File "%s" already exists. Manually delete file to have script regenerate it.'%data_filename)
if os.path.exists(dists_filename):
    raise IOError('File "%s" already exists. Manually delete file to have script regenerate it.'%dists_filename)

print("***Loading image data...")
image_export_filename = 'data/VIS_image.npz'
#image_export_filename = 'data/Quickbird_2002_NDVI_thresholded.npz'
#image_export_filename = 'data/Quickbird_2010_NDVI_thresholded.npz'
image_data_array = np.load(image_export_filename)
image = image_data_array['image']
cols = image_data_array['cols']
rows = image_data_array['rows']
origin_x = image_data_array['origin_x']
origin_y = image_data_array['origin_y']
pixel_width = image_data_array['pixel_width']
pixel_height = image_data_array['pixel_height']

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
print("\tDropped %s households outside raster extent."%(initial_shape-final_shape))

print("***Extracting windows...")
# Extract a window surrounding each household pixel, where the window has an 
# edge length (in pixels) of: (window_size*2)*1.
data = np.zeros((window_width, window_width, len(hh_coords.x)), dtype='int8')
for hh_num in xrange(0, len(hh_coords.x)):
    x = hh_coords.x[hh_num]
    y = hh_coords.y[hh_num]
    center_x, center_y = convert_to_img_coords(x, y)
    # In the below lieves ul means "upper left", lr means "lower right"
    ul_x, ul_y = center_x-window_size, center_y+window_size+1
    lr_x, lr_y = center_x+window_size+1, center_y-window_size
    box = image[ul_x:lr_x, lr_y:ul_y]
    data[:,:,hh_num] = box
np.save(data_filename, data)
