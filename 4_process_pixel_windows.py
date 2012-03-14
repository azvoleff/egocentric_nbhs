#!/usr/bin/python

# Used to extract a window of pixel around a each point in a set of points.
# The image must be in a projected coordinate system.

import sys
import os

import numpy as np

#data_dir = '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
#data_dir = 'F:/Data/Ghana/Egocentric_NBH_Data/'
data_dir = 'M:/Data/Ghana/Egocentric_NBH_Data/'

if not os.path.exists(data_dir):
    raise IOError("Error accessing %s"%data_dir)

# max_buffer_radius species the maximum buffer size to consider (in meters) by 
# specifying the maximum buffer radius.
min_buffer_radius = 25
max_buffer_radius = 1000
buffer_radius_increment = 25

# Here window_size is in PIXELS not meters. So it is the maximum diameter 
# buffer that can be considered (which in meters is equal to window_size * 
# resolution). The max_buffer_radius specifies the maximum buffer size to 
# consider in the calculations, whereas window_size tells the script which 
# precalculated window data set to use.
window_size = 425
window_width = (window_size*2)
# Resolution is the resolution of the image in meters.
resolution = 2.4

###############################################################################
# Uncomment these two lines to run on VIS image.
#base_filename = data_dir + 'VIS_%ipixels_'%window_size
# For the VIS classification, 0 is unknown, 1 is veg, 2 is soil, and 3 is 
# impervious.
#classes_text_names_prefix = 'QB2002_OBIA'
#classes_text_names = ["NA", "VEG", "SOIL", "IMPERVIOUS"]

###############################################################################
# Uncomment one of the two following sets of two lines to run on an NDVI image.
# Note no class coding: for the NDVI thresholding, 0 is unknown, 1 is 
# non-vegetation, and 2 is vegetation.
#base_filename = data_dir + '2002NDVI_%ipixels_'%window_size
#classes_text_names_prefix = 'QB2002_NDVI'
#classes_text_names = ["NA", "NONVEG", "VEG"]

base_filename = data_dir + '2010NDVI_%ipixels_'%window_size
classes_text_names_prefix = 'QB2010_NDVI'
classes_text_names = ["NA", "NONVEG", "VEG"]

###############################################################################
# Main code starts here
def main(argv=None):
    results_filename = base_filename + 'results.npz'

    data_filename = base_filename + 'windows.npy'
    data = np.load(data_filename)

    hh_filename = base_filename + 'hh.npy'
    hh_data = np.loadtxt(hh_filename, dtype={'names': ('woman_id', 'x', 'y'), 'formats': ('S11', 'f4', 'f4')})

    max_buffer_radius_possible = window_size*resolution
    assert max_buffer_radius <= max_buffer_radius_possible, "max_buffer_radius with %s dataset cannot exceed %.2f meters"%(data_filename, max_buffer_radius_possible)

    # The code assumes that classes are coded in the image data as
    # integers ranging from 0 (undefined) to the length of classes_text_names.
    classes = np.arange(0, len(classes_text_names))
    max_dists = np.arange(min_buffer_radius, max_buffer_radius, buffer_radius_increment)

    print("***Calculating distance matrix...")
    # Calculate the distance matrix, storing in a matrix the distance of each cell 
    # from the center point of the matrix (where the matrix is a square matrix with 
    # (window_size*2)*1 rows and columns). The distances in the matrix are 
    # expressed directly in distance by multiplying by the resolution of the raster 
    # (this converts the distances from being expressed in number of pixels to 
    # number of meters).
    x_dist = np.arange(-window_size, window_size, 1) * np.ones((window_width, 1))
    # Convert to meters
    x_dist = x_dist * np.abs(resolution)
    y_dist = x_dist.transpose() * np.abs(resolution)
    # Use the distance formula (where the center point has a (x,y) location of 
    # (0,0):
    dists = np.sqrt(x_dist**2+y_dist**2)
    # Add a third dimension to the dists matrix (so it is window_size x window_size 
    # x 1), so that it can be used as a mask with the 3 dimensional data matrix.
    dists = np.resize(dists, (dists.shape[0], dists.shape[1], 1))

    print("***Running class calculations...")
    results = np.zeros((data.shape[2], len(max_dists), len(classes)))
    masked = np.zeros((dists.shape[0], dists.shape[1], data.shape[2]), dtype="bool")
    # To allow tracking of missing data, temporarily recode all the variables by 
    # adding one. This will allow true missing data (now coded as 1 rather than 
    # zero) to be distinguished from data that was just masked out because it is 
    # beyond the buffer. This means we also need to add 1 to all of the 'classes' 
    # values.
    data = data + 1
    classes = classes + 1
    column_headers = ["woman_id", "x", "y"]
    for max_dist_index in xrange(len(max_dists)):
        cur_max_dist = max_dists[max_dist_index]
        print("Current dist: %s"%cur_max_dist)
        masked = (dists < cur_max_dist) * data
        for class_index in xrange(len(classes)):
            print("\t\tClass: %s"%classes[class_index])
            # TODO: could use np.apply_over_axes here
            these_results = np.sum(np.sum(masked == classes[class_index], 1), 0)
            results[:,max_dist_index, class_index] = these_results
            column_headers.append("%s_%im_%s"%(classes_text_names_prefix, cur_max_dist, classes_text_names[class_index]))
    # Make column_headers a row vector
    column_headers = np.array(column_headers)

    # Now convert counts into percentages of the total area for that particular 
    # buffer radius.
    # Format of results array:
    #     1st dimension: total
    #     2nd dimension: max_dist_index
    #     3rd dimension: class_index
    # Sum up the area for each class and max_dist, excluding the area in class 0 
    # (undefined).
    area = np.sum(results[:,:,:], 2) # Areas are expressed in pixels.
    for n in xrange(len(classes_text_names)):
        results[:,:,n] = (results[:,:,n] / area) * 100
    np.savez(results_filename, results=results, max_dists=max_dists,
            classes=classes, window_size=window_size)
    results_reshaped = results.reshape((results.shape[0], -1, 1))

    # Write results to CSV for import into R, Stata, SPSS, SAS, etc.
    results_csv_filename = base_filename + 'results.csv'
    try:
        output_file_obj = open(results_csv_filename, "w")
    except:
        raise IOError("Unable to open %s"%output_file)
    # Make and write the CSV file header:
    header = column_headers[0]
    for column_header in column_headers[1:]:
        header = header + "," + column_header
    header = header + "\n"
    output_file_obj.write(header)
    for row_num in xrange(results_reshaped.shape[0]):
        row_part1 = hh_data[row_num]
        # Start with an integer as woman_id field needs no conversion
        woman_id = row_part1[0].strip('"')
        output_file_obj.write("%s"%woman_id)
        output_file_obj.write(",%.10f"%row_part1[1])
        output_file_obj.write(",%.10f"%row_part1[2])
        row_part2 = results_reshaped[row_num, :]
        # Now write out the NBH fraction data
        for item in row_part2:
            output_file_obj.write(",%.10f"%float(item))
        output_file_obj.write("\n")
    output_file_obj.close()

if __name__ == "__main__":
    sys.exit(main())
