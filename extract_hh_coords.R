#!/usr/bin/Rscript

require("ggplot2")
require("rgdal")
theme_update(theme_grey(base_size=18))
update_geom_defaults("point", aes(size=.8))
DPI <- 300
WIDTH <- 8.33
HEIGHT <- 5.53

#load("whsa_ii_data050510.Rdata")
#load("R:/Data/Ghana/20101206/whsa_ii_data050510.Rdata")
load("F:/Data/Ghana/20101206/whsa_ii_data050510.Rdata")

hh <- with(whsa2data050510, data.frame(HHID, x=longitude, y=latitude))
# Throw out household with longitude < .3 (too far from the rest to be a real 
# datapoint).
hh <- hh[!(hh$x < -.3),]

coordinates(hh) <- c("x", "y")
proj4string(hh) <- CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
#hh.utm <- spTransform(hh, CRS("+proj=utm +zone=30 +ellps=WGS84 +units=m +no_defs"))
hh.utm <- spTransform(hh, CRS("+init=epsg:32630"))

writeOGR(hh.utm, "WHSA_hh_UTM30.shp", "WHSA_hh", "ESRI Shapefile")

hh.utm <- as.data.frame(hh.utm)
qplot(hh.utm$x, hh.utm$y, xlab="Easting", ylab="Northing", main="WHSA HH in UTM30")
ggsave("household_positions.png", width=WIDTH, height=HEIGHT, dpi=DPI)
write.csv(hh.utm, file="WHSA_hh_UTM30.csv", row.names=F)
