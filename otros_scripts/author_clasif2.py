#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
from datetime import *

#Creador de una matriz vacia
def Matriz_vacia(filas, columnas):
    A = []
    for i in range(0,filas):
        A.append([0]*columnas)
    return A

#Muestra la informacion del reparto de la actividad temporal del autor elegido 
def activity_info(list_commits_author, authors, author):
    print list_commits_author[author]
    hours = Matriz_vacia(2, 24)
    hours[0] = range(1,25)
    for aux in authors[author]:
        hours[1][int(aux[2].hour)-1] += 1
    print hours[0]
    print hours[1]

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

con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                      db=list_projects[3])
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
    query = ('SELECT id, author_id, date FROM scmlog '
             'WHERE author_id = %s ORDER BY date')
    cursor.execute(query, i)
    authors.append(cursor.fetchall())

list_commits_author = []
for author in authors:
    #OH=Office Hour, AO=After Office, LN=Late Night
    activity = [0, 0, 0] # [OH, AO, LN]
    for commit in author:
        if commit[2].hour >= 9 and commit[2].hour < 17:     #OH
            activity[0] += 1
        elif commit[2].hour >= 1 and commit[2].hour < 9:    #LN
            activity[2] += 1
        else:                                               #AO
            activity[1] += 1
    list_commits_author.append(activity)

author = 13
print 'Author ID:' + str(author + 1)
activity_info(list_commits_author, authors, author)

cursor.execute('select sum(added) from commits_lines')
tot_lines = int(cursor.fetchall()[0][0])
add_rem = [0, 0]
cursor.execute('SELECT SUM(added) FROM commits_lines '
               'WHERE id = ANY (SELECT id FROM scmlog WHERE author_id = %s)', author+1)
add_rem[0] = int(cursor.fetchall()[0][0])
cursor.execute('SELECT SUM(removed) FROM commits_lines '
               'WHERE id = ANY (SELECT id FROM scmlog WHERE author_id = %s)', author+1)
add_rem[1] = int(cursor.fetchall()[0][0])
print 'Total de lineas: ' + str(tot_lines)
print add_rem
print 'Add del total: ' + str(add_rem[0]*100/tot_lines) + '% ; Rem del total: ' + str(add_rem[1]*100/tot_lines) + '%'

cursor.close()
con.close()
