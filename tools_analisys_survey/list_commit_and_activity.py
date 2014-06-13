#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
from datetime import *
import numpy as np
import csv
import sys

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

if len(sys.argv) < 2:
    sys.exit('Usage: python list_commit_and_activity.py db_project [dir_to_save]')
    
dir_to_save = '/tmp/'
if len(sys.argv) == 3:
    dir_to_save = sys.argv[2]
db_project = sys.argv[1]
print 'Dir to save:', dir_to_save

con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                      db=db_project)
cursor = con.cursor()

cursor.execute('SELECT MIN(date) FROM scmlog')
date_min = cursor.fetchall()[0][0]
cursor.execute('SELECT MAX(date) FROM scmlog')
date_max = cursor.fetchall()[0][0]

print 'Date first commit:', date_min
print 'Date last commit:', date_max

period = range(date_min.year,date_max.year)
period.append(date_max.year)

#Upeople
date_limit = datetime(date_max.year-1, date_max.month, 1)
query = ('SELECT upeople_id FROM people_upeople WHERE people_id = ANY (SELECT DISTINCT author_id FROM scmlog WHERE date >= %s)')
cursor.execute(query, date_limit)
upeople = cursor.fetchall()

#Bots
query = ('SELECT upeople_id FROM people_upeople WHERE people_id = ANY (SELECT id FROM people WHERE name LIKE "%bot" OR name LIKE "%jenkins%" OR name LIKE "%gerrit%")')
cursor.execute(query)
bots = cursor.fetchall()

authors_commits = []
authors_ids = []
for aut in upeople:
    if not aut in bots:
        query = ('SELECT people_id FROM people_upeople WHERE upeople_id=%s')
        cursor.execute(query, aut[0])
        people_ids = cursor.fetchall()
        if people_ids:
            list_commits = ()
            for id in people_ids:
                query = ('SELECT committer_id, author_id, date FROM scmlog '
                         'WHERE author_id = %s')
                cursor.execute(query, id[0])
                list_commits += cursor.fetchall()
            authors_commits.append(tuple(sorted(list_commits, key=lambda item: item[2])))
            ids = (aut,) + people_ids
            authors_ids.append(ids)

tot_authors = len(authors_commits)

activity_author = []
commits_author = []
for author in authors_commits:
    M_month = []
    N_month = []
    for year in period:
        first_month = 1
        last_month = 12
        if year == date_min.year:
            first_month = date_min.month
            last_month = 12
        elif year == date_max.year:
            first_month = 1
            last_month = date_max.month
        for month in range(first_month, last_month+1):
            aut = calendar_commit_month_author(year, month, author)
            work_days = 0
            for i in range(len(aut)):
                if aut[i] != 0:
                    work_days += 1
            M_month.append(work_days)
            N_month.append(np.sum(aut))
    activity_author.append(M_month)
    commits_author.append(N_month)

add_act = []
for author in commits_author:
    add_act.append(np.sum(author[-6:]))

print 'Total authors:', len(add_act)
aut_act = 0
for aut in add_act:
    if aut != 0:
        aut_act+=1
print 'Active authors in the last 6 months:', aut_act

with open(dir_to_save + "output_authors_ids_nobots.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['#upeople_id', 'people_ids'])
    writer.writerows(authors_ids)
with open(dir_to_save + "output_activity_nobots.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(activity_author)
with open(dir_to_save + "output_commits_nobots.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(commits_author)

cursor.close()
con.close()
