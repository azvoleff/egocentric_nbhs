#!/usr/bin/python
# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system. Thhis code must be run on 
# a 64bit python installation to have enough memory if window_size is greater 
# than about 125 pixels.

import os

import numpy as np

from osgeo import gdal

###############################################################################
# Accra VIS Imagery
ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("/media/G-Tech_Data/Data/Imagery/Ghana/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("R:/Data/Imagery/Ghana/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("F:/Data/Imagery/Ghana/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
#ds = gdal.Open("P:/Data/Imagery/Ghana/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
image_export_filename = 'data/VIS_image.npz'

###############################################################################
# Accra NDVI images
#ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/Accra_NDVI/cloud_masked_qb02_ndvi_ge120_v02.tif")
#image_export_filename = 'data/Quickbird_2002_NDVI_thresholded.npz'
#ds = gdal.Open("/media/Orange_Data/Data/Imagery/Ghana/Accra_NDVI/cloud_masked_qb10_ndvi_ge120_v02.tif")
#image_export_filename = 'data/Quickbird_2010_NDVI_thresholded.npz'

###############################################################################
# Image processing code (to save image as a numpy array) starts below.
if os.path.exists(image_export_filename):
    raise IOError('File "%s" already exists. Manually delete file to have script regenerate it.'%image_export_filename)
print("***Loading image data...")

gt = ds.GetGeoTransform()
image = ds.ReadAsArray().transpose()

# Format of ds.GetGeoTransform is:
# (upper left x, x-size, rotation1, upper left y, rotation2, y-size)
# upper left is the origin for GDAL
np.savez(image_export_filename, image=image, origin_x=gt[0], origin_y=gt[3],
        pixel_width=gt[1], pixel_height=gt[5], cols=ds.RasterXSize,
        rows=ds.RasterXSize)
