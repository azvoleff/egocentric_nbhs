#!/usr/bin/Rscript

# Reads and outputs the coordinates of each WHSA household to both a shapefile 
# and to a csv.

require("ggplot2")
require("rgdal")
theme_update(theme_grey(base_size=18))
update_geom_defaults("point", aes(size=.8))
DPI <- 300
WIDTH <- 8.33
HEIGHT <- 5.53

#data_dir <- '/home/azvoleff/Data/Ghana/Egocentric_NBH_Data/'
data_dir <- 'N:/Data/Ghana/Egocentric_NBH_Data'

#load("whsa_ii_data050510.Rdata")
load("N:/Data/Ghana/WHSA/whsa_ii_data050510.Rdata")
#load("/media/G-Tech_Data/Data/Ghana/20101206/whsa_ii_data050510.Rdata")

hh <- with(whsa2data050510, data.frame(woman_id, x=longitude, y=latitude))
# Throw out household with longitude < .3 (too far from the rest to be a real 
# datapoint).
hh <- hh[!(hh$x < -.3),]

coordinates(hh) <- c("x", "y")
proj4string(hh) <- CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
#hh.utm <- spTransform(hh, CRS("+proj=utm +zone=30 +ellps=WGS84 +units=m +no_defs"))
hh.utm <- spTransform(hh, CRS("+init=epsg:32630"))
writeOGR(hh.utm, data_dir, "WHSA_hh_UTM30", "ESRI Shapefile", overwrite_layer=TRUE)

hh.utm <- as.data.frame(hh.utm)
qplot(hh.utm$x, hh.utm$y, xlab="Easting", ylab="Northing", main="WHSA HH in UTM30")
hh_plot_filename <- paste(data_dir, "/WHSA_hh_UTM30.png", sep="")
ggsave(hh_plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)

hh_csv_filename <- paste(data_dir, "/WHSA_hh_UTM30.csv", sep="")
hh.utm$woman_id <- as.character(hh.utm$woman_id)
write.csv(hh.utm, hh_csv_filename, row.names=F)
