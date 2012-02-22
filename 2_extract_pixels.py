#!/usr/bin/python
# Uses GDAL to convert a geotiff image to a numpy array for later processing to 
# choose a window of pixels around each of the WHSA surveyed households.

import os

import numpy as np

from osgeo import gdal

#data_dir = '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
data_dir = 'G:/Data/Ghana/Egocentric_NBH_Data/'

###############################################################################
# Accra VIS Imagery
ds = gdal.Open("G:/Data/Imagery/Ghana/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
image_export_filename = data_dir + 'VIS_image.npz'

###############################################################################
# Accra NDVI images
#ds = gdal.Open("G:/Data/Imagery/Ghana/Accra_NDVI/cloud_masked_qb02_ndvi_ge120_v02.tif")
#image_export_filename = data_dir + 'Quickbird_2002_NDVI_thresholded.npz'
#ds = gdal.Open("G:/Data/Imagery/Ghana/Accra_NDVI/cloud_masked_qb10_ndvi_ge120_v02.tif")
#image_export_filename = data_dir + 'Quickbird_2010_NDVI_thresholded.npz'

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
