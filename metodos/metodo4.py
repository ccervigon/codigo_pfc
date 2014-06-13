#!/usr/bin/python

import MySQLdb
from datetime import *
import numpy as np

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
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

    PM = []
    prof_in_month = []
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
    
    for i in work_authors:
        min_dw = 15
        last_dw = None
        aut_act = 0
        if np.sum(i) != 0:
            j = sorted(i, reverse=True)
            for a in j:
                if a >= min_dw:
                    last_dw = j.index(a)
                if a != 0:
                    aut_act += 1
            if last_dw != None:
                prof_in_month.append(last_dw+1)
                top_val = float(j[last_dw+1])/j[last_dw]
                if top_val != 0:
                    paso = float(top_val) / (aut_act-last_dw)
                else:
                    paso = 0
            else:
                prof_in_month.append(0)
                top_val = float(j[0])/15
                paso = float(top_val) / aut_act
            if paso != 0:
                list_weight = list(np.arange(0, top_val, paso))
            else:
                list_weight = np.zeros(tot_authors)
            if list_weight[-1] > top_val:
                list_weight.pop()
            if last_dw != None:
                aux = []
                for i in range(last_dw+1):
                    aux.append(1)
                list_weight = list(reversed(list(list_weight) + aux))
            PM.append(np.sum(list_weight))

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
