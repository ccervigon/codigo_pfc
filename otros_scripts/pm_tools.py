#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
from datetime import *
import matplotlib.pyplot as plt
import numpy as np

len_pro = 13 #12 months + 1 to the year
len_semi = 54 #53 weaks + 1 to the year
len_amat = (365/3)+2 #365/3 slots of 3 days + 1 to the year

#Creador de una matriz vacia
def Matrix_empty(rows, columns):
    A = []
    for i in range(0,rows):
        A.append([0]*columns)
    return A

# --------- ACCESO A BBDD ----------

def open_bd(project):
    con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
                          db=project)
    cursor = con.cursor()
    
    return con, cursor

def close_bd(cursor, con):
    cursor.close()
    con.close()

def extract_info(cursor):
    cursor.execute('SELECT COUNT(*) FROM people')
    tot_authors = int(cursor.fetchall()[0][0])
    cursor.execute('SELECT COUNT(*) FROM scmlog')
    tot_commits = int(cursor.fetchall()[0][0])
    cursor.execute('select sum(added) from commits_lines')
    tot_added = int(cursor.fetchall()[0][0])
    cursor.execute('select sum(removed) from commits_lines')
    tot_removed = int(cursor.fetchall()[0][0])
    
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

    return tot_authors, tot_commits, tot_added, tot_removed, period, authors

# --------- GET INFO ----------

#Devuelve una matriz de [MESESxANIOS] con el total de commits realizado cada mes.
def commits_months(period, authors):
    M = Matrix_empty(13, len(period))
    M[0] = period
    for author in authors:
        for aux in author:
            M[int(aux[2].month)][int(aux[2].year-date_min)] += 1
    return M

#Devuelve un vector con los commits realizados por el autor a lo largo del mes elegido.
def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

#Devuelve un vector con los commits realizados por el autor por mes a lo largo del proyecto.
def commits_month_author(years, author):
    M = np.zeros((12*years), dtype=np.int)
    for commit in author:
        M[(int(commit[2].year-date_min)*12)+(int(commit[2].month)-1)] += 1
    return M

def info_authors_period_activity(authors):
    list_activity_authors = []
    for author in authors:
        #OH=Office Hour, AO=After Office, LN=Late Night
        activity = [0, 0, 0] # [OH, AO, LN]
        for commit in author:
            if commit[1].hour >= 9 and commit[1].hour < 17:     #OH
                activity[0] += 1
            elif commit[1].hour >= 1 and commit[1].hour < 9:    #LN
                activity[2] += 1
            else:                                               #AO
                activity[1] += 1
        list_activity_authors.append(activity)
    
    return list_activity_authors

#Devuelve las modas del vector pasado
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

# --------- SHOW INFO ----------

#Imprime los commits en una tabla [SEMANAxANIO]
def show_commits_author_weeks(author_id, period, authors):
    W = Matrix_empty(54, len(period))
    W[0] = period
    for aux in authors[author_id]:
        day = aux[2].toordinal() - date(aux[2].year, 1, 1).toordinal() + 1
        week = ((day - 1) / 7) + 1
        W[int(week)][int(aux[2].year-date_min)] += 1
    for i in range(0, 54):
        print W[i]
    print
    
#Imprime los commits en una tabla [MESxANIO]
def show_commits_author_months(author_id, period, authors):
    M = Matrix_empty(13, len(period))
    M[0] = period
    for aux in authors[author_id]:
        M[int(aux[2].month)][int(aux[2].year-date_min)] += 1
    for i in range(0, 13):
        print M[i]
    print

#Imprime el ID del autor de los commits indicados en el argumento commits
#y las tablas de commits agrupados en semanas y meses.
def info_author (list_commits, commits, period, authors):
    try:
        a = list_commits.index(commits)
        print a
        show_commits_author_weeks(a, period, authors)
        show_commits_author_months(a, period, authors)
    except:
        pass

# --------- SMOOTH ----------

def smooth(x, window_len=10, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    import numpy as np    
    t = np.linspace(-2,2,0.1)
    x = np.sin(t)+np.random.randn(len(t))*0.1
    y = smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        #raise ValueError, "Input vector needs to be bigger than window size."
        return x

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]

def fix_smooth(f_original, len_window, window):
    f_smooth = np.array([], dtype=np.int)
    flag = False
    position = 0
    for i in range(0, len(f_original)):
        if f_original[i] != 0:
            if i+1 == len(f_original):
                if flag:
                    if len(f_original[position:]) == 7:
                        smooth_aux = smooth(np.array(f_original[position-1:]), len_window, window)
                        smooth_aux = smooth_aux[1:]
                    else:
                        smooth_aux = smooth(np.array(f_original[position:]), len_window, window)
                    f_smooth = np.append(f_smooth, smooth_aux)
                else:
                    f_smooth = np.append(f_smooth, f_original[i])
            elif not flag:
                position = i
                flag = True
        elif f_original[i] == 0 and flag:
            if i+1 == len(f_original):
                if len(f_original[position:i]) == 7:
                    smooth_aux = smooth(np.array(f_original[position-1:i]), len_window, window)
                    smooth_aux = smooth_aux[1:]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
            elif f_original[i+1] == 0:
                if len(f_original[position:i]) == 7:
                    smooth_aux = smooth(np.array(f_original[position-1:i]), len_window, window)
                    smooth_aux = smooth_aux[1:]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
        else:
            f_smooth = np.append(f_smooth, 0)
    return f_smooth