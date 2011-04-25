require("plotrix")

window_size <- 50
num_classes <- 3
classes <- seq(1, num_classes+1)
max_dists <- seq(10, (window_size*2 + 1)*2.4, 50)

for (max_dist_index in 1:length(max_dists)) {
    max_dist = max_dists[max_dist_index]
    data_filename = paste('VIS_', window_size, 'pixels_results_maxdist',
            max_dist, '.csv', sep="")
    image_filename = paste('VIS_', window_size, 'pixels_results_maxdist',
            max_dist, '.png', sep="")
    VIS_matrix = read.table(data_filename)
    VIS_matrix[is.na(VIS_matrix)] <- 0
    VIS_matrix = VIS_matrix/100
    VIS_matrix[,1] = round(VIS_matrix[,1],5)
    VIS_matrix[,2] = round(VIS_matrix[,2],5)
    VIS_matrix[,3] = 1 - VIS_matrix[,1]- VIS_matrix[,2]
    VIS_matrix[VIS_matrix<0] <- 0

    png(file=image_filename)
    plot_title = paste(max_dist, "Meter Neighborhood Radius")
    triax.plot(VIS_matrix, main=plot_title)
#               axis.labels=c("Vegetation (%)", "Soil (%)", "Impervious (%)"))
    dev.off()
}
