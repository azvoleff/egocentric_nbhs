#!/usr/bin/Rscript

# Makes correlation of a WHSA variable with a neighborhood-level measure 
# calculated over a range of different neighborhood buffer sizes.

require("plotrix")
require("ggplot2")
require("nlme")
#Variogram(

DPI <- 300
WIDTH <- 9
HEIGHT <- 5.67
theme_update(theme_grey(base_size=18))

variable_name <- "BP_diastolic"
variable_name <- "BP_systolic"
variable_name <- "wealth_quintile"
variable_name <- "W1321A_MALARIA"
variable_col <- grep(variable_name, names(whsa2data050510))
whsa_var <- whsa2data050510[variable_col]

load("~/Data/Ghana/20101206/whsa_ii_data050510.Rdata")

min_radius <- 50
max_radius <- 975
dradius <- 25

radii <- seq(min_radius, max_radius, dradius)

base_class <- 'VEG'
other_classes <- c(base_class, 'NONVEG')
#col_prefix <- 'QB2002_NDVI_'
col_prefix <- 'QB2010_NDVI_'

#data_dir <- '/home/azvoleff/Data/Ghana/Ecocentric_NBH_Data/'
data_dir <- '/home/azvoleff/Data/Ghana/Ecocentric_NBH_Data/20110503_100-to-1000-by-25m/'

load(paste(data_dir, 'merged_buffer_results.Rdata', sep=""))

correlations <- c()
for (radius in radii) {
    base_class_col <- paste(col_prefix, radius, 'm_', base_class, sep='')
    col_names <- paste(col_prefix, radius, 'm_', other_classes, sep='')
    col_nums <- c()
    for (col_name in col_names) {
        col_nums <- c(col_nums,  grep(col_name, names(merged_results)))
    }
    # Calculate a new percentage for the base_class col that ignores all 
    # columns not listed in the other_classes vector.
    nbh_var <- (merged_results[base_class_col] / rowSums(merged_results[col_nums], na.rm=TRUE))*100
    correlations <- c(correlations, cor(whsa_var, nbh_var, use="complete.obs"))
}

plot_title <- paste("Correlation of '", variable_name, "' with ", col_prefix, base_class, sep="")
qplot(radii, correlations, geom="line", main=plot_title, xlab="Buffer Radius (meters)", ylab="Correlation")
plot_filename=paste(data_dir, col_prefix, 'corplot_', variable_name, '.png', sep="")
ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)
