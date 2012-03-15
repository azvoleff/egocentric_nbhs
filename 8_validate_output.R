# Uses a set of polygonal buffers around the WHSA2 points to independently 
# verify the neighborhood calculations of the Python code.

require(rgdal)
require(raster)

data_dir <- 'M:/Data/Ghana/Egocentric_NBH_Data/'

# Read the WHSA2 buffer polygon shapefile
buffers <- readOGR("M:/Data/Ghana/WHSA", "whsa2_100m_buffer")
whsa2_pts <- readOGR("D:/Shared_Documents/SDSU/Ghana/AccraABM", "whsa2")

# Accra VIS Imagery
#lulc <- raster("M:/Data/Ghana/Imagery/Accra_VIS/Ghana_VIS_masked_geotiff.tif")
# Accra NDVI images
#lulc <- raster("M:/Data/Ghana/Imagery/Accra_NDVI/cloud_masked_qb02_ndvi_ge120_v02.tif")
lulc <- raster("M:/Data/Ghana/Imagery/Accra_NDVI/cloud_masked_qb10_ndvi_ge120_v02.tif")

lulc_NBHs <- extract(lulc, whsa2_pts, buffer=500)

# Max neighborhood area in number of pixels
NBH_area <- sapply(lulc_NBHs, function(x) length(x))
valid_area <- sapply(lulc_NBHs, function(x) sum(x!=0))
na_area <- sapply(lulc_NBHs, function(x) sum(x==0))
nonveg <- sapply(lulc_NBHs, function(x) sum(x==1))
veg <- sapply(lulc_NBHs, function(x) sum(x==2))

# There is one household without any neighborhood (it is off the image 
# entirely). So code the valid area as zero.
valid_area[is.na(valid_area)] <- 0

valid_area_pct <- (valid_area / NBH_area) * 100
veg_pct <- (veg / valid_area) * 100
nonveg_pct <- (nonveg / valid_area) * 100

NBH_data <- data.frame(cbind(woman_id=whsa2_pts$id, valid_area_pct, veg_pct, nonveg_pct))
write.csv(NBH_data, file="NBH_data_validation.csv")
