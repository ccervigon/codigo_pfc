#!/usr/bin/python
# -*- coding: utf-8 -*- 

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

for project in range(0, len(list_projects)):
    print 'Project: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()

    cursor.execute('SELECT MIN(date) FROM scmlog')
    date_min = cursor.fetchall()[0][0]
    cursor.execute('SELECT MAX(date) FROM scmlog')
    date_max = cursor.fetchall()[0][0]

    period = range(date_min.year,date_max.year)
    period.append(date_max.year)

    query = ('SELECT id from upeople')
    cursor.execute(query)
    upeople = cursor.fetchall()

    authors_commits = []
    authors_ids = []
    for aut in upeople:
        query = ('SELECT people_id FROM people_upeople WHERE upeople_id=%s')
        cursor.execute(query, aut[0])
        people_ids = cursor.fetchall()
        if people_ids:
            list_commits = ()
            for id in people_ids:
                query = ('SELECT committer_id, author_id, author_date FROM scmlog '
                         'WHERE author_id = %s')
                cursor.execute(query, id[0])
                list_commits += cursor.fetchall()
            authors_commits.append(tuple(sorted(list_commits, key=lambda item: item[2])))
            authors_ids.append(people_ids)

    tot_authors = len(authors_commits)

    work_authors = []
    for author in authors_commits:
        M_month = []
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
        work_authors.append(M_month)

    pm_author = []
    for author in work_authors:
        pm_author.append(sum(month > 0 for month in author))

    print 'Total authors: ' + str(tot_authors)
    print 'Total PM: ' + str(np.sum(pm_author))
    print
    print '----------------------------------------------'

    cursor.close()
    con.close()
