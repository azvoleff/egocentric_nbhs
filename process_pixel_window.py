#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import sys
import os

import numpy as np

from osgeo import gdal

window_size = 250 # Window that is 12 meters per side

data_filename = 'VIS_%spixels_windows.npz'%window_size
data_array = np.load(data_filename)
data = data_array[data]
window_size = data_array[window_size]

dists_filename = 'VIS_%spixels_dists.npz'%window_size
dists = np.load(dists_filename)

np.savez(data_filename, data=data, window_size=window_size, dists=dists)

print("***Running class calculations...")
classes = np.arange(0,num_classes+1)
max_dists = np.arange(0,window_size,10)
results = np.zeros((np.shape(data)[2], len(classes), len(max_dists)), dtype="int8")
for max_dist_index in xrange(0, len(max_dists)):
    masked = dists < max_dists[max_dist_index] * data
    print "masked.shape:", masked.shape
    print("Current dist: %s"%max_dists[max_dist_index])
    for class_index in xrange(0, num_classes+1):
        print("\tClass: %s"%classes[class_index])
        results[:,class_index, max_dist_index] = np.sum(np.sum(
            masked == classes[class_index], 1), 0)
        np.save(results_filename, results)
