#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
from math import sqrt
import matplotlib.pyplot as plt
import argparse
import numpy as np
from scipy.stats import mode

def moda(l):
    repeticiones = 0
    for i in l:
        apariciones = l.count(i)
        if apariciones > repeticiones:
            repeticiones = apariciones

    modas = []
    for i in l:
        apariciones = l.count(i)
        if apariciones == repeticiones and i not in modas:
            modas.append(i)
    return modas

def calc_num_authors(percent, list, tot_list):
    flag = False
    i = 0
    sum_dat = 0
    while not flag:
        sum_dat += list[i]
        if sum_dat >= tot_list*percent:
            flag = True
        else:
            i += 1
    
    sum_1a_mit = 0
    for a in range(0, i):
        sum_1a_mit += list[a]
    sum_2a_mit = tot_list - sum_1a_mit
    
    return i, sum_1a_mit, sum_2a_mit

def print_estadisticas(percent, porcentaje_list, tipo_info):
    print '% de autores con el ' + str((1-percent)*100) + '% de los ' + tipo_info + ':'
    print porcentaje_list
    
    print("La media es: ", np.mean(porcentaje_list))
    print ('La mediana es: ', np.median(porcentaje_list))
    print("La moda es: ", moda(porcentaje_list))
    print ('Varianza: ', np.var(porcentaje_list))
    print ('Desviacion tipica: ', np.std(porcentaje_list))

def print_info(tot_authors, tot_info, aut_1a_mit, percent, sum_1a_mit, sum_2a_mit, tipo_info):
    print 'Info ' + tipo_info + ':'
    print 'Autores ' + str(100-100*percent) + '%: ' + str(tot_authors - aut_1a_mit) + ' ' + str(100*float(tot_authors - aut_1a_mit)/float(tot_authors)) + '%'
    print 'Autores resto: ' + str(aut_1a_mit) + ' ' + str(100*float(aut_1a_mit)/float(tot_authors)) + '%'
    print 'Total de ' + tipo_info + ': ' + str(tot_info) + '; ' + str(100-100*percent) + '% ' + tipo_info + ': ' + str(tot_info*(1-percent))
    print 'Suma autores ' + str(100-100*percent) + '%: ' + str(sum_2a_mit)
    print 'Suma autores resto: ' + str(sum_1a_mit)
    print

def autores_en_porcentaje(list_data, tot_list, tot_authors, percent):    
    flag = False
    i = 0
    sum_data = 0
    lr_com = list(sorted(list_data))
    while not flag:
        sum_data += lr_com[i]
        if sum_data >= tot_list*percent:
            flag = True
        else:
            i += 1
    return tot_authors - i

def figuras_list(list_data, tot_list, tot_authors, type_data):
    list_aux = range(1, len(list_data) + 1)
    ax.plot(list_aux, list(reversed(sorted(list_data))))
    X1 = autores_en_porcentaje(list_data, tot_list, tot_authors, 0.2)
    X2 = autores_en_porcentaje(list_data, tot_list, tot_authors, 0.1)
    plt.ylabel(type_data)
    ax.axvspan(0, X1, facecolor = 'b', alpha = 0.25)
    ax.axvspan(X1, X2, facecolor = 'g',alpha = 0.25)
    textstr = 'Total ' + type_data + ':\nBlue: 80% of total\nGreen: 90% of total'
    props = dict(boxstyle = 'round', facecolor = 'red', alpha = 0.15)
    ax.text(0.98, 0.90, textstr, transform = ax.transAxes, fontsize = 10, verticalalignment = 'top', horizontalalignment = 'right', bbox = props)


list_projects = []
list_projects.append('openstack_authors')
'''
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
'''
# Parse command line options
parser = argparse.ArgumentParser(description="""
Script que elabora graficas y saca resultados
de una lista de proyectos""")
parser.add_argument("-pc",
                    help = "Percent Commits (Default 0.2)",
                    type = float, default = 0.2)
parser.add_argument("-pa",
                    help = "Percent Added (Default 0.2)",
                    type = float, default = 0.2)
parser.add_argument("-pr",
                    help = "Percent Removed (Default 0.2)",
                    type = float, default = 0.2)
parser.add_argument("-figsave",
                    help = "Figure Save (default False)",
                    default = False, action='store_true')
parser.add_argument("-figshow",
                    help = "Figure Show (default False)",
                    default = False, action='store_true')

args = parser.parse_args()
print args
print

corr_com_add = []
corr_com_rem = []
corr_add_rem = []
com_corr = []

porcentaje_commits = []
porcentaje_added = []
porcentaje_removed = []
percent_commits = args.pc
percent_add = args.pa
percent_rem = args.pr
plt.hold()

