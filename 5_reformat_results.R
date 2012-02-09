#!/usr/bin/Rscript

# Reads and outputs the coordinates of each WHSA household to both a shapefile 
# and to a csv.

#data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/20110503_100-to-1000-by-25m/'

window_size <- 500

#load("whsa_ii_data050510.Rdata")
#load("R:/Data/Ghana/20101206/whsa_ii_data050510.Rdata")
#load("F:/Data/Ghana/20101206/whsa_ii_data050510.Rdata")
#load("/media/G-Tech_Data/Data/Ghana/20101206/whsa_ii_data050510.Rdata")
#load("/media/Orange_Data/Data/Ghana/20101206/whsa_ii_data050510.Rdata")
load("/home/azvoleff/Data/Ghana/20101206/whsa_ii_data050510.Rdata")

hh <- with(whsa2data050510, data.frame(HHID, x=longitude, y=latitude))
# Bind the rownames so they can be used as unique IDs in the later merge.
hh <- cbind(hh, ROWID=rownames(hh))
# Add back in the household with longitude < .3 (too far from the rest to be a 
# real datapoint).
extra_household <- hh[hh$x < -.3,]
extra_household$x <- NA
extra_household$y <- NA

VIS_2002_filename <- paste(data_dir, 'VIS_', window_size, 'pixels_results.csv', sep="")
NDVI_2002_filename <- paste(data_dir, '2002NDVI_', window_size, 'pixels_results.csv', sep="")
NDVI_2010_filename <- paste(data_dir, '2010NDVI_', window_size, 'pixels_results.csv', sep="")

# Bind the rownames so they can be used as unique IDs in the later merge.
VIS_2002 <- read.csv(VIS_2002_filename)
VIS_2002 <- cbind(VIS_2002, ROWID=rownames(VIS_2002))

NDVI_2002 <- read.csv(NDVI_2002_filename)
NDVI_2002 <- cbind(NDVI_2002, ROWID=rownames(NDVI_2002))

NDVI_2010 <- read.csv(NDVI_2010_filename)
NDVI_2010 <- cbind(NDVI_2010, ROWID=rownames(NDVI_2010))

# First merge the two NDVI datasets - the VIS dataset has NAs for many 
# households as the VIS image does not cover the full extent of the WHSA study 
# area.
merged_results <- merge(NDVI_2002, NDVI_2010)
merged_results <- merge(merged_results, VIS_2002, all.x=TRUE)
merged_results <- merge(merged_results, extra_household, all=TRUE)

# There shouldn't be any NAs (not directly). Whenever nothing is known about a 
# neighborhoods cover type in a particular buffer, the _NA column for that 
# buffer type should be set to 100 (as 100 percent of cover is therefore 
# unknown) and the NAs in ans VIS or veg/nonveg columns should be set to 0, as 
# nothing is known.
unknown_cover_cols <- grep('_NA$', names(merged_results))
unknown_cover_cols_NAs <- is.na(merged_results[unknown_cover_cols])
merged_results[unknown_cover_cols][unknown_cover_cols_NAs] <- 100
# Set any remaining NAs (that are not in the unknown cover cols) to zero
merged_results[is.na(merged_results)] <- 0

merged_results_CSV_file <- paste(data_dir, 'merged_buffer_results.csv', sep="")
merged_results_Rdata_file <- paste(data_dir, 'merged_buffer_results.Rdata', sep="")

write.csv(merged_results, merged_results_CSV_file, row.names=F)
save(merged_results, file=merged_results_Rdata_file)
