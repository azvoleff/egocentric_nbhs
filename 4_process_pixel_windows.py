#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import sys
import os

import numpy as np

# Here window_size is is meters - the maximum size of the buffer to be 
# considered.
window_size = 500

# Resolution is the resolution of the image in meters.
resolution = 2.4

# The num_classes specifies how many classes are in the image data. Here it is 
# set to 4, as there are 4 classes (V I and S plus a fourth class meaning 
# undefined). The code assumes that classes are coded in the image data 
# integers ranging from 0 (undefined) to num_classes-1.
num_classes = 3
base_filename = 'data/NDVI_%ipixels_'%window_size

results_filename = base_filename + 'results.npz'

# Disregard the percentage of cover that is undefined, which is coded as zero, 
# so start the classes array from 1 rather than zero.
classes = np.arange(1, num_classes+1)
max_dists = np.arange(25, (window_size + 1)*resolution, 25)

data_filename = base_filename + '%windows.npy'
data = np.load(data_filename)

print("\n***Calculating distance matrix...")
# Calculate the distance matrix, storing in a matrix the distance of each cell 
# from the center point of the matrix (where the matrix is a square matrix with 
# (window_size*2)*1 rows and columns). The distances in the matrix are 
# expressed directly in distance by multiplying by the resolution of the raster 
# (this converts the distances from being expressed in number of pixels to 
# number of meters).
x_dist = np.arange(-window_size, window_size+1, 1) * np.ones((window_width, 1))
# Convert to meters
x_dist = x_dist * np.abs(resolution)
y_dist = x_dist.transpose()*np.abs(resolution)
# Use the distance formula (where the center point has a (x,y) location of 
# (0,0):
dists = np.sqrt(x_dist**2+y_dist**2)
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
    filename = base_filename + 'results_maxdist%i.csv'%max_dists[n]
    np.savetxt(filename, results[:,n,:])

filename = base_filename + 'results_maxdists.csv'
np.savetxt(filename, max_dists)
filename = base_filename + 'results_classes.csv'
np.savetxt(filename, classes)
