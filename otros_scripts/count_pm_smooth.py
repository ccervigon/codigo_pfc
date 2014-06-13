#!/usr/bin/python

import MySQLdb
from datetime import *
import matplotlib.pyplot as plt
import numpy as np

class Window:
    def __init__(self):
        self.size_1 = []
        self.size_2 = []
        self.size_3 = []
        self.size_4 = []
        self.size_5 = []

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

def plot_window_result_author(window, author):
    ax = plt.subplot(5,1,1)
    ax.bar(np.arange(len(window.size_1[author-1])), window.size_1[author-1])
    ax.set_xlim(right=len(window.size_1[author-1]))
    ax.set_xlim(700, 800)
    ax.set_ylim(top=14)
    ax = plt.subplot(5,1,2)
    ax.bar(np.arange(len(window.size_2[author-1])), window.size_2[author-1])
    ax.set_xlim(right=len(window.size_1[author-1]))
    ax.set_xlim(700, 800)
    ax.set_ylim(top=14)
    ax = plt.subplot(5,1,3)
    ax.bar(np.arange(len(window.size_3[author-1])), window.size_3[author-1])
    ax.set_xlim(right=len(window.size_1[author-1]))
    ax.set_xlim(700, 800)
    ax.set_ylim(top=14)
    ax = plt.subplot(5,1,4)
    ax.bar(np.arange(len(window.size_4[author-1])), window.size_4[author-1])
    ax.set_xlim(right=len(window.size_1[author-1]))
    ax.set_xlim(700, 800)
    ax.set_ylim(top=14)
    ax = plt.subplot(5,1,5)
    ax.bar(np.arange(len(window.size_5[author-1])), window.size_5[author-1])
    ax.set_xlim(right=len(window.size_1[author-1]))
    ax.set_xlim(700, 800)
    ax.set_ylim(top=14)

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
"""
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
"""
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
    for author in authors:
        M = np.array([])
        for year in period:
            for month in range(1, 13):
                aut = calendar_commit_month_author(year, month, author)
                M = np.concatenate((M, aut))
        work_authors.append(M)

    com_auts = commits_months(period, authors)
    
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    len_windows = [1, 7, 9, 11, 30]
    
    result_win = []
    
    for w in windows:
        win = Window()
        i = 0
        for size in len_windows:
            i += 1
            smooth_authors = [] 
            for author in work_authors:
                smooth_authors.append(fix_smooth(author, size, w))
            if i == 1:
                win.size_1 = smooth_authors
            elif i == 2:
                win.size_2 = smooth_authors
            elif i == 3:
                win.size_3 = smooth_authors
            elif i == 4:
                win.size_4 = smooth_authors
            elif i == 5:
                win.size_5 = smooth_authors
        result_win.append(win)
    
    plt.hold(True)
    for w in range(0, len(windows)):
        author = 8
        plot_window_result_author(result_win[w], author)
        plt.subplot(len(len_windows),1,1)
        plt.title(windows[w])
        #plt.show()
        plt.savefig('figuras/smooth/' + windows[w] + '_' + str(author) + '.png', dpi = 200)
        plt.close()

    '''
    plt.hold(True)
    for size in range(1, len(len_windows)+1):
        author = 8
        if size == 1:
            for w in range(0, len(windows)):
                ax = plt.subplot(5,1,w+1)
                ax.bar(np.arange(len(result_win[w].size_1[author-1])), result_win[w].size_1[author-1])
                ax.set_xlim(right=len(result_win[w].size_1[author-1]))
                ax.set_xlim(700, 800)
        if size == 2:
            for w in range(0, len(windows)):
                ax = plt.subplot(5,1,w+1)
                ax.bar(np.arange(len(result_win[w].size_2[author-1])), result_win[w].size_2[author-1])
                ax.set_xlim(right=len(result_win[w].size_2[author-1]))
                ax.set_xlim(700, 800)
        if size == 3:
            for w in range(0, len(windows)):
                ax = plt.subplot(5,1,w+1)
                ax.bar(np.arange(len(result_win[w].size_3[author-1])), result_win[w].size_3[author-1])
                ax.set_xlim(right=len(result_win[w].size_3[author-1]))
                ax.set_xlim(700, 800)
        if size == 4:
            for w in range(0, len(windows)):
                ax = plt.subplot(5,1,w+1)
                ax.bar(np.arange(len(result_win[w].size_4[author-1])), result_win[w].size_4[author-1])
                ax.set_xlim(right=len(result_win[w].size_4[author-1]))
                ax.set_xlim(700, 800)
        if size == 5:
            for w in range(0, len(windows)):
                ax = plt.subplot(5,1,w+1)
                ax.bar(np.arange(len(result_win[w].size_5[author-1])), result_win[w].size_5[author-1])
                ax.set_xlim(right=len(result_win[w].size_5[author-1]))
                ax.set_xlim(700, 800)
        plt.subplot(5,1,1)
        plt.title('Size: ' + str(1 + (size-1)*2))
        plt.savefig('figuras/prueba/' + str(size) + '_' + str(author) + '.png', dpi = 200)
        #plt.show()
        plt.close()
    '''
    
    """
    #MATRIX OF RESULTS OF DIFERRENT WINDOWS TYPES AND DIFERENT SIZE [WINDOWS x SIZE_WINDOWS]
    windows=['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    len_max_windows = 7
    pm_matrix = np.zeros([len(windows)+1, (len_max_windows-3)+2], dtype='a8')
    pm_matrix[0][0] = 'size_win'
    for i in range(3, (len_max_windows)+1):
        pm_matrix[0][i-2] = i
    
    for w in range(0, len(windows)):
        pm_matrix[w+1][0] = windows[w]
        for len_window in range(0, (len_max_windows-3)+1):
            
            smooth_work_days_authors = []
            for aut in work_authors:
                smooth_work_days_authors.append(smooth(np.array(aut), len_window+3, windows[w]))
            
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

            pm_matrix[w+1][len_window+1] = "{0:.2f}".format(np.sum(PM))

    print pm_matrix
    print
    
    list_PM.append(pm_matrix)
    """

    cursor.close()
    con.close()
