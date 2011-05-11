#!/usr/bin/Rscript

# Makes mixing diagrams of VIS proportions for a series of different buffer 
# sizes surrounding the WHSA households.

require("plotrix")

min_radius <- 50
max_radius <- 975
dradius <- 25

radii <- seq(min_radius, max_radius, dradius)

classes <- c('NA', 'NONVEG', 'VEG')
#col_prefix <- 'QB2002_NDVI_'
col_prefix <- 'QB2010_NDVI_'

#classes <- c('VEG', 'SOIL', 'IMPERVIOUS')
#col_prefix <- 'QB2002_OBIA_'

#data_dir <- '/home/azvoleff/Data/Ghana/Ecocentric_NBH_Data/'
data_dir <- '/home/azvoleff/Data/Ghana/Ecocentric_NBH_Data/20110503_100-to-1000-by-25m/'

load(paste(data_dir, 'merged_buffer_results.Rdata', sep=""))

if (length(classes) != 3) {
    stop("Length of classes MUST equal 3")
}


pdf(file=paste(data_dir, col_prefix, 'ternary_plot.pdf', sep=""))
par(cex=1.4, oma=c(0, 0, .5, 0))
for (radius in radii) {
    col_names <- paste(col_prefix, radius, 'm_', classes, sep='')
    col_nums <- c()
    for (col_name in col_names) {
        col_nums <- c(col_nums,  grep(col_name, names(merged_results)))
    }
    prop_matrix <- merged_results[col_nums]
    prop_matrix[is.na(prop_matrix)] <- 0
    prop_matrix[,1] <- round(prop_matrix[,1],5)
    prop_matrix[,2] <- round(prop_matrix[,2],5)
    prop_matrix[,3] <- 100 - prop_matrix[,1]- prop_matrix[,2]
    prop_matrix[prop_matrix<0] <- 0

    area_hectares = round((pi*radius**2)/10000,1)

    plot_title <- paste(radius, "m radius (", area_hectares, " hectares)", sep="")
    # NOTE: mar format: c(bottom, left, top, right)
    triax.plot(prop_matrix, main=plot_title, sub="test", show.grid=TRUE,
            axis.labels=classes, mar=c(4, 0, 1, 0))
}
dev.off()
