#!/usr/bin/python
# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system. Thhis code must be run on 
# a 64bit python installation to have enough memory if window_size is greater 
# than about 125 pixels.

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

image_export_filename = 'VIS_image.npz'

if os.path.exists(image_export_filename):
    raise IOError('File "%s" already exists. Manually delete file to have script regenerate it.'%image_export_filename)
print("***Loading image data...")
#ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("/media/G-Tech_Data/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("R:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
ds = gdal.Open("F:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("P:/Data/Imagery/Ghana/VIS/Ghana_VIS_masked_geotiff.tif")
gt = ds.GetGeoTransform()
image = ds.ReadAsArray().transpose()

# Format of ds.GetGeoTransform is:
# (upper left x, x-size, rotation1, upper left y, rotation2, y-size)
# upper left is the origin for GDAL
np.savez(image_export_filename, image=image, origin_x=gt[0], origin_y=gt[3],
        pixel_width=gt[1], pixel_height=gt[5], cols=ds.RasterXSize,
        rows=ds.RasterXSize)
