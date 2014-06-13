#!/usr/bin/python
# -*- coding: utf-8 -*- 

"""
Description: Analisis de los autores de openstack para detectar patrones de clasificacion en profesionales
"""

import MySQLdb
from datetime import *
import numpy as np

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                      db='openstack_authors')
cursor = con.cursor()

cursor.execute('SELECT MIN(date) FROM scmlog')
date_min = cursor.fetchall()[0][0]
date_min = date_min.year
cursor.execute('SELECT MAX(date) FROM scmlog')
date_max = cursor.fetchall()[0][0]
date_max = date_max.year

period = range(date_min,date_max)
period.append(date_max)

cursor.execute('SELECT * FROM companies')
list_companies = cursor.fetchall()
tot_companies = len(list_companies)

companies = np.zeros([tot_companies, 2], dtype='a16')
for comp in range(0, tot_companies):
    companies[comp][0] = list_companies[comp][1]

cursor.execute('SELECT company_id FROM upeople_companies WHERE upeople_id = ANY (SELECT upeople_id FROM people_upeople)')
upeople_company = cursor.fetchall()

for people in upeople_company:
    if companies[people[0]-1][1] != '':
        companies[people[0]-1][1] = str(int(companies[people[0]-1][1]) + 1)
    else:
        companies[people[0]-1][1] = 1

query = ('SELECT people_id FROM people_upeople WHERE upeople_id = ANY '
         '(SELECT upeople_id FROM upeople_companies)')
cursor.execute(query)
authors_id = cursor.fetchall()
tot_authors = len(authors_id)

authors = []
for i in range(0,tot_authors):
    query = ('SELECT committer_id, author_id, date FROM scmlog '
              'WHERE author_id = %s ORDER BY date')
    cursor.execute(query, authors_id[i][0])
    authors.append(cursor.fetchall())

print len(authors)
work_authors = []
a = 0
for author in authors:
    M = []
    a += 1
    print a
    file = open('info_openstack/' + str(a), 'w')
    for year in period:
        for month in range(1, 13):
            aut = calendar_commit_month_author(year, month, author)
            file.write(str(aut))
            file.write('\n')
            work_days = 0
            for i in range(0, len(aut)):
                if aut[i] != 0:
                    work_days += 1
            M.append(work_days)
    work_authors.append(M)
    file.close()

aux = 0
aux_sum = 0
for i in range(0, len(work_authors)):
    j = np.sum(work_authors[i])
    if j > aux_sum:
        aux = i
        aux_sum = j

print work_authors[aux]

cursor.close()
con.close()