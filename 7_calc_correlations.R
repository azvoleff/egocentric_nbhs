#!/usr/bin/Rscript

# Makes correlation of a WHSA variable with a neighborhood-level measure 
# calculated over a range of different neighborhood buffer sizes.

require(plotrix)
require(ggplot2)
require(gridExtra)
require(reshape) # for melt
require(pspearman)

DPI <- 300
WIDTH <- 9
HEIGHT <- 5.67
theme_update(theme_bw(base_size=16))
#update_geom_defaults("line", aes(size=1))

# Variables to analyze with correlation analysis
#cor_variable_names <- c("BP_diastolic", "BP_systolic", "wealth_quintile", "W401_AMOUNT_OF_PAIN")
#cor_method_names <- c("pearson", "pearson", "spearman", "spearman")
cor_variable_names <- c("w203_own_health", "rand_sf36_pf", "rand_sf36_ew", "rand_sf36_gh")
cor_method_names <- c("spearman", "pearson", "pearson", "pearson")

# Variables to analyze with bivariate logistic regression
#logit_variable_names <- c("W1321A_MALARIA")
logit_variable_names <- c()

#load("D:/Shared_Documents/SDSU/Ghana/AccraABM/whsa1_whsa2linked.Rdata")
#whsa1 <- as.data.frame(whsa1_whsa2linked)
load("D:/Shared_Documents/SDSU/Ghana/AccraABM/whsa2_spdf_FMV_ego.Rdata")
whsa2 <- as.data.frame(whsa2_spdf_FMV_ego)

data_dir <- 'R:/Data/Ghana/Egocentric_NBH_Data/20120315_25_to_1000m/'
min_radius <- 25
max_radius <- 1000
dradius <- 25
radii <- seq(min_radius, max_radius, dradius)

base_class <- 'VEG'
other_classes <- c(base_class, 'NONVEG')
#col_prefix <- 'QB2002_NDVI_'
col_prefix <- 'QB2010_NDVI_'


load(paste(data_dir, 'merged_buffer_results_20120315.Rdata', sep=""))

# First do the easy ones - correlation analysis
for (n in 1:length(cor_variable_names)) {
    variable_name <- cor_variable_names[n]
    method_name <- cor_method_names[n]
    variable_col <- grep(variable_name, names(whsa2))
    whsa_var <- whsa2[,variable_col]
    # Save summary info to textfile
    summary_filename <- paste(data_dir, col_prefix, 'summary_', variable_name,
            '.csv', sep="")
    if (method_name == "spearman") {
        write.csv(table(whsa_var, useNA="always"), row.names=FALSE, file=summary_filename)
    }
    else if (method_name == "pearson") {
        write.csv(as.matrix(summary(whsa_var)), file=summary_filename)
    }
    correlations <- c()
    correlations_pvalues <- c()
    for (radius in radii) {
        base_class_col <- paste(col_prefix, radius, 'm_', base_class, sep='')
        col_names <- paste(col_prefix, radius, 'm_', other_classes, sep='')
        col_nums <- c()
        for (col_name in col_names) {
            col_nums <- c(col_nums,  grep(col_name, names(merged_results)))
        }
        # Calculate a new percentage for the base_class col that ignores all 
        # columns not listed in the other_classes vector.
        nbh_var <- (merged_results[,base_class_col] / rowSums(merged_results[col_nums], na.rm=TRUE))*100
        correlation_test <- cor.test(whsa_var, nbh_var, method=method_name,
                na.action=na.rm, exact=TRUE)
        correlations <- c(correlations, correlation_test$estimate)
        correlations_pvalues <- c(correlations_pvalues, correlation_test$p.value)
    }
    plot_title <- paste("Correlation of '", variable_name, "' with ",
            col_prefix, base_class, sep="")
    corr_plot <- ggplot(data.frame(radii, correlations),aes(x=radii,y=correlations)) + 
            geom_line() + labs(x = 'Radius (m)',y='Correlation (r)')
    signif_plot <- ggplot(data.frame(radii, correlations_pvalues),aes(x=radii,y=correlations_pvalues)) + 
            geom_line() + labs(x = 'Radius (m)',y='Signif. (p)')
    plot_filename <- paste(data_dir, col_prefix, 'corplot_', variable_name,
            '_combined.png', sep="")
    png(plot_filename, width=900, height=600)
    grid.arrange(corr_plot, signif_plot)
    dev.off()
    plot_filename <- paste(data_dir, col_prefix, 'corplot_', variable_name,
            '_combined.svg', sep="")
    svg(plot_filename, width=9, height=6)
    grid.arrange(corr_plot, signif_plot)
    dev.off()
}

###############################################################################
# Now do logistic regression for dichotomous variables
odds_ratios <- function(logistic.model, filename=FALSE) {
    coeffs <- data.frame(summary(logistic.model)$coefficients)
    # Get column 1 twice so that I can have both the coefficients and the odds 
    # ratios in the final output.
    odds <- coeffs[c(0, 1, 1, 4)]
    Signif.Symbol <- factor(rep(" ", nrow(odds)),
            levels=c(" ", ".", "*", "**", "***"))
    odds <- cbind(odds, Signif.Symbol)
    names(odds) <- c("Coefficient", "Odds.Ratio", "P.Value", "Signif.Symbol")
    odds$Odds.Ratio <- exp(odds$Odds.Ratio)
    odds$Signif.Symbol[odds$P.Value <= .1 & odds$P.Value > .05] <- "."
    odds$Signif.Symbol[odds$P.Value <= .05 & odds$P.Value > .01] <- "*"
    odds$Signif.Symbol[odds$P.Value <= .01 & odds$P.Value > .001] <- "**"
    odds$Signif.Symbol[odds$P.Value <= .001] <- "***"
    if (filename!=FALSE) {
        odds[c(1:2)] <- round(odds[,c(1:2)], digits=2)
        odds$P.Value <- round(odds$P.Value, digits=3)
        write.csv(odds, file=filename)
    }
    else return(odds)
}

