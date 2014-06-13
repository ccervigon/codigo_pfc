#!/usr/bin/python

import MySQLdb
from datetime import *
import numpy as np

def calc_num_authors(percent, list, tot_list):
    flag = False
    i = 0
    sum_dat = 0
    while not flag:
        sum_dat += list[i]
        i += 1
        if sum_dat >= tot_list*percent:
            flag = True
    return i

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

list_PM = []

for project in range(0, len(list_projects)):
    print 'Project: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM people')
    tot_authors = int(cursor.fetchall()[0][0])
    cursor.execute('SELECT COUNT(*) FROM scmlog')
    tot_commits = int(cursor.fetchall()[0][0])

    authors = []
    for i in range(1,tot_authors+1):
        query = ('SELECT committer_id, author_id, author_date FROM scmlog '
                  'WHERE author_id = %s ORDER BY author_date')
        cursor.execute(query, i)
        authors.append(cursor.fetchall())
    
    list_commits_author = []
    author = 1
    while author <= tot_authors:
        query = ('SELECT COUNT(*) from scmlog where author_id = %s')
        cursor.execute(query, author)
        list_commits_author.append(int(cursor.fetchall()[0][0]))
        author += 1

    list_commits_sorted = list(reversed(sorted(list_commits_author)))
    com90 = calc_num_authors(0.9, list_commits_sorted, tot_commits)

    PM = com90 * 1.11
    list_PM.append("{0:.2f}".format(PM))

    print 'Total authors: ' + str(tot_authors)
    print 'PM project:', PM
    print 'Professional authors:'
    print com90
    print
    print '----------------------------------------------'

    cursor.close()
    con.close()
