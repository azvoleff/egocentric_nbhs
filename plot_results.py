import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

for index in xrange(0:len(max_dists)):
    max_dist
    fig = plt.figure(figsize=(12, 8), facecolor='w', edgecolor='k', 
            subplotpars=matplotlib.figure.SubplotParams(left=.05, right=.95, 
            bottom=.05, top=.95))
    ax = fig.gca(projection='3d')
    S1_data = np.genfromtxt(model + datafile_suffix, delimiter=",")
    surf = ax.plot(results[1], Y_S1, Z_S1, rstride=1, cstride=1,
            linewidth=0, antialiased=True, alpha=.9)
    ax.set_xlabel("Vegetation (%)")
    ax.set_ylabel("Soil (%)")
    ax.set_zlabel("Impervious (%)")
    ax.set_xlim3d(0, 100)
    ax.set_ylim3d(0, 100)
    ax.set_zlim3d(0, 100)
    ax.view_init(azim=-70, elev=30)
    plt.savefig("VIS_%spixels_plot_maxdist%s_view1.png"%(window_size, max_dist), dpi=300)
    ax.view_init(azim=70, elev=30)
    plt.savefig("VIS_%spixels_plot_maxdist%s_view2.png"%(window_size, max_dist), dpi=300)
