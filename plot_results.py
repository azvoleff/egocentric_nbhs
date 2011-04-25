import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

window_size = 50

results_filename = 'VIS_%spixels_results.npz'%window_size
results_array = np.load(results_filename)
results = results_array['results']
max_dists = results_array['max_dists']
window_size = results_array['window_size']

for max_dist_index in xrange(len(max_dists)):
    fig = plt.figure(figsize=(12, 8), facecolor='w', edgecolor='k', 
            subplotpars=matplotlib.figure.SubplotParams(left=.05, right=.95, 
            bottom=.05, top=.95))
    ax = fig.add_subplot(111, projection='3d')

    x = np.array(results[:, max_dist_index, 0], dtype="int")
    y = np.array(results[:, max_dist_index, 1], dtype="int")
    z = np.array(results[:, max_dist_index, 2], dtype="int")

    ax.scatter(x, y, z, antialiased=True, alpha=.9)

    ax.set_xlabel("Vegetation (%)")
    ax.set_ylabel("Soil (%)")
    ax.set_zlabel("Impervious (%)")
    max_dist = max_dists[max_dist_index]
    ax.set_title("%s Meter Neighborhood Radius"%max_dist)
    ax.set_xlim3d(0, 100)
    ax.set_ylim3d(0, 100)
    ax.set_zlim3d(0, 100)

    ax.view_init(azim=-70, elev=30)
    filename = "VIS_%spixels_plot_maxdist%s_view1.png"%(window_size, max_dist)
    plt.savefig(filename, dpi=300)

    ax.view_init(azim=70, elev=30)
    filename = "VIS_%spixels_plot_maxdist%s_view2.png"%(window_size, max_dist)
    plt.savefig(filename, dpi=300)
