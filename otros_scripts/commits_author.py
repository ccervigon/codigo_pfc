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

list_projects = []
list_projects.append('vizgrimoire_vizgrimoirer_cvsanaly')
list_projects.append('openstack_tempest_cvsanaly')
list_projects.append('twbs_bootstrap_cvsanaly')
con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', db=list_projects[1])
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
	query = ('SELECT committer_id, author_id, date FROM scmlog '
		 	 'WHERE author_id = %s ORDER BY date')
	cursor.execute(query, i)
	authors.append(cursor.fetchall())

#Lista de autores con una matriz 13xANIOS cada uno, con el numero
#de commits realizados en cada uno de los meses de cada anio.
list_author_month = []
for author in authors:
	M = Matriz_vacia(13, 3)
	M[0] = period
	for aux in author:
		M[int(aux[2].month)][int(aux[2].year-date_min)] += 1
	list_author_month.append(M)

#Lista de autores con una matriz 54xANIOS cada uno, con el numero
#de commits realizados en cada uno de las semanas de cada anio.
list_author_weeks = []
for author in authors:
	W = Matriz_vacia(54, 3)
	W[0] = period
	for aux in author:
		day = aux[2].toordinal() - date(aux[2].year, 1, 1).toordinal() + 1
		week = ((day - 1) / 7) + 1
		W[int(week)][int(aux[2].year-date_min)] += 1
	list_author_weeks.append(W)

#Hacemos la cuenta de 1 PM por cada mes que haya trabajado cada autor.
PM_mounth = 0
for a in range(0, len(list_author_month)):
	for y in range(0, len(period)):
		for m in range(1, 13):
			if list_author_month[a][m][y] != 0:
				PM_mounth += 1
				
#Hacemos la cuenta de 5/22 PM por cada semana que haya trabajado cada autor.
PM_week = 0
for a in range(0, len(list_author_weeks)):
	for y in range(0, len(period)):
		for w in range(1, 54):
			if list_author_weeks[a][w][y] != 0:
				PM_week += 5.0/22.0

print 'Contando por meses:' + str(PM_mounth)
print 'Contando por semanas:' + str(PM_week)

cursor.close()
con.close()
