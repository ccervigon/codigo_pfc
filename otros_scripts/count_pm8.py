#!/usr/bin/python

"""
Description: This program analize the projects and it obtains the PM of each project according to it detect
month to month the professional authors and it add the proportional part make by the rest of authors.
The values of work days by authors have been adjusted with a smoothing function.
"""

import MySQLdb
from datetime import *
import matplotlib.pyplot as plt
import numpy as np

class Info_diff:
    def __init__(self):
        self.media = []
        self.desv_tip = []

#Matrix empty creator
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

def commits_month_author(years, author):
    M = np.zeros((12*years), dtype=np.int)
    for commit in author:
        M[(int(commit[2].year-date_min)*12)+(int(commit[2].month)-1)] += 1
    return M

def pm_matrix_to_latex(project, pm_matrix):
    file = open('cod_latex.txt', 'a')
    file.write('\n')
    file.write('\smallskip\n')
    file.write('\\begin{table}[H]\n')
    file.write('\centering\n')
    file.write('\\begin{tabular}{|l|r|r|r|r|r|}\n')
    file.write('\hline\n')
    file.write('Project: & \multicolumn{5}{|c|}{' + project.replace('_', '\_') + '} \\\ \hline\n')
    file.write('size\_win & 3 & 4 & 5 & 6 & 7 \\\ \hline\n')
    for i in range(1,6):
        file.write(pm_matrix[i][0] + ' & ' + pm_matrix[i][1] + ' & ' + pm_matrix[i][2] + ' & ' +
                   pm_matrix[i][3] + ' & ' + pm_matrix[i][4] + ' & ' + pm_matrix[i][5] + ' \\\ \hline\n')
    file.write('\end{tabular}\n')
    file.write('\end{table}\n')
    file.close()

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

list_projects = []
#list_projects.append('vizgrimoire_vizgrimoirer_cvsanaly')
list_projects.append('openstack_tempest_cvsanaly')
'''
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
list_PM = []
file = open('cod_latex.txt', 'w')
file.close()

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
    for author in authors:
        M = []
        for year in period:
            for month in range(1, 13):
                aut = calendar_commit_month_author(year, month, author)
                work_days = 0
                for i in range(0, len(aut)):
                    if aut[i] != 0:
                        work_days += 1
                M.append(work_days)
        work_authors.append(M)

    com_auts = commits_months(period, authors)

    #MATRIX OF RESULTS OF DIFERRENT WINDOWS TYPES AND DIFERENT SIZE [WINDOWS x SIZE_WINDOWS]
    windows=['hanning', 'hamming', 'bartlett', 'blackman']
    len_windows = [5, 7, 9]
    pm_matrix = np.zeros([len(windows)+1, len(len_windows)+1], dtype='a8')
    pm_matrix[0][0] = 'size_win'
    for i in range(0, len(len_windows)):
        pm_matrix[0][i+1] = len_windows[i]

    list_aux = []
    for w in range(0, len(windows)):
        pm_matrix[w+1][0] = windows[w]
        
        i = 0
        for len_window in len_windows:
            
            i += 1
            smooth_work_days_authors = []
            for aut in work_authors:
                smooth_work_days_authors.append(fix_smooth(np.array(aut), len_window, windows[w]))

            list_aux.append(smooth_work_days_authors[7])

            y = 0
            PM = []
            len_list = len(smooth_work_days_authors[0])
            for month in range(0, len_list):
                prof_authors = 0
                min_dw = 15
                sum_com = 0
                m = (month % 12)
                if m == 0:
                    y += 1
                for author in range(0, tot_authors):
                    if smooth_work_days_authors[author][month] >= min_dw:
                        prof_authors += 1
                        sum_com += np.sum(calendar_commit_month_author(date_min+y-1, m+1, authors[author]))
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

            pm_matrix[w+1][i] = "{0:.2f}".format(np.sum(PM))
    
    print pm_matrix
    print
    
    pm_matrix_to_latex(list_projects[project], pm_matrix)

    list_PM.append(pm_matrix)

    cursor.close()
    con.close()
