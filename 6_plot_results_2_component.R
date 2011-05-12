#!/usr/bin/Rscript

# Makes mixing diagrams of VIS proportions for a series of different buffer 
# sizes surrounding the WHSA households.

require("plotrix")
require("ggplot2")
DPI <- 300
WIDTH <- 9
HEIGHT <- 5.67
theme_update(theme_grey(base_size=18))

min_radius <- 50
max_radius <- 975
dradius <- 25

radii <- seq(min_radius, max_radius, dradius)

classes <- c('NONVEG', 'VEG')
#col_prefix <- 'QB2002_NDVI_'
col_prefix <- 'QB2010_NDVI_'

#data_dir <- '/home/azvoleff/Data/Ghana/Ecocentric_NBH_Data/'
data_dir <- '/home/azvoleff/Data/Ghana/Ecocentric_NBH_Data/20110503_100-to-1000-by-25m/'

load(paste(data_dir, 'merged_buffer_results.Rdata', sep=""))

if (length(classes) != 2) {
    stop("Length of classes MUST equal 2")
}


for (radius in radii) {
    col_names <- paste(col_prefix, radius, 'm_', classes, sep='')
    col_nums <- c()
    for (col_name in col_names) {
        col_nums <- c(col_nums,  grep(col_name, names(merged_results)))
    }
    proportions <- merged_results[col_nums]
    names(proportions) <- classes
    # Calculate a new percentage ignoring the third component, using only the 
    # selected two components in the sum.
    new_total = proportions[1] + proportions[2]
    proportions[1] <- (proportions[1] / new_total)*100
    proportions[2] <- (proportions[2] / new_total)*100
    proportions[proportions<0] <- 0
    # Drop any rows that have an NA in them
    proportions <- proportions[!is.na(proportions[1]),]
    proportions <- proportions[!is.na(proportions[2]),]

    proportions <- stack(proportions)

    area_hectares = round((pi*radius**2)/10000,1)

    plot_title <- paste(radius, "m radius (", area_hectares, " hectares)", sep="")
    # NOTE: mar format: c(bottom, left, top, right)
    q <- qplot(values, facets=ind~., geom="histogram", binwidth=5, data=proportions, main=plot_title, xlab="Percentage in Class", ylab="Number of Neighborhoods")
    plot_filename=paste(data_dir, col_prefix, '2component_plot_', radius, 'mradius.png', sep="")
    ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)
}
