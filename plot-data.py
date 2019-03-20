import matplotlib.pyplot as plt
import numpy as np
import subprocess
# import thLib as th
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


# def count_good_value ( x ):
#     boundary = 0.025   #pick a threshold from the plot. removing DC offset may affect the value
#     count = 0
#     for i in range (0, len(x)):
#         if boundary < abs (x[i]):
#             count += 1
#
#     return count

def find_data_std( x ):
    x_arr = np.array( x )
    x_arr = np.absolute( x_arr )
    return np.std( x_arr[50:-1], ddof=1 )

#
def find_dup_run( x, primary ):
    # return max(x) == min(x)   # for echo C + D
    max_value = max( x )
    min_value = min( x )

    if primary:
        return max_value - min_value < 0.4
    else:
        return ( max_value - min_value < 0.015 or
                max_value - min_value > 0.5 )                                   # for echo B


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

def _unsued_method():
    """
    (4) Plot Temperature vs Amplitude at 30us
    """
    # concat temperature
    # tempTable = pd.DataFrame()
    # tC_1, tC_2 = concat_all_data(tempC=True, search_key='cycle')
    # tempTable['Temperature_bottom'] = tC_1
    # tempTable['Temperature_top'] = tC_2
    # tempTable.to_csv(address + 'temp.csv')
    #
    # with open(address + 'avgData.csv') as outfile:
    #     avgTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()
    # print (avgTable.head())
    #
    # with open(address + 'temp.csv') as outfile:
    #     tempTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()
    # tC = tempTable['Temperature'][:cycle]
    #
    # # cycle_id = 3
    # # while cycle_id < cycle + 1:
    # #     emptyResults, tC = concat_all_data(cycle_id, 'temp')
    # #     cycle_id += 1
    #
    # #calculate the value at 30ns
    # dt = 1.38888889e-7
    # row_id = int(round(30e-6 / dt))
    # print (row_id)
    #
    # value = avgTable.iloc[row_id][1:]
    # print (value)
    # print (tC)
    # plt.figure(4)
    # plt.scatter(tC, value)
    # plt.title('Temperature vs Amp (SOC = 46.5%)')
    # plt.xlabel('Temperature oC')
    # plt.ylabel('Amplitude')
    # plt.interactive(False)
    # plt.show()
    """
    (5) Temperature Plot
    """
    # with open(address + 'Me03-H100_181214_sorted.csv') as outfile:
    #     tempTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()
    #
    # # calculate the value at 30ns
    # cyc, temp_value = [], []
    # while cycle_id < cycle + 1:
    #     cyc.append(cycle_id)
    #     temp_value.append(tempTable['Temperature_top'][ cycle_id - 1])
    #     cycle_id += 1
    #
    # plt.figure(5)
    # plt.plot(cyc, temp_value, '-*')
    # plt.title('Temperature vs Cycle | SOH = 100')
    # plt.xlabel('Cycle')
    # plt.ylabel('TempC oC')
    # plt.interactive(False)
    # plt.show()


def _extra_plot_function():
    """
    (6) Plot the avg of each battery type
    """
    # global ME
    # global ME_id
    #
    # my_file = open(address + 'noise.dat')
    # y_str = my_file.read()
    # y_str = y_str.splitlines()
    # backgrd = []
    #
    # for num in y_str:
    #     backgrd.append(float(num))
    # my_file.close()
    #
    #
    # avgTable_concat = pd.DataFrame()
    # while ME_id < ME + 1:
    #
    #     file_list = display_list_of_file('Me0' + str(ME_id))
    #     print (file_list)
    #     ME_dataFrame = pd.DataFrame()
    #     avg_filter = pd.DataFrame()
    #
    #     for filename in file_list:
    #         with open(address + filename) as outfile:
    #             avg_tab = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    #         outfile.close()
    #
    #         ME_dataFrame = pd.concat([ME_dataFrame, avg_tab], axis=1,
    #                                  ignore_index=True)
    #
    #     ME_dataFrame = ME_dataFrame.fillna(0)
    #     [row, column] = ME_dataFrame.shape
    #     print (ME_dataFrame.shape)
    #
    #     avg = np.mean(ME_dataFrame, axis=1)
    #     # avg = [a_i - b_i for a_i, b_i in zip(avg, backgrd)]
    #     # for i in range(512):
    #     #     avg[i] = avg[i] - backgrd[i]
    #     avg = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)
    #
    #
    #     col_header = ME_id
    #     avgTable = pd.DataFrame({col_header: avg})
    #     avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)
    #
    #     x = np.arange(0, 1.38888889e-7 * row, 1.38888889e-7)
    #     plt.plot(x, avg, label='ME 0%s ' % str(ME_id))
    #     ME_id += 1
    #
    # avgTable_concat.to_csv(address + 'avgData-ME-SoH100.csv')
    # plt.title('SoC vs Time for average data |' + ' S0H = 100 | echo-E')
    # plt.xlim((0, 0.00005))
    # plt.ylim((-0.6, 0.5))
    # plt.xlabel('time')
    # plt.ylabel('amplitude')
    #
    # plt.legend()
    # plt.show()

    """
     (7) plot signals from different board
    """
    # txt = 'Board 1-2-3-4 denotes for Echoes-A, B, C, D respectively'
    # while cycle_id < cycle + 1:
    #     with open(address + 'cycle' + str(cycle_id) + '.csv') as outfile:
    #         table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    #     outfile.close()

    #     print (table.head().to_string())
    #     [row, column] = table.shape

    #     # avg = np.mean(table['data'], axis=1)  # average 64 captures
    #     avg = echoes_dsp.apply_bandpass_filter(table['data'], 300000, 1200000,
    #                                            51)  # apply bandpass

    #     x = np.arange(0, 1.38888889e-7 * row, 1.38888889e-7)
    #     plt.plot(x, avg, marker='-*', label='Board %s ' % str(cycle_id))
    #     # plt.title(' Me02 |' + ' Bandpass Enabled | No Noise removed')
    #     plt.title('Tuna Can | Negative-bipolar | Gain 0.55 | External Oscillator')
    #     plt.text(1, 1, txt)
    #     plt.xlim((0, 0.00005))
    #     plt.xlabel('time')
    #     plt.ylabel('amplitude')
    #     cycle_id += 1

    # plt.legend()
    # plt.show()


def check_data_quality():
    global cycle
    global cycle_id
    while cycle_id < cycle + 1:
        echoes_index = []
        list_file = display_list_of_file('cycle' + str(cycle_id) + '-')
        print (list_file)

        ''' Loop through every sample data in a read/capture '''
        for filename in list_file:
            with open(address + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float
            ''' DETECT a long streak in a sample '''
            if find_dup_run(data, primary_channel):
                print ("cycle : %s" % str( cycle_id + 1 ))
                with open(address + 'bad-flat.txt', 'ab') as writeout:
                    writeout.writelines(filename + '\n')
                writeout.close()

            ''' detect a time-shift in signal
                by checking differnce of 2nd echo position against average'''
            echo_idx = _locate_2ndEcho_index(data)
            echoes_index.append(echo_idx)

        ''' DETECT a time-shift in signal '''
        avg = _find_avg( echoes_index )
        print ('avg is: %s' % str(avg))
        for i, element in enumerate(echoes_index):
            if abs( element - avg ) > 2:
                print ("shift %s" % str(i + 1))
                with open(address + 'bad-shift.txt', 'ab') as writeout:
                    writeout.writelines(str(cycle_id) + '-' + str(i+1) + '\n')
                writeout.close()

        cycle_id += 1

    return

#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():
    global avgPos
    global avgNum
    global cycle
    global cycle_id
    global backgrd

    """
        (1) Check data quality: detect flat curve, missing echo
    """
    # check_data_quality()

    """
    (2) plot all 64 raw data in one cycle
    detect a bad read by visual inspection
    Generate a csv report with all raw captures
    """
    # rawRead_concat = pd.DataFrame()
    # while cycle_id < cycle + 1:

    #     oneRead,list_file = concat_all_data(tempC=False,
    #                                         search_key='cycle' + str(cycle_id) + '-')

    #     '''  generate all Raw data sets csv report
    #         Comment out the next 2 lines if don't use '''
    #     rawRead_concat = pd.concat([rawRead_concat, oneRead], axis=1)           # concat the avg data into dataframe

    #     '''  Plot all captures per read '''

    #     [row, column] = oneRead.shape
    #     dt = float(1/7200000)
    #     x = np.arange(0, 1.38888889e-7*row, 1.38888889e-7)

    #     plt.figure(2)
    #     plt.title('SoC vs Time | Bandpass Enabled')
    #     plt.interactive(False)

    #     avgPos = 2
    #     # while avgPos < column + 1:
    #     #     # y = echoes_dsp.apply_bandpass_filter(oneRead.loc[:, avgPos],
    #     #     #                                      300000, 1200000, 51)
    #     #     # change the integers inside this routine as (number of rows, number of columns, plotnumber)
    #     #     plt.plot(x, y, label='0%s ' % str(avgPos +1))
    #     #     plt.xlim((0, 0.00005))
    #     #     plt.xlabel('time')
    #     #     plt.ylabel('amplitude')
    #     #     avgPos += 1
    #     # plt.legend()
    #     # plt.show()

    #     cycle_id += 1
    
    # rawRead_concat = rawRead_concat.T
    # rawRead_concat.to_csv(address + 'allRawData-secondary.csv')


    """
    (3) plot avg of each cycle. Save avg (mean) to csv file
    """

    avgTable_concat = pd.DataFrame()

    plt.figure(1)
    plt.interactive(False)
    ped = 1.38888889e-1         #* 1000000
    while cycle_id < cycle + 1:


        cycle_id += 1
        oneRead, list_file = concat_all_data(tempC=False,
                                             search_key='cycle' + str(cycle_id) + '-')

        if not list_file:
            continue



        [row, column] = oneRead.shape
        print ("row %s col %s" % (str(row), str(column)))

        avg = np.mean(oneRead, axis=1)                                          # average 64 captures
        # avg = echoes_dsp.apply_bandpass_filter(avg, 300000, 2600000, 51)        # apply bandpass
        # avg = echoes_dsp.apply_lowpass_filter(avg, 2500000, 51)
        # avg = [a_i - b_i for a_i, b_i in zip( avg, backgrd )]                 # subtract background

        col_header = cycle_id
        avgTable = pd.DataFrame({col_header : avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)        # concat the avg data into dataframe

        x_1 = np.arange(0, ped * row, ped)
        ax1 = plt.subplot(212)
        ax1.margins(0.05)
        ax1.plot(x_1, avg, label='Cycle %s ' % str(cycle_id))
        plt.xlim((0, 40))
        plt.xlabel('time (us)')
        plt.ylabel('amplitude')
        plt.grid('on')
        ax1.set_title(battery_id + SoH + ' | Bandpass [0.3 - 2.6] Mhz')
        ax1.legend(loc='upper right')

        if primary_channel:
            x_2 = np.arange(79 * ped, 107 * ped, ped)                           # for gel
            avg_2 = avg[79: 108]
            # x_2 = np.arange(111 * ped, 136 * ped, ped)                        # for tape
            # avg_2 = avg[111: 136]

            ax2 = plt.subplot(221)
            ax2.margins()
            ax2.plot(x_2, avg_2)
            ax2.set_title('Echo 1')
            ax2.grid('on')

            x_3 = np.arange(127*ped, 160*ped, ped)                              # for gel
            avg_3 = avg[127 : 160]
            # x_3 = np.arange(215 * ped, 251 * ped, ped)                        # for tape
            # avg_3 = avg[215: 252]

            ax3 = plt.subplot(222)
            ax3.plot(x_3, avg_3)
            ax3.set_title('Echo 2')
            ax3.grid('on')

        else:

            x_4 = np.arange(144*ped, 187*ped, ped)
            avg_4 = avg[144 : 187]
            ax4 = plt.subplot(221)
            ax4.plot(x_4, avg_4, label='Cycle %s ' % str(cycle_id))
            ax4.grid('on')
            ax4.set_title(
                battery_id + SoH + ' | Transmission | Bandpass [0.3 - 2.6] Mhz')
        #     # plt.title(' TC06 |' + ' SoH = 72 | Bandpass Enabled | No Noise removed | secondary')

        # ''' -------   plot the avg for checking clean data    ---- '''
        # x_1 = np.arange(0, 1000000 *ped * row, 1000000*ped)
        # # x_1 = [1000000.0*ped for i in range(0, row)]                 #convert to micro-sec unit scale
        # plt.plot(x_1, avg,label='Capture 0%s ' % str(cycle_id))
        # # plt.title(' Hyundai batt  |' + ' Bandpass Enabled [0.3Mhz - 2.0Mhz] ')
        # # plt.title(' 16500 |Echo-A | Bandpass Enabled | Gain 0.65')
        # # plt.xlim((0, 0.00005))
        # plt.xlim(0,50)
        # plt.xlabel('time (usec)')
        # plt.ylabel('amplitude')
        # plt.grid('on')


    ## avgTable_concat = avgTable_concat.mean( axis =1 )                         # avg all cycle
    avgTable_concat = avgTable_concat.T
    avgTable_concat.to_csv(address + input_channel + '-raw-avg.csv')


    # plt.legend(loc="upper right")
    plt.show()


    return
#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

input_channel = 'secondary'
primary_channel = (input_channel == 'primary')
print (str(primary_channel))

battery_id  = 'TC19-'
SoH         = 'H78.1'
day         = '_181223'


address = '/media/kacao/Ultra-Fit/titan-echo-boards/Echo-A/' \
          + battery_id + SoH + day + '/' + input_channel + '/'


echoes_index = []
backgrd = []

avgPos  = 0  # number of capture in each cycle
avgNum  = 64
cycle   = 300
cycle_id = 0

ME = 4
ME_id = 1

# with open(address + 'background.dat') as my_file:
#     y_str = my_file.read()
#    y_str = y_str.splitlines()

#     for num in y_str:
#         backgrd.append(float(num))
# my_file.close()

echoes_dsp = echoes_signals( 7200000.0 )
if __name__ == '__main__':
    main()