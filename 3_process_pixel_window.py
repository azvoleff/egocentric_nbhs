#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import sys
import os

import numpy as np

window_size = 500
# The num_classes specifies how many classes are in the image data. Here it is 
# set to 4, as there are 4 classes (V I and S plus a fourth class meaning 
# undefined). The code assumes that classes are coded in the image data 
# integers ranging from 0 (undefined) to num_classes-1.
num_classes = 3
results_filename = 'VIS_%spixels_results.npz'%window_size

# Disregard the percentage of cover that is undefined, which is coded as zero, 
# so start the classes array from 1 rather than zero.
classes = np.arange(1, num_classes+1)
max_dists = np.arange(25, (window_size + 1)*2.4, 25)

data_filename = 'VIS_%spixels_windows.npy'%window_size
data = np.load(data_filename)

dists_filename = 'VIS_%spixels_dists.npy'%window_size
dists = np.load(dists_filename)
# Add a third dimension to the dists matrix (so it is window_size x window_size 
# x 1), so that it can be used as a mask with the 3 dimensional data matrix.
dists = np.resize(dists, (dists.shape[0], dists.shape[1], 1))

print("***Running class calculations...")
results = np.zeros((data.shape[2], len(max_dists), len(classes)))
masked = np.zeros((dists.shape[0], dists.shape[1], data.shape[2]), dtype="bool")
for max_dist_index in xrange(len(max_dists)):
    print("Current dist: %s"%max_dists[max_dist_index])
    masked = (dists < max_dists[max_dist_index]) * data

    for class_index in xrange(len(classes)):
        print("\t\tClass: %s"%classes[class_index])
        # TODO: could use np.apply_over_axes here
        these_results = np.sum(np.sum(masked == classes[class_index], 1), 0)
        results[:,max_dist_index, class_index] = these_results

# Now convert counts into percentages of the total area.
# Format of results array:
#     1st dimension: total
#     2nd dimension: max_dist_index
#     3rd dimension: class_index
# Sum up the area for each class and max_dist, excluding the area in class 0 
# (undefined).
area = np.sum(results[:,:,:], 2) # Areas are expressed in pixels.
for n in xrange(num_classes):
    results[:,:,n] = (results[:,:,n] / area) * 100
np.savez(results_filename, results=results, max_dists=max_dists,
        classes=classes, window_size=window_size)

for n in xrange(len(max_dists)):
    filename = 'VIS_%ipixels_results_maxdist%i.csv'%(window_size, max_dists[n])
    np.savetxt(filename, results[:,n,:])

filename = 'VIS_%ipixels_results_maxdists.csv'%window_size
np.savetxt(filename, max_dists)
filename = 'VIS_%ipixels_results_classes.csv'%window_size
np.savetxt(filename, classes)
