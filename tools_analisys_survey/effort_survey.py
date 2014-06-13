#!/usr/bin/python
# -*- coding: utf-8 -*- 

import sys
import sqlite3
import csv

dir_to_save = '/tmp/'
if len(sys.argv) == 3:
    dir_to_save = sys.argv[2]
print 'Dir to save:', dir_to_save

con = sqlite3.connect(sys.argv[1])
con.text_factory = lambda x: unicode(x, "utf-8", "ignore")
cursor = con.cursor()

effort_author = []
query = ('SELECT upeople_id,resp1,resp2,resp4 from surveyApp_survey_author')
for aut in cursor.execute(query):
    hours = 0
    percent = 0
    if aut[1] == 'None':
        hours = 0
    else:
        hours = int(aut[1])
    if aut[2] == 'None':
        percent = 0
    else:
        percent = float(aut[2])/100
    if aut[3] == 'full':
        hours = 40
    effort_author.append([aut[0], str(hours*percent).replace('.', ',')])

with open(dir_to_save + "effort_survey_authors.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['Upeople_id', 'Effort done by author'])
    for i in range(len(effort_author)):
        writer.writerow(effort_author[i])

cursor.close()
con.close()
