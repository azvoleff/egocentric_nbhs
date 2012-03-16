#!/usr/bin/Rscript

require(ggplot2)
DPI <- 300
WIDTH <- 9
HEIGHT <- 5.67
theme_update(theme_grey(base_size=12))
update_geom_defaults("point", aes(size=3))
update_geom_defaults("line", aes(size=1))

# Reads and outputs the coordinates of each WHSA household to both a shapefile 
# and to a csv.

#data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
#data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/20110503_100-to-1000-by-25m/'
data_dir <- 'M:/Data/Ghana/Egocentric_NBH_Data/'

window_size <- 425

# Add back in the household with longitude < .3 (was too far from the rest to 
# be a real datapoint so it was dropped). The woman_id is: 10602504902
load("M:/Data/Ghana/WHSA/whsa_ii_data050510.Rdata")
extra_hh <- whsa2data050510[whsa2data050510$longitude < -.3,]
extra_hh <- data.frame(woman_id=extra_hh$woman_id)

VIS_2002_filename <- paste(data_dir, 'VIS_', window_size, 'pixels_results.csv', sep="")
NDVI_2002_filename <- paste(data_dir, '2002NDVI_', window_size, 'pixels_results.csv', sep="")
NDVI_2010_filename <- paste(data_dir, '2010NDVI_', window_size, 'pixels_results.csv', sep="")

VIS_2002 <- read.csv(VIS_2002_filename)
NDVI_2002 <- read.csv(NDVI_2002_filename)
NDVI_2010 <- read.csv(NDVI_2010_filename)

# First merge the two NDVI datasets - the VIS dataset has NAs for many 
# households as the VIS image does not cover the full extent of the WHSA study 
# area.
# Drop  duplicate columns in NDVI_2010 and VIS_2002:
NDVI_2010 <- NDVI_2010[!(names(NDVI_2010) %in% c("x", "y"))]
VIS_2002 <- VIS_2002[!(names(VIS_2002) %in% c("x", "y"))]

merged_results <- merge(NDVI_2002, NDVI_2010, by=c("woman_id"), sort=TRUE)
merged_results <- merge(merged_results, VIS_2002, by=c("woman_id"), all.x=TRUE)
merged_results <- merge(merged_results, extra_hh, all=TRUE)

merged_results_CSV_file <- paste(data_dir, 'merged_buffer_results.csv', sep="")
merged_results_Rdata_file <- paste(data_dir, 'merged_buffer_results.Rdata', sep="")

write.csv(merged_results, merged_results_CSV_file, row.names=F)
save(merged_results, file=merged_results_Rdata_file)

qplot(merged_results[merged_results$QB2010_NDVI_100m_NA>0,]$QB2010_NDVI_100m_NA, geom="histogram", xlab="Percentage of egocentric NBH that is undefined", ylab="Number of Women", main="100m buffer from 2010 QB (excluding women with no missing pixels)")
ggsave("2010_100m_NAs.png", width=WIDTH, height=HEIGHT, dpi=DPI)
qplot(merged_results[merged_results$QB2010_NDVI_500m_NA>0,]$QB2010_NDVI_500m_NA, geom="histogram", xlab="Percentage of egocentric NBH that is undefined", ylab="Number of Women", main="500m buffer from 2010 QB (excluding women with no missing pixels)")
ggsave("2010_500m_NAs.png", width=WIDTH, height=HEIGHT, dpi=DPI)

qplot(merged_results[merged_results$QB2002_NDVI_100m_NA>0,]$QB2002_NDVI_100m_NA, geom="histogram", xlab="Percentage of egocentric NBH that is undefined", ylab="Number of Women", main="100m buffer from 2002 QB (excluding women with no missing pixels)")
ggsave("2002_100m_NAs.png", width=WIDTH, height=HEIGHT, dpi=DPI)
qplot(merged_results[merged_results$QB2002_NDVI_500m_NA>0,]$QB2002_NDVI_500m_NA, geom="histogram", xlab="Percentage of egocentric NBH that is undefined", ylab="Number of Women", main="500m buffer from 2002 QB (excluding women with no missing pixels)")
ggsave("2002_500m_NAs.png", width=WIDTH, height=HEIGHT, dpi=DPI)
