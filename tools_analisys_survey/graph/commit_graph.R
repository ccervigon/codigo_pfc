#! /usr/bin/Rscript --vanilla

args <- commandArgs(trailingOnly = TRUE)
dir <- args[1]

commits <- read.csv(paste(dir, "output_commits_nobots.csv", sep=''), header = FALSE)

col <- ncol(commits)
added_commits <- colSums(commits)
added_authors <- colSums(commits != 0)

#added_commits

png(paste(dir, "graph_commits.png", sep=''), width=1024, units="px")
plot(added_commits, type="l", ylab="Commits per month", xlab="Months project life",
    main="Evolution of commits per month")
garbage <- dev.off()

#added_authors

png(paste(dir, "graph_active_authors.png", sep=''), width=1024, units="px")
plot(added_authors, type="l", ylab="Authors per month", xlab="Months project life",
    main="Evolution of active authors per month")
garbage <- dev.off()