for (n in 1:length(logit_variable_names)) {
    variable_name <- logit_variable_names[n]
    variable_col <- grep(variable_name, names(whsa2))
    whsa_var <- whsa2[,variable_col]
    summary_filename <- paste(data_dir, col_prefix, 'summary_', variable_name,
            '.csv', sep="")
    write.csv(table(whsa_var, useNA="always"), row.names=FALSE, file=summary_filename)
    odds_ratios_estimates <- c()
    odds_ratios_pvalues <- c()
    for (radius in radii) {
        base_class_col <- paste(col_prefix, radius, 'm_', base_class, sep='')
        col_names <- paste(col_prefix, radius, 'm_', other_classes, sep='')
        col_nums <- c()
        for (col_name in col_names) {
            col_nums <- c(col_nums,  grep(col_name, names(merged_results)))
        }
        # Calculate a new percentage for the base_class col that ignores all 
        # columns not listed in the other_classes vector.
        nbh_var <- (merged_results[,base_class_col] / rowSums(merged_results[col_nums], na.rm=TRUE))*100
        whsa_var <- as.factor(whsa_var)
        glm_model <- glm(whsa_var ~ nbh_var, family=binomial("logit"))
        odds_ratios_object <- odds_ratios(glm_model)

        # Note that we want the second element as the first is an intercept.
        odds_ratios_estimates <- c(odds_ratios_estimates, odds_ratios_object$Odds.Ratio[2])
        odds_ratios_pvalues <- c(odds_ratios_pvalues, odds_ratios_object$P.Value[2])
    }

    plot_title <- paste("Odds Ratios: '", variable_name, "' Regressed on ",
            col_prefix, base_class, sep="")
    qplot(radii, odds_ratios_estimates, geom="line", main=plot_title,
          xlab="Buffer Radius (meters)", ylab="Odds Ratio")
    plot_filename=paste(data_dir, col_prefix, 'logitplot_', variable_name,
            '.png', sep="")
    ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)

    plot_title <- paste("P-value for Odds Ratios of '", variable_name,
            "' Regressed on ", col_prefix, base_class, sep="")
    qplot(radii, odds_ratios_pvalues, geom="line", main=plot_title,
            xlab="Buffer Radius (meters)", ylab="p-value")
    plot_filename=paste(data_dir, col_prefix, 'logitplot_', variable_name,
            '_p-values.png', sep="")
    ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)
}

###############################################################################
# Now plot vegetation percentage summary stats
# First do the easy ones - correlation analysis
means <- c()
variances <- c()
maxs <- c()
mins <- c()
missings <- c()
for (radius in radii) {
    base_class_col <- paste(col_prefix, radius, 'm_', base_class, sep='')
    col_names <- paste(col_prefix, radius, 'm_', other_classes, sep='')
    col_nums <- c()
    for (col_name in col_names) {
        col_nums <- c(col_nums,  grep(col_name, names(merged_results)))
    }
    # Calculate a new percentage for the base_class col that ignores all 
    # columns not listed in the other_classes vector.
    nbh_var <- (merged_results[,base_class_col] / rowSums(merged_results[col_nums], na.rm=TRUE))*100
    means <- c(means, mean(nbh_var, na.rm=TRUE))
    variances <- c(variances, var(nbh_var, na.rm=TRUE))
    maxs <- c(maxs, max(nbh_var, na.rm=TRUE))
    mins <- c(mins, min(nbh_var, na.rm=TRUE))
    missings <- c(missings, sum(is.na(nbh_var)))
}

plot_title <- paste("Mean of ", col_prefix, base_class, sep="")
qplot(radii, means, geom="line", main=plot_title,
      xlab="Buffer Radius (meters)", ylab="Mean")
plot_filename <- paste(data_dir, col_prefix, base_class, '_means',
        '.png', sep="")
ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)

plot_title <- paste("Variances of ", col_prefix, base_class, sep="")
qplot(radii, variances, geom="line", main=plot_title,
      xlab="Buffer Radius (meters)", ylab="Variance")
plot_filename <- paste(data_dir, col_prefix, base_class, '_variances',
        '.png', sep="")
ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)

plot_title <- paste("Max of ", col_prefix, base_class, sep="")
qplot(radii, maxs, geom="line", main=plot_title,
      xlab="Buffer Radius (meters)", ylab="Maximum")
plot_filename <- paste(data_dir, col_prefix, base_class, '_maxs',
        '.png', sep="")
ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)

plot_title <- paste("Min of ", col_prefix, base_class, sep="")
qplot(radii, mins, geom="line", main=plot_title,
      xlab="Buffer Radius (meters)", ylab="Minimum")
plot_filename <- paste(data_dir, col_prefix, base_class, '_mins',
        '.png', sep="")
ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)

plot_title <- paste("Missings of ", col_prefix, base_class, sep="")
qplot(radii, missings, geom="line", main=plot_title,
      xlab="Buffer Radius (meters)", ylab="Number of NAs")
plot_filename <- paste(data_dir, col_prefix, base_class, '_missings',
        '.png', sep="")
ggsave(filename=plot_filename, width=WIDTH, height=HEIGHT, dpi=DPI)
