#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import csv
import sys

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
window_size = 250 # Window that is 12 meters per side

#ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("R:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
ds = gdal.Open("F:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")

width = ds.RasterXSize
height = ds.RasterYSize
gt = ds.GetGeoTransform()
# Format of ds.GetGeoTransform is:
# (ULX, x-size, ?, ULY, y-size, ?)

print width, height
print gt

def convert_to_img_coords(x, y):
    x_res = gt[1]
    y_res = gt[5]
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]
    img_x =  int(np.floor((x - minx)/x_res))
    img_y =  int(np.floor((y - maxy)/y_res))
    return img_x, img_y

# Calculate the distance matrix, storing in a matrix the distance of each cell 
# from the center point of the matrix (where the matrix is a square matrix with 
# (window_size*2)*1 rows and columns). The distances in the matrix are 
# expressed in number of pixels - not directly in distance.

hh_coords = np.recfromcsv("WHSA_hh_UTM30.csv")
# Extract a window surrounding each household pixel, where the window has an 
# edge length (in pixels) of: (window_size*2)*1.
# The HHID column will be prepended to the output columns to identify the 
# household ID of each data row, and allow merging of the spectral data with 
# the household-level data.
data = []
HHID = []
window = ds.ReadAsArray(img_x-window_size, img_y-window_size,
    (window_size*2)+1, (window_size*2)+1)
for x, y in zip(hh_coords.x, hh_coords.y):
    img_x, img_y = convert_to_img_coords(x, y)
    window = ds.ReadAsArray(img_x-window_size, img_y-window_size,
            (window_size*2)+1, (window_size*2)+1)
    data.append(window)
data = np.array(data, dtype='float32')
ds.destroy()

# Calculate range, mean, and standard deviation of each window for each band 
# (or vegetation index).
range = np.max(np.max(data,3),2) - np.min(np.min(data,3),2)

# Need the sums over each window to calculate mean
sums = np.sum(np.sum(data,3),2)
window_width = (window_size*2) + 1
means = sums/(window_width**2)
means_reshaped = means.reshape(means.shape[0],means.shape[1],1,1)
stds = np.sqrt(np.sum(np.sum((data-means_reshaped)**2,3),2)/(window_width**2))
