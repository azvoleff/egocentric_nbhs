#!/usr/bin/Rscript

# Makes mixing diagrams of VIS proportions for a series of different buffer 
# sizes surrounding the WHSA households.

require("plotrix")

window_size <- 125
max_dists <- seq(25, (window_size*2 + 1)*2.4, 25)

filename_base = paste('VIS_', window_size, 'pixels_results_', sep="")

maxdists_filename = paste(filename_base, 'maxdists.csv', sep="")
maxdists = read.table(maxdists_filename)

image_filename = paste(filename_base, 'mixingdiagram.pdf', sep="")

pdf(file=image_filename)
for (max_dist_index in 1:length(max_dists)) {
    max_dist = max_dists[max_dist_index]
    data_filename = paste(filename_base, 'maxdist', max_dist, '.csv', sep="")
    VIS_matrix = read.table(data_filename)
    VIS_matrix[is.na(VIS_matrix)] <- 0
    VIS_matrix[,1] = round(VIS_matrix[,1],5)
    VIS_matrix[,2] = round(VIS_matrix[,2],5)
    VIS_matrix[,3] = 100 - VIS_matrix[,1]- VIS_matrix[,2]
    VIS_matrix[VIS_matrix<0] <- 0

    plot_title = paste(max_dist, "Meter Neighborhood Radius")
    triax.plot(VIS_matrix, main=plot_title, show.grid=TRUE,
            axis.labels=c("Vegetation", "Soil", "Impervious"))
}
dev.off()
