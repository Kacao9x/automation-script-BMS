
import matplotlib.pyplot as plt
import numpy as np
import os, subprocess
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

# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls '+ address +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name

def main():
    global ME
    global ME_id


    avgTable_concat = pd.DataFrame()
    while ME_id < ME + 1:
        # if ME_id == 2 or ME_id == 3 or ME_id == 4:
        #     ME_id = 5
        file_list = display_list_of_file( 'Me0' + str(ME_id) )
        print (file_list)
        ME_dataFrame = pd.DataFrame()


        for filename in file_list:
            with open( address + filename ) as outfile:
                avg_tab = pd.read_csv(outfile, sep=',', error_bad_lines=False)
            outfile.close()

            ME_dataFrame = pd.concat([ME_dataFrame, avg_tab], axis=1,
                                     ignore_index=True)

        ME_dataFrame = ME_dataFrame.fillna( 0 )
        [row, column] = ME_dataFrame.shape
        print (ME_dataFrame.shape)

        avg = np.mean( ME_dataFrame, axis = 1 )
        avg = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)

        col_header = ME_id
        avgTable = pd.DataFrame( { col_header : avg })
        avgTable_concat = pd.concat( [avgTable_concat, avgTable], axis=1)

        x = np.arange(0, 1.38888889e-7 * row, 1.38888889e-7)
        plt.plot(x, avg, label='ME 0%s ' % str(ME_id))
        plt.title('SoC vs Time for average data |' + ' S0H = 100 | echo-E')
        plt.xlim((0, 0.00005))
        plt.ylim((-0.6,0.5))
        plt.xlabel('time')
        plt.ylabel('amplitude')

        ME_id += 1

    avgTable_concat.to_csv(address + 'avgData-ME-SoH100.csv')
    plt.legend()
    plt.show()
    return


#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
address = 'C:/Users/eel/TitanAES/echo-board-data/echo-E/avgdata/bandpass/'
bad_data = []
echoes_index = []

avgPos = 1  # number of capture in each cycle
avgNum = 64
cycle = 750
cycle_id = 1

ME = 5
ME_id = 1
echoes_dsp = echoes_signals( 7200000.0 )
# cycle number to plot

if __name__ == '__main__':
    main()