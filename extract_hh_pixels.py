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
# size of 2 (giving a window that is 5 pixels per side).
window_size = 0 # Single 2.4m pixel
window_size = 2 # Window that is 12 meters per side

ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("R:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")

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

hh_coords = np.recfromcsv("WHSAII_household_locations_UTM30.csv")

data = []
# The HHID column will be prepended to the output columns to identify the 
# household ID of each data row, and allow merging of the spectral data with 
# the household-level data.
HHID = []
for x, y in zip(hh_coords.x, hh_coords.y):
    img_x, img_y = convert_to_img_coords(x, y)
    window = ds.ReadAsArray(img_x-window_size, img_y-window_size,
            (window_size*2)+1, (window_size*2)+1)
    data.append(window)
data = np.array(data, dtype='float32')
ds.destroy()

sys.exit()

# Calculate range, mean, and standard deviation of each window for each band 
# (or vegetation index).
range = np.max(np.max(data,3),2) - np.min(np.min(data,3),2)

# Need the sums over each window to calculate mean
sums = np.sum(np.sum(data,3),2)
window_width = (window_size*2) + 1
means = sums/(window_width**2)
means_reshaped = means.reshape(means.shape[0],means.shape[1],1,1)
stds = np.sqrt(np.sum(np.sum((data-means_reshaped)**2,3),2)/(window_width**2))

output_file = "spectral_results_%spixelwindow.csv"%(window_size*2+1)
try:
    output_file_obj = open(output_file, "w")
except:
    raise IOError("Unable to open %s"%output_file)
# Make and write the CSV file header:
header_prefixes = ["range_", "mean_", "std_"]
header_suffixes = ["B1", "B2", "B3", "B4", "NDVI", "MSAVI"]
header = "HHID"
for prefix in header_prefixes:
    for suffix in header_suffixes:
        header = header + ", " + prefix + suffix
header = header + "\n"
output_file_obj.write(header)

HHID = np.array(hh_coords.HHID).reshape(np.shape(data)[0],1)
output_data = np.hstack([HHID, range, means, stds])
# First convert them all to strings to get the proper precision
for row in output_data:
    # Start with an integer as HHID field needs no conversion
    output_file_obj.write("%s"%row[0])
    for item in row[1:]:
        output_file_obj.write(", %.10f"%float(item))
    output_file_obj.write("\n")
output_file_obj.close()
