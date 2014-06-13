#!/usr/bin/python

import MySQLdb
from datetime import *

len_pro = 13 #12 months + 1 to the year
len_semi = 54 #53 weaks + 1 to the year
len_amat = (365/3)+2 #365/3 slots of 3 days + 1 to the year

#Creador de una matriz vacia
def Matrix_empty(rows, columns):
    A = []
    for i in range(0,rows):
        A.append([0]*columns)
    return A

def Author_prof(period, author):
    M = Matrix_empty(len_pro, len(period))
    M[0] = period
    for aux in author:
        M[int(aux[2].month)][int(aux[2].year-date_min)] += 1
    return M

def Author_semi(period, author):
    W = Matrix_empty(len_semi, len(period))
    W[0] = period
    for aux in author:
        day = aux[2].toordinal() - date(aux[2].year, 1, 1).toordinal() + 1
        week = ((day - 1) / 7) + 1
        W[int(week)][int(aux[2].year-date_min)] += 1
    return W

def Author_amat(period, author):
    D = Matrix_empty(len_amat, len(period))
    D[0] = period
    for aux in author:
        day = aux[2].toordinal() - date(aux[2].year, 1, 1).toordinal() + 1
        interval = ((day - 1) / 3) + 1
        D[int(interval)][int(aux[2].year-date_min)] += 1
    return D

def Count_PM(period, author, len_table, PM):
    PM_count = 0
    for y in range(0, len(period)):
        for m in range(1, len_table):
            if author[m][y] != 0:
                PM_count += PM
    return PM_count

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
    print 'Proyecto: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM people')
    tot_authors = int(cursor.fetchall()[0][0])
    cursor.execute('SELECT COUNT(*) FROM scmlog')
    tot_commits = int(cursor.fetchall()[0][0])
    
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

    list_commit_authors = []
    PM_pro = 0
    PM_semi = 0
    PM_amat = 0
    aut_type = [0, 0, 0]
    list_commits = []
    for author in authors:
        list_commits.append(len(author))
        if len(author) >= (tot_commits*0.1):
            aut = Author_prof(period, author)
            list_commit_authors.append(aut)
            PM_pro += Count_PM(period, aut, len_pro, 1)
            aut_type[0] += 1
        elif len(author) >= (tot_commits*0.05):
            aut = Author_semi(period, author)
            list_commit_authors.append(aut)
            PM_semi += Count_PM(period, aut, len_semi, 5.0/22.0)
            aut_type[1] += 1
        else:
            aut = Author_amat(period, author)
            list_commit_authors.append(aut)
            PM_amat += Count_PM(period, aut, len_amat, 3.0/30.0)
            aut_type[2] += 1
    
    
    print 'Total commits: ' + str(tot_commits)
    print 'Prof: ' + str(tot_commits*0.1) + ' Semi: ' + str(tot_commits*0.05)
    print
    print 'PM_pro: ' + str(PM_pro)
    print 'PM_semi: ' + str(PM_semi)
    print 'PM_amat: ' + str(PM_amat)
    print 'PM_tot: ' + str(PM_pro + PM_semi + PM_amat)
    print ('Type of author[PRO,SEMI,AMAT]: ', aut_type)
    print

    cursor.close()
    con.close()
