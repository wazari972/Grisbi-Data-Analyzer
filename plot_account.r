#!/usr/bin/Rscript

O_WIDTH <- 700
O_HEIGHT <- 500

RANGE_INC <- 5/100

PREFIX <- "graph-Account"
SUFFIX <- "png"

IN_FILE <- "data-Accounts.csv"

args <- commandArgs(trailingOnly = TRUE)

IN_FILE <- args[1]
DIR <- args[2]

fix_range <- function(range) {
    length <- max(range) - min(range) 
    inc <- RANGE_INC*length
    range <- c(min(range) - inc, max(range) + inc)
    }

ofile_name <- function(name) {
        name <- gsub("\\.", "-", name)
        return(paste(DIR, paste(paste(PREFIX, name, sep="-"), SUFFIX, sep="."), sep="/"))
    }

plot_months <- function(dates) {
    dates <- lapply(dates, as.character)
    for (id in 2:size) {
        new_date <- dates[id]
        old_date <- dates[[id-1]]
        if (any(grep("-1$", new_date)) && any(grep("-31$", old_date), grep("-30$", old_date), grep("-29$", old_date), grep("-28$", old_date))) {
            abline(v = id,  col="seagreen4",lty=2) # add vertical line at month break
        }
    }    
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
    plot_months(account$Date)
    #title(paste("Account", name, sep=" - "))
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
if (length(names(account)) != 2)
    do_plot("Total", tot_values)