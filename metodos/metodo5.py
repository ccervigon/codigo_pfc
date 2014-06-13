#!/usr/bin/python

import MySQLdb
from datetime import *
import numpy as np

#Creador de una matriz vacia
def Matrix_empty(rows, columns):
    A = []
    for i in range(0,rows):
        A.append([0]*columns)
    return A

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

def commits_months(period, authors):
    M = Matrix_empty(13, len(period))
    M[0] = period
    for author in authors:
        for aux in author:
            M[int(aux[2].month)][int(aux[2].year-date_min)] += 1
    return M

list_projects = []
list_projects.append('vizgrimoire_vizgrimoirer_cvsanaly')
list_projects.append('openstack_tempest_cvsanaly')
list_projects.append('twbs_bootstrap_cvsanaly')
#GNOME
list_projects.append('gnome_easytag_cvsanaly')
list_projects.append('gnome_gnoduino_cvsanaly')
list_projects.append('gnome_libgee_cvsanaly')
list_projects.append('gnome_chronojump_cvsanaly')
list_projects.append('gnome_gnome_calendar_cvsanaly')
list_projects.append('gnome_libgweather_cvsanaly')
list_projects.append('gnome_kupfer_cvsanaly')
list_projects.append('gnome_gedit_cvsanaly')
list_projects.append('gnome_tracker_cvsanaly')
list_projects.append('gnome_gnome_packagekit_cvsanaly')

list_projects_authors_classif = []
list_PM = []

for project in range(0, len(list_projects)):
    print 'Project: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM people')
    tot_authors = int(cursor.fetchall()[0][0])

    cursor.execute('SELECT MIN(date) FROM scmlog')
    date_min = cursor.fetchall()[0][0]
    date_min = date_min.year
    cursor.execute('SELECT MAX(date) FROM scmlog')
    date_max = cursor.fetchall()[0][0]
    date_max = date_max.year
    
    period = range(date_min,date_max)
    period.append(date_max)
    
    authors = []
    for i in range(1,tot_authors+1):
        query = ('SELECT committer_id, author_id, author_date FROM scmlog '
                  'WHERE author_id = %s ORDER BY author_date')
        cursor.execute(query, i)
        authors.append(cursor.fetchall())

    work_authors = []
    for year in period:
        for month in range(1, 13):
            M = []
            for author in authors:
                aut = calendar_commit_month_author(year, month, author)
                work_days = 0
                for i in range(0, len(aut)):
                    if aut[i] != 0:
                        work_days += 1
                M.append(work_days)
            work_authors.append(M)

    com_auts = commits_months(period, authors)

    i = 0
    y = 0
    PM = []
    prof_in_month = []
    for month in work_authors:
        prof_authors = 0
        min_dw = 15
        sum_com = 0
        m = (i % 12)
        if m == 0:
            y += 1
        #print '[Year, Month]', y, m
        j = 0
        for author in month:
            if author >= min_dw:
                prof_authors += 1
                sum_com += np.sum(calendar_commit_month_author(date_min+y-1, m+1, authors[j]))
            j += 1
        if com_auts[m+1][y-1] != 0:
            percent_com_prof = float(sum_com) / com_auts[m+1][y-1]
        else:
            percent_com_prof = 0
        if percent_com_prof != 0:
            PM.append(prof_authors*(1 + (1 - percent_com_prof)))
        elif com_auts[m+1][y-1] != 0:
            PM.append(1)
        else:
            PM.append(0)
        i += 1
        prof_in_month.append(prof_authors)
        #print '[Prof, Percent, Sum, Com_aut, PM]', prof_authors, percent_com_prof, sum_com, com_auts[m+1][y-1], PM[-1]

    list_PM.append("{0:.2f}".format(np.sum(PM)))

    print 'Total authors: ' + str(tot_authors)
    print 'PM project:', np.sum(PM)
    print 'Professional authors[per month]:'
    print prof_in_month
    print 'Added professional:'
    print np.sum(prof_in_month)
    print
    print '----------------------------------------------'
    
    cursor.close()
    con.close()
