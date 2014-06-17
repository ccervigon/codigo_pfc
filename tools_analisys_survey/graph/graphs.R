#! /usr/bin/Rscript --vanilla

args <- commandArgs(trailingOnly = TRUE)
dir <- args[1]

statistics <- read.csv(paste(dir, "statistics.csv", sep=''), header = TRUE)

#GRAPH OF STATISTICS
png(paste(dir, "graph_statistics.png", sep=''), width=1024, units="px")
plot(statistics$precision, type="b", ylim=c(0,1),
     axes=T, ann=T, xlab="Threshold", ylab="", cex.lab=0.8, lwd=1.2, pch=17)
box()
lines(statistics$recall, type="b", lty=2, lwd=2, pch=18)
lines(statistics$fmeasure, type="b", lty=3, lwd=2, pch=19)
lines(statistics$accuracy, type="b", lty=4, lwd=2, pch=25)
lines(statistics$goodnes, type="b", lty=5, lwd=2, pch=21)
legend("bottomleft", names(statistics[c(-1,-2,-3,-4,-5)]), cex=1.3, 
   lty=1:5, lwd=2, pch=c(17,18,19,25,21), bty="nb")
title(main="Relevance of results (for many threshold values)")
garbage <- dev.off()

#STATISTICS WITH ZOOM
png(paste(dir, "graph_statistics_zoom.png", sep=''), width=1024, units="px")
plot(statistics$precision, type="b", ylim=c(0.4,1),
     axes=T, ann=T, xlab="Threshold", ylab="", cex.lab=0.8, lwd=1.2, pch=17,
     xlim=c(5,20))
box()
lines(statistics$recall, type="b", lty=2, lwd=2, pch=18)
lines(statistics$fmeasure, type="b", lty=3, lwd=2, pch=19)
lines(statistics$accuracy, type="b", lty=4, lwd=2, pch=25)
lines(statistics$goodnes, type="b", lty=5, lwd=2, pch=21)
legend("bottomleft", names(statistics[c(-1,-2,-3,-4,-5)]), cex=1.3, 
   lty=1:5, lwd=2, pch=c(17,18,19,25,21), bty="nb")
title(main="Relevance of results (for many threshold values)")
garbage <- dev.off()

#GRAPHS OF TP, FN, TN, FP
png(paste(dir, "graph_tp_fn.png", sep=''), width=1024, units="px")
barplot(t(statistics[c(2,3)]), main="Number of correctly identifier full-time developers with threshold", ylab="Full-time Developers", xlab="Threshold (in commits/semester)",
          space=0.3, cex.axis=0.8, las=1, cex=0.8,
          names.arg=statistics$threshold, legend=rownames(t(statistics[c(2,3)]))) 
garbage <- dev.off()

png(paste(dir, "graph_tn_fp.png", sep=''), width=1024, units="px")
barplot(t(statistics[c(4,5)]), main="Number of correctly identifier non-full-time developers with threshold", ylab="Non-full-time Developers", xlab="Threshold (in commits/semester)",
          space=0.3, cex.axis=0.8, las=1, cex=0.8,
          names.arg=statistics$threshold, legend=rownames(t(statistics[c(4,5)]))) 
garbage <- dev.off()

#NORMALIZED GRAPHS
ntp <- function(x,y) {x/y}
ntn <- function(x,y) {x/y}
normed <- statistics
tot_prof <- normed[1,2] + normed[1,3]
tot_non_prof <- normed[1,4] + normed[1,5]
normed$tp <- lapply(normed$tp, ntp, y=tot_prof)
normed$fn <- lapply(normed$fn, ntp, y=tot_prof)
normed$tn <- lapply(normed$tn, ntn, y=tot_non_prof)
normed$fp <- lapply(normed$fp, ntn, y=tot_non_prof)

png(paste(dir, "graph_tp_fn_norm.png", sep=''), width=1024, units="px")
barplot(t(normed[c(2,3)]), main="Number of correctly identifier full-time developers with threshold (normalized)", ylab="Full-time Developers", xlab="Threshold (in commits/semester)",
          ylim=c(0,1),space=0.3, cex.axis=0.8, las=1, cex=0.8,
          names.arg=statistics$threshold, legend=rownames(t(statistics[c(2,3)]))) 
garbage <- dev.off()

png(paste(dir, "graph_tn_fp_norm.png", sep=''), width=1024, units="px")
barplot(t(normed[c(4,5)]), main="Number of correctly identifier non-full-time developers with threshold (normalized)", ylab="Non-full-time Developers", xlab="Threshold (in commits/semester)",
          ylim=c(0,1),space=0.3, cex.axis=0.8, las=1, cex=0.8,
          names.arg=statistics$threshold, legend=rownames(t(statistics[c(4,5)]))) 
garbage <- dev.off()


#COMPENSATION FN AND FP
png(paste(dir, "comp_fn_fp.png", sep=''), width=1024, units="px")
compensed <- statistics$fn - statistics$fp
barplot(compensed, main="Compensacion FN y FP", xlab="Threshold",
        names.arg=statistics$threshold, ylim=c(-60,60), space=0.3)
garbage <- dev.off()
