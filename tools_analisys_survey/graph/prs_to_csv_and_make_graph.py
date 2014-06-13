#!/usr/bin/python
# -*- coding: utf-8 -*- 

import csv
from subprocess import call
import sys

threshold = []
precision = []
recall = []
fmeasure = []
accuracy = []
goodness = []

if len(sys.argv) < 2:
    sys.exit('Usage: python prs_to_csv_and_make_graph.py PROJECT_DIR')
project_dir = sys.argv[1]

file = open(project_dir + 'results_prs.txt')
with open(project_dir + "statistics.csv", "wb") as f:
    writer = csv.writer(f)
    i = 0
    for line in file:
        data = line.split()
        if i == 0:
            writer.writerow([data[1][:-1], data[2][1:-1], data[3][:-1], data[4][:-1], data[5][:-2], data[6][:-1], data[7][:-1], data[8][:-1], data[9][:-1], data[10]])
        else:
            writer.writerow([data[0], data[1][1:-1], data[2][:-1], data[3][:-1], data[4][:-1], data[5], data[6], data[7], data[8], data[9]])
        i += 1

call(['Rscript', 'graphs.R', project_dir])
