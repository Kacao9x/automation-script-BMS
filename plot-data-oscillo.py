
import matplotlib.pyplot as plt
import numpy as np
import os, subprocess
import thLib as th
import glob
import pandas as pd
from scipy.signal import filtfilt, firwin, upfirdn



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

# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls '+ address +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name

def concat_custom_data( ):
    global x, y
    value_table = pd.DataFrame()
    time_table = pd.DataFrame()

    list_file = display_list_of_file('.dat')
    print (list_file)
    for filename in list_file:
    # for filename in glob.glob(os.path.join(address, "*.dat")):
        my_file = open(address + filename)
        y_str = my_file.read()
        y_str = y_str.splitlines()

        for i, num in enumerate(y_str):
            x.append( float( num.split()[0] ))
            y.append(float( num.split()[1] ))

        amplitude = pd.DataFrame( y )
        time_scale = pd.DataFrame( x )

        value_table = pd.concat([value_table, amplitude], axis=1, ignore_index=True)
        time_table = pd.concat([time_table, time_scale], axis=1, ignore_index=True)

    # with 0s rather than NaNs
    # value_table = value_table.fillna(0)

    return value_table, time_table


def main():
    value_table, time_table = concat_custom_data()
    plt.figure(2)
    plt.title('SoC vs Time')
    plt.interactive(False)

    print (value_table.head())
    [row, column] = value_table.shape
    i=1

    while i < column + 1:
        # plt.subplot(column/2, 2, i)
        # change the integers inside this routine as (number of rows, number of columns, plotnumber)
        plt.plot(time_table.loc[:,i-1], value_table.loc[:, i - 1])
        plt.xlim((0, 0.00005))
        i = i + 1

    plt.legend()
    plt.show()


#==============================================================================#
address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
y, x = [], []
if __name__ == '__main__':
    main()