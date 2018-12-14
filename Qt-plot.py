import sys
from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


import numpy as np
import subprocess
import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *


#==============================================================================#

#Subprocess's call command with piped output and active shell
def Call(cmd):
    return subprocess.call(cmd, stdout=subprocess.PIPE,
                           shell=True)

#Subprocess's Popen command with piped output and active shell
def Popen(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0].rstrip()

#Subprocess's Popen command for use in an iterator
def PopenIter(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).stdout.readline
#==============================================================================#


class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def plot(self):

        global avgPos
        global avgNum
        global cycle
        global cycle_id
        global backgrd

        """
        (2) plot all 64 raw data in one cycle
        detect a bad read by visual inspection
        Generate a csv report with all raw captures
        """
        # create an axis
        ax = self.figure.add_subplot(111)

        rawRead_concat = pd.DataFrame()
        while cycle_id < cycle + 1:

            oneRead,list_file = concat_all_data(tempC=False,
                                                search_key='cycle' + str(cycle_id) + '-')

            '''  generate all Raw data sets csv report
                Comment out the next 2 lines if don't use '''
            rawRead_concat = pd.concat([rawRead_concat, oneRead], axis=1)           # concat the avg data into dataframe

            '''  Plot all captures per read '''

            [row, column] = oneRead.shape
            dt = float(1/7200000)
            x = np.arange(0, 1.38888889e-7*row, 1.38888889e-7)
            plt.figure(2)
            # ax.title('SoC vs Time | Bandpass Enabled')
            # ax.plt.interactive(False)

            avgPos = 0
            while avgPos < column:
                y = echoes_dsp.apply_bandpass_filter(oneRead.loc[:, avgPos],
                                                     300000, 1200000, 51)
                # change the integers inside this routine as (number of rows, number of columns, plotnumber)

                ax.plot(x, y, label='0%s ' % str(avgPos +1))
                avgPos += 1
            ax.legend()
            # plt.show()
            self.canvas.draw()
            cycle_id += 1

        # ''' plot some random stuff '''
        # # create an axis
        # ax = self.figure.add_subplot(111)
        # # discards the old graph
        # ax.clear()
        # # plot data
        # ax.plot(data, '*-')
        # # refresh canvas
        # self.canvas.draw()


# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls '+ address +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name


def count_good_value ( x ):
    boundary = 0.025        #pick a threshold from the plot. removing DC offset may affect the value
    count = 0
    for i in range (0, len(x)):
        if boundary < abs (x[i]):
            count += 1

    return count

def find_data_std( x ):
    x_arr = np.array( x )
    x_arr = np.absolute( x_arr )
    return np.std( x_arr[50:-1], ddof=1 )

def find_dup_run( x ):
    # return max(x) == min(x)   # for echo C + D
    return (max( x ) - min( x )) < 0.015 # for echo E


def _locate_2ndEcho_index( data ):
    data = data[ 170 : 260 ]
    return 170 + data.index( max(data) )



def concat_all_data(tempC = bool, search_key = str):
    '''
    :param cycle: keyword number to search and sort out
    :param tempC: True to read the temperature files, False otherwise
    :return: a dataframe contains all avg capture in a custom format
            an array of all data sets
    '''
    big_set = pd.DataFrame()
    global echoes_index
    echoes_index = []
    if tempC:
        ''' Read the temperature files
        '''
        tC_1, tC_2 = [], []
        list_file = display_list_of_file(search_key)
        print (list_file)
        for filename in list_file:

            with open(address + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            for i, num in enumerate(y_str):
                if len(num.split()) > 2:
                    tC_1.append(num.split()[1])
                    tC_2.append(num.split()[2])

        return tC_2, tC_1


    else:
        '''Read data from capture files
        '''
        list_file = display_list_of_file(search_key)
        print (list_file)
        for captureID, filename in enumerate(list_file):

            with open(address + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float

            single_set = pd.DataFrame({captureID: data})                        # concat all data set into a singl dataframe
            big_set = pd.concat([big_set, single_set], axis=1,
                                ignore_index=True)

        big_set = big_set.fillna(0)                                             # with 0s rather than NaNs

        return big_set, list_file


def _find_avg( numbers ):
    return (sum(numbers)) / max(len(numbers), 1)

def Diff(li1, li2):
    return (list(set(li1) - set(li2)))


#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
address = '/media/kacao-titan/Ultra-Fit/titan-echo-boards/echo-A/TC12-H75_181211/secondary/'
echoes_index = []
backgrd = []

avgPos = 0  # number of capture in each cycle
avgNum = 64
cycle = 3
cycle_id = 1

ME = 4
ME_id = 1


echoes_dsp = echoes_signals( 7200000.0 )



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())