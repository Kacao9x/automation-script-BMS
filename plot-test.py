import matplotlib.pyplot as plt
import numpy as np
import subprocess
import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *
from scipy import signal

# ==============================================================================#

# Subprocess's call command with piped output and active shell
def Call(cmd):
    return subprocess.call(cmd, stdout=subprocess.PIPE,
                           shell=True)


# Subprocess's Popen command with piped output and active shell
def Popen(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0].rstrip()


# Subprocess's Popen command for use in an iterator
def PopenIter(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).stdout.readline


# ==============================================================================#

# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls ' + address + ' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name


def count_good_value(x):
    boundary = 0.025  # pick a threshold from the plot. removing DC offset may affect the value
    count = 0
    for i in range(0, len(x)):
        if boundary < abs(x[i]):
            count += 1

    return count


def find_data_std(x):
    x_arr = np.array(x)
    x_arr = np.absolute(x_arr)
    return np.std(x_arr[50:-1], ddof=1)


def find_dup_run(x):
    # return max(x) == min(x)   # for echo C + D
    return (max(x) - min(x)) < 0.015  # for echo E


def _locate_2ndEcho_index(data):
    data = data[170: 260]
    return 170 + data.index(max(data))


def concat_all_data(tempC=bool, search_key=str):
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

            data = [float(num) for num in y_str]  # convert string to float

            single_set = pd.DataFrame(
                {captureID: data})  # concat all data set into a singl dataframe
            big_set = pd.concat([big_set, single_set], axis=1,
                                ignore_index=True)

        big_set = big_set.fillna(0)  # with 0s rather than NaNs

        return big_set, list_file


def _find_avg(numbers):
    return (sum(numbers)) / max(len(numbers), 1)


def Diff(li1, li2):
    return (list(set(li1) - set(li2)))


def upsample(s,n,phase=0):
    return np.roll(np.kron(s, np.r_[1, np.zeros(n-1)]), phase)

def interp(s,r,l=4,alpha=0.5):
    b = signal.firwin(2*l*r+1, alpha/r)
    a = 1
    return r*signal.lfilter(b,a,upsample(s,r))[r*l+1:-1]

# ==============================================================================#
# ======================== MAIN FUNCTION ======================================-#
def main():
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
    # rawRead_concat = pd.DataFrame()
    # while cycle_id < cycle + 1:
    #
    #     oneRead,list_file = concat_all_data(tempC=False,
    #                                         search_key='cycle' + str(cycle_id) + '-')
    #
    #     '''  generate all Raw data sets csv report
    #         Comment out the next 2 lines if don't use '''
    #     rawRead_concat = pd.concat([rawRead_concat, oneRead], axis=1)           # concat the avg data into dataframe
    #
    #     '''  Plot all captures per read '''
    #
    #     [row, column] = oneRead.shape
    #     dt = float(1/7200000)
    #     x = np.arange(0, 1.38888889e-7*row, 1.38888889e-7)
    #
    #     plt.figure(2)
    #     plt.title('SoC vs Time | Bandpass Enabled')
    #     plt.interactive(False)
    #
    #     avgPos = 0
    #     while avgPos < column:
    #         y = echoes_dsp.apply_bandpass_filter(oneRead.loc[:, avgPos],
    #                                              300000, 1200000, 51)
    #         # change the integers inside this routine as (number of rows, number of columns, plotnumber)
    #         plt.plot(x, y, label='0%s ' % str(avgPos +1))
    #         plt.xlim((0, 0.00005))
    #         plt.xlabel('time')
    #         plt.ylabel('amplitude')
    #         avgPos += 1
    #     plt.legend()
    #     plt.show()
    #
    #     cycle_id += 1

    # rawRead_concat = rawRead_concat.T
    # rawRead_concat.to_csv(address + 'allRawData.csv')

    """
    (3) plot avg of each cycle. Save avg (mean) to csv file
    # """
    avgTable_concat = pd.DataFrame()

    plt.figure(1)
    plt.interactive(False)
    ped = 1.38888889e-7
    while cycle_id < cycle + 1:
        # if cycle_id == 1:
        #     cycle_id = 2
        oneRead, list_file = concat_all_data(tempC=False,
                                             search_key='cycle' + str(
                                                 cycle_id) + '-')
        [row, column] = oneRead.shape

        avg = np.mean(oneRead, axis=1)  # average 64 captures
        avg = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000,
                                               51)  # apply bandpass
        avg = [a_i - b_i for a_i, b_i in zip( avg, backgrd )]                 # subtract background

        temp = interp(avg,10)
        adc_captures_interp = interp(temp,10)
    

        a = adc_captures_interp[8999:19999]
        T1 =9000 + np.argmax(a)
        print("argmax of T1"+str(np.argmax(a)))
        
        while adc_captures_interp[T1] > 0:
          T1 = T1+1
        print("T1 position is = "+str(T1))
        T1 = float(T1*0.0014)
        print("T1 is = "+str(T1))
        T2 = 20000+np.argmin(adc_captures_interp[19999:29999])
        
        while adc_captures_interp[T2] < 0:
          T2 = T2+1
        print("T2 position is = "+str(T2))
        T2 = float(T2*0.0014)
        print("T2 is = "+str(T2))

        tempC_1 = 21.6958
        diff_corr = (tempC_1 - 24)*0.051
        diff = T2-T1-diff_corr
        print("Temperature is = "+str(tempC_1))
        #SoC = 87.95*diff*diff - 3011*diff + 25210
        SoC1 = -1201*diff*diff + 34310*diff - 244900
        #print("SoC is = "+str(SoC))
        print("SoC is = "+str(SoC1))

        # col_header = cycle_id
        # avgTable = pd.DataFrame({col_header: avg})
        # avgTable_concat = pd.concat([avgTable_concat, avgTable],
        #                             axis=1)  # concat the avg data into dataframe

        # x_1 = np.arange(0, ped * row, ped)
        # ax1 = plt.subplot(212)
        # ax1.margins(0.05)
        # ax1.plot(x_1, avg, label='Cycle %s ' % str(cycle_id))
        # plt.xlim((0, 0.00004))
        # plt.xlabel('time')
        # plt.ylabel('amplitude')

        # x_2 = np.arange(79 * ped, 104 * ped, 1.38888889e-7)
        # avg_2 = avg[79: 104]
        # ax2 = plt.subplot(221)
        # ax2.margins()
        # ax2.plot(x_2, avg_2)
        # ax2.set_title('Echo 1')

        # x_3 = np.arange(123 * ped, 151 * ped, 1.38888889e-7)
        # avg_3 = avg[123: 151]
        # ax3 = plt.subplot(222)
        # # ax3.margins(x=0, y=-0.25)  # Values in (-0.5, 0.0) zooms in to center
        # ax3.plot(x_3, avg_3)
        # ax3.set_title('Echo 2')

        # plt.plot(x, avg, label='Cycle %s ' % str(cycle_id))
        # plt.title(' TC10 |' + ' SoH = 73 | Bandpass Enabled | No Noise removed | primary')
        # plt.xlim((0, 0.00005))
        # plt.xlabel('time')
        # plt.ylabel('amplitude')
        cycle_id += 1

        


    # avgTable_concat = avgTable_concat.mean( axis =1 )                         # avg all cycle
    # avgTable_concat = avgTable_concat.T
    # avgTable_concat.to_csv(address + 'TC10-primary.csv')

    # plt.legend()
    # plt.show()
    return


# ==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
address = '/media/kacao-titan/Ultra-Fit/titan-echo-boards/Steve-test/primary/'
echoes_index = []
backgrd = []

avgPos = 0  # number of capture in each cycle
avgNum = 64
cycle = 3
cycle_id = 3

ME = 4
ME_id = 1

with open(address + 'backgrd.dat') as my_file:
    y_str = my_file.read()
    y_str = y_str.splitlines()

    for num in y_str:
        backgrd.append(float(num))
my_file.close()

echoes_dsp = echoes_signals(7200000.0)
if __name__ == '__main__':
    main()