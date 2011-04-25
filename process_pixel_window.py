#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import sys
import os

import numpy as np

from osgeo import gdal

window_size = 125 # Window that is 12 meters per side
# The num_classes specifies how many classes are in the image data. Here it is 
# set to 4, as there are 4 classes (V I and S plus a fourth class meaning 
# undefined). The code assumes that classes are coded in the image data 
# integers ranging from 0 (undefined) to num_classes-1.
num_classes = 3
results_filename = 'VIS_%spixels_results.npz'%window_size

# Disregard the percentage of cover that is undefined, which is coded as zero, 
# so start the classes array from 1 rather than zero.
classes = np.arange(1, num_classes+1)
max_dists = np.arange(10, (window_size*2 + 1)*2.4, 50)

data_filename = 'VIS_%spixels_windows.npz'%window_size
data_array = np.load(data_filename)
data = data_array['data']
window_size = data_array['window_size']

dists_filename = 'VIS_%spixels_dists.npy'%window_size
dists = np.load(dists_filename)
dists = np.tile(dists, (data.shape[2], 1, 1)).transpose()

print("***Running class calculations...")
results = np.zeros((data.shape[2], len(max_dists), len(classes)))
for max_dist_index in xrange(len(max_dists)):
    masked = (dists < max_dists[max_dist_index]) * data
    print("Current dist: %s"%max_dists[max_dist_index])
    
    for class_index in xrange(len(classes)):
        print("\tClass: %s"%classes[class_index])
        these_results = np.sum(np.sum(masked == classes[class_index], 1), 0)
        results[:,max_dist_index, class_index] = these_results

# Now convert counts into percentages of the total area.
# Format of results array:
#     1st dimension: total
#     2nd dimension: max_dist_index
#     3rd dimension: class_index
# Sum up the area for each class and mad_dist, excluding the area in class 0 
# (undefined).
# Now tile the area so there is one area column for each class_index, allowing 
# easy element-by-element division of results by area.shape to get percentage 
# of each neighborhood in each class:
area = np.sum(results[:,:,:], 2) # Areas are expressed in pixels.
for n in xrange(num_classes):
    results[:,:,n] = (results[:,:,n] / area) * 100
np.savez(results_filename, results=results, max_dists=max_dists,
        classes=classes, window_size=window_size)

for n in xrange(len(max_dists)):
    filename = 'VIS_%ipixels_results_maxdist%i.csv'%(window_size, max_dists[n])
    np.savetxt(filename, results[:,n,:])
