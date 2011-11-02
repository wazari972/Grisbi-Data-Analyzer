#!/usr/bin/Rscript

O_WIDTH <- 700
O_HEIGHT <- 500

RANGE_INC <- 5/100

PREFIX <- "out/graph-Account"
SUFFIX <- "png"

IN_FILE <- "out/data-Accounts.csv"

fix_range <- function(range) {
    length <- max(range) - min(range) 
    inc <- RANGE_INC*length
    range <- c(min(range) - inc, max(range) + inc)
    }

ofile_name <- function(name) {
        name <- gsub("\\.", "-", name)
        return(paste(paste(PREFIX, name, sep="-"), SUFFIX, sep="."))
    }

account <- read.csv(file=IN_FILE, head=TRUE, sep=";")

if (length(names(account)) == 1)
    account <- read.csv(file=IN_FILE, head=TRUE, sep=",")
    
size <- length(account$Date)

do_plot <- function(name, values) {
    range <- range(values)
    range <- fix_range(range)
    print(ofile_name(name))
    png(ofile_name(name), width=O_WIDTH, height=O_HEIGHT)
    
    plot.new()
    plot.window(xlim=c(0, size), ylim=range, xaxs='i', yaxs='i')
    axis(2)
    lines(seq(1,size), values, col="blue")
    title(paste("Account", name, sep=" - "))
    box()
}

tot_values <- rep(0, size)

for (id in 2:length(names(account))) {
    values <- account[[names(account)[id]]]
    do_plot(names(account)[id], values)
    new_list <- c()
    for (i in 1:size) {
        new_val <- tot_values[[i]] + values[[i]]
        new_list <- c(new_list, new_val)
    }
    tot_values <- new_list
}

do_plot("Total", tot_values)