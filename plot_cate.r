#!/usr/bin/Rscript

O_WIDTH <- 700
O_HEIGHT <- 500

RANGE_INC <- 5/100

PREFIX <- "out/graph-Category"
SUFFIX <- "png"

IN_FILE <- "out/data-Accounts.csv"

args <- commandArgs(trailingOnly = TRUE)

fix_range <- function(range) {
    length <- max(range) - min(range) 
    inc <- RANGE_INC*length
    range <- c(min(range) - inc, max(range) + inc)
    }

FILE <- args[1]
FILENAME <- lapply(strsplit(FILE, "\\."), function(x) x[1])
CATE_NAME <- lapply(strsplit(FILENAME[[1]], "-"), function(x) x[3])

ofile_name <- function(name) {
    name <- gsub("\\.", "-", name)
    return(paste(paste(PREFIX, name, sep="-"), SUFFIX, sep="."))
}
ofile_name(CATE_NAME)
png(ofile_name(CATE_NAME), width=O_WIDTH, height=O_HEIGHT)

category <- read.csv(file=FILE, head=TRUE, sep=";")

if (length(names(category)) == 1)
    category <- read.csv(file=FILE, head=TRUE, sep=",")
    
size <- length(category$Date)

lists <- list(category[[2]])
i <- 1
names <- names(category)[[2]]
if (length(names(category)) > 2) {
    for (id in 3:length(names(category))) {
        new_list <- c()
        for (j in 1:size) {
            new_val <- category[[names(category)[id]]][[j]] + lists[[i]][[j]]
            new_list <- c(new_list, new_val)
        }
        lists <- c(lists, list(new_list))
        i <- i + 1
        names <- c(names, names(category)[id])
    }
}
rng <- range(category[[2]])
for (id in length(lists))
    rng <- range(min(rng), max(rng), lists[[id]])
rng <- fix_range(rng)

plot.new()
plot.window(xlim=c(0, size), ylim=rng, xaxs='i', yaxs='i')
axis(2)
rain <- rainbow(length(names(category)), start=.7, end=.1)

for (id in 1:length(lists)) {
    lines(seq(1,size), lists[[id]], col=rain[id])
    
}

title(paste("Category", CATE_NAME, sep=" - "))
legend("bottom", legend=names, fill=rain)

box()
