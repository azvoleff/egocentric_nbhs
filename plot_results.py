import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

window_size = 50

results_filename = 'VIS_%spixels_results.npz'%window_size
results_array = np.load(results_filename)
results = results_array['results']
max_dists = max_dists_array['max_dists']
window_size = window_size_array['window_size']

for max_dist_index in xrange(0:len(max_dists)):
    fig = plt.figure(figsize=(12, 8), facecolor='w', edgecolor='k', 
            subplotpars=matplotlib.figure.SubplotParams(left=.05, right=.95, 
            bottom=.05, top=.95))
    ax = fig.gca(projection='3d')

    x = results[:, max_dist_index, 0]
    y = results[:, max_dist_index, 1]
    z = results[:, max_dist_index, 2]

    points = ax.(x, y, z, rstride=1, cstride=1,
            antialiased=True, alpha=.9)

    ax.set_xlabel("Vegetation (%)")
    ax.set_ylabel("Soil (%)")
    ax.set_zlabel("Impervious (%)")
    max_dist = max_dists[max_dist_index]
    ax.set_title(" %s Meter Neighborhood Radius"%max_dist)
    ax.set_xlim3d(0, 100)
    ax.set_ylim3d(0, 100)
    ax.set_zlim3d(0, 100)
    ax.view_init(azim=-70, elev=30)
    plt.savefig("VIS_%spixels_plot_maxdist%s_view1.png"%(window_size, max_dist), dpi=300)
    ax.view_init(azim=70, elev=30)
    plt.savefig("VIS_%spixels_plot_maxdist%s_view2.png"%(window_size, max_dist), dpi=300)
