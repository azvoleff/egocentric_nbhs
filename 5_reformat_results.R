#!/usr/bin/Rscript

# Reads and outputs the coordinates of each WHSA household to both a shapefile 
# and to a csv.

#data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
#data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/20110503_100-to-1000-by-25m/'
data_dir <- 'M:/Data/Ghana/Egocentric_NBH_Data/'

window_size <- 425

# Add back in the household with longitude < .3 (was too far from the rest to 
# be a real datapoint so it was dropped).
load("M:/Data/Ghana/WHSA/whsa_ii_data050510.Rdata")
extra_hh <- whsa2data050510[whsa2data050510$longitude < -.3,]
extra_hh <- data.frame(ROWID=as.numeric(rownames(extra_hh)))

#VIS_2002_filename <- paste(data_dir, 'VIS_', window_size, 'pixels_results.Rdata', sep="")
NDVI_2002_filename <- paste(data_dir, '2002NDVI_', window_size, 'pixels_results.csv', sep="")
NDVI_2010_filename <- paste(data_dir, '2010NDVI_', window_size, 'pixels_results.csv', sep="")

NDVI_2002 <- read.csv(NDVI_2002_filename)
NDVI_2002 <- cbind(NDVI_2002, ROWID=as.numeric(rownames(NDVI_2002)))
NDVI_2010 <- read.csv(NDVI_2010_filename)
NDVI_2010 <- cbind(NDVI_2010, ROWID=as.numeric(rownames(NDVI_2010)))

# First merge the two NDVI datasets - the VIS dataset has NAs for many 
# households as the VIS image does not cover the full extent of the WHSA study 
# area.
# Drop  duplicate columns in NDVI_2010 and VIS_2002:
NDVI_2010 <- NDVI_2010[!(names(NDVI_2010) %in% c("x", "y", "woman_id"))]
#VIS_2002 <- VIS_2002[!(names(VIS_2002) %in% c("x", "y"))]

merged_results <- merge(NDVI_2002, NDVI_2010, by=c("ROWID"), sort=TRUE)
# Increment the ROWIDs in merged_results to account for the missing HH
row_id_gt_extra_hh <- merged_results$ROWID >= extra_hh$ROWID
merged_results$ROWID[row_id_gt_extra_hh] <- merged_results$ROWID[row_id_gt_extra_hh] + 1
#merged_results <- merge(merged_results, VIS_2002, by=c("ROWID", "woman_id"), all.x=TRUE)
merged_results <- merge(merged_results, extra_hh, by=c("ROWID"), all=TRUE)

merged_results_CSV_file <- paste(data_dir, 'merged_buffer_results.csv', sep="")
merged_results_Rdata_file <- paste(data_dir, 'merged_buffer_results.Rdata', sep="")

write.csv(merged_results, merged_results_CSV_file, row.names=F)
save(merged_results, file=merged_results_Rdata_file)