for project in range(0, len(list_projects)):
    print 'Proyecto: ' + list_projects[project]
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=list_projects[project])
    cursor = con.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM scmlog')
    tot_commits = int(cursor.fetchall()[0][0])
    
    cursor.execute('SELECT COUNT(*) FROM people')
    tot_authors = int(cursor.fetchall()[0][0])
    print 'Total de autores: ' + str(tot_authors)
    print
    
    cursor.execute('SELECT sum(added) FROM commits_lines')
    tot_lines = int(cursor.fetchall()[0][0])

    commits_author = []
    added_author = []
    removed_author = []
    author = 1
    while author <= tot_authors:
        #print str(author) + ' de ' + str(tot_authors) + ' del proyecto ' + list_projects[project]
        query = ('SELECT COUNT(*) from scmlog where author_id = %s')
        cursor.execute(query, author)
        commits_author.append(int(cursor.fetchall()[0][0]))
        query = ('SELECT SUM(added) FROM commits_lines '
                 'WHERE id = ANY (SELECT id FROM scmlog WHERE author_id = %s)')
        cursor.execute(query, author)
        try:
            aux = int(cursor.fetchall()[0][0])
        except:
            aux = 0
        added_author.append(aux)
        query = ('SELECT SUM(removed) FROM commits_lines '
                 'WHERE id = ANY (SELECT id FROM scmlog WHERE author_id = %s)')
        cursor.execute(query, author)
        try:
            aux = int(cursor.fetchall()[0][0])
        except:
            aux = 0
        removed_author.append(aux)
        author += 1
    
    commits_author_sorted = list(sorted(commits_author))
    added_author_sorted = list(sorted(added_author))
    removed_author_sorted = list(sorted(removed_author))
    
    autores_1a_mit_com, sum_1a_mit_com, sum_2a_mit_com = calc_num_authors(percent_commits, commits_author_sorted, tot_commits)
    autores_1a_mit_add, sum_1a_mit_add, sum_2a_mit_add = calc_num_authors(percent_add, added_author_sorted, tot_lines)
    autores_1a_mit_rem, sum_1a_mit_rem, sum_2a_mit_rem = calc_num_authors(percent_rem, removed_author_sorted, tot_lines)

    print_info(tot_authors, tot_commits, autores_1a_mit_com, percent_commits, sum_1a_mit_com, sum_2a_mit_com, 'commits')
    print_info(tot_authors, tot_lines, autores_1a_mit_add, percent_add, sum_1a_mit_add, sum_2a_mit_add, 'added')
    print_info(tot_authors, tot_lines, autores_1a_mit_rem, percent_rem, sum_1a_mit_rem, sum_2a_mit_rem, 'removed')


    porcentaje_commits.append(int(100*float(tot_authors - autores_1a_mit_com)/float(tot_authors)))
    porcentaje_added.append(int(100*float(tot_authors - autores_1a_mit_add)/float(tot_authors)))
    porcentaje_removed.append(int(100*float(tot_authors - autores_1a_mit_rem)/float(tot_authors)))
    
    if args.figsave | args.figshow:
        fig = plt.figure()
        ax = fig.add_subplot(3,1,1)
        figuras_list(commits_author_sorted, tot_commits, tot_authors, 'Commits')
        plt.xlim(xmin = 0)
        plt.title(list_projects[project])
        ax = fig.add_subplot(3,1,2)
        figuras_list(added_author_sorted, tot_lines, tot_authors, 'Lines Added')
        plt.xlim(xmin = 0)
        ax = fig.add_subplot(3,1,3)
        figuras_list(removed_author_sorted, tot_lines, tot_authors, 'Lines Removed')
        plt.xlim(xmin = 0)
        plt.xlabel('Author')
        #Guardado de graficas con los commits-autor en orden decreciente
        if args.figsave:
            plt.savefig('figuras/estadist/' + list_projects[project] + '.png', dpi = 150)
        if args.figshow:
            plt.show()
            try:
                input()
            except:
                pass 
    
    matrix = np.matrix([commits_author, added_author, removed_author])
    cov = np.cov(matrix)
    corr = np.corrcoef(matrix)
    print 'Covarianza ' + list_projects[project]
    print cov
    print
    print 'Correlacion ' + list_projects[project]
    print corr
    print
    com_corr.append(corr[0][1])
    corr_com_add.append("{0:.4f}".format(corr[0][1]))
    corr_com_rem.append("{0:.4f}".format(corr[0][2]))
    corr_add_rem.append("{0:.4f}".format(corr[1][2]))
    print '---------------------------------------'
    
    cursor.close()
    con.close()

print 'Estadisticas generales:'
print_estadisticas(percent_commits, porcentaje_commits, 'commits')
print '---------------------------------------'
print_estadisticas(percent_add, porcentaje_added, 'added')
print '---------------------------------------'
print_estadisticas(percent_rem, porcentaje_removed, 'removed')

print
print corr_com_add
print corr_com_rem
print corr_add_rem
print np.mean(com_corr)