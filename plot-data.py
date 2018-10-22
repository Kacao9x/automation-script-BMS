
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
    return data.index( max(data) )


def find_timeshift_signal( ):

    return


def concat_all_data(tempC = bool, search_key = str):
    '''
    :param cycle: keyword number to search and sort out
    :param tempC: True to read the temperature files, False otherwise
    :return: a dataframe contains all avg capture in a custom format
            an array of all data sets
    '''
    big_set = pd.DataFrame()

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

        for captureID, filename in enumerate(list_file):

            with open(address + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float
            # data = []
            # for i, num in enumerate(y_str):
            #     data.append(float(num))

            # concat all data set into a singl dataframe
            single_set = pd.DataFrame({captureID: data})
            big_set = pd.concat([big_set, single_set], axis=1,
                                ignore_index=True)
            del data

        # with 0s rather than NaNs
        big_set = big_set.fillna(0)

        return big_set, list_file


# def concat_all_data(cycle, key):
#     global echoes_index
#     echoes_index[:] = []
#     big_set = pd.DataFrame()
#
#     list_file = display_list_of_file('cycle' + str(cycle) + '-')
#     # list_file = display_list_of_file(key + '-')
#     # print (list_file)
#     for captureID, filename in enumerate( list_file ):
#         # if captureID == 0:
#         #     with open(address + 'bad.txt', 'ab') as writeout:
#         #         writeout.writelines( filename + '\n')
#         #     writeout.close()
#
#         with open(address + filename) as my_file:
#             y_str = my_file.read()
#             y_str = y_str.splitlines()
#         my_file.close()
#
#         data = []
#         for i, num in enumerate(y_str):
#             data.append(float(num))
#
#         #===== end-loop to read data ===== #
#
#         ''' remove background noise from the signal '''
#         # data = [a_i - b_i for a_i, b_i in zip(data, backgrd)]
#
#         # concat all data set into a singl dataframe
#         single_set = pd.DataFrame({captureID: data})
#         big_set = pd.concat([big_set, single_set], axis=1, ignore_index=True)
#
#         ''' detect a long streak in a read '''
#         # if find_dup_run( data ):
#         #     print ("streak : %s" % str(captureID + 1))
#         #     with open(address + 'bad-flat.txt', 'ab') as writeout:
#         #         writeout.writelines( filename + '\n')
#         #     writeout.close()
#         #
#         ''' detect a time-shift in signal '''
#         # echo_idx = _locate_2ndEcho_index( data )
#         # echoes_index. append( echo_idx )
#
#     # with 0s rather than NaNs
#     big_set = big_set.fillna(0)
#
#     return big_set, list_file


def _find_avg( numbers ):
    return (sum(numbers)) / max(len(numbers), 1)

def Diff(li1, li2):
    return (list(set(li1) - set(li2)))

#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():
    global avgPos
    global avgNum
    global cycle
    global cycle_id
    global backgrd

    """
    (1) plot a single data RAW data set
    """
    # while avgPos < avgNum + 1:
    #     oneRead = concat_all_data(cycle_id, 'raw-' + str(avgPos))
    #     [row, column] = oneRead.shape
    #     avgPos += 1
    #     dt = float(1 / 7200000)
    #     x = np.arange(0, 1.38888889e-7 * row, 1.38888889e-7)
    #
    #     plt.figure(1)
    #     plt.title('SoC vs Time')
    #     plt.interactive(False)
    #
    #     i = 1
    #     while (i < column+1):
    #     # plt.subplot(column/2, 2, i)
    #     # change the integers inside this routine as (number of rows, number of columns, plotnumber)
    #         plt.plot(x, oneRead.loc[:, i - 1])
    #         plt.xlim((0, 0.00010))
    #         plt.xlabel('time')
    #         plt.ylabel('amplitude')
    #         i += 10
    #
    #     plt.legend()
    #     plt.show()
    #     del tC, oneRead

    """
    (2) plot all 64 raw data in one cycle
    detect a bad read by visual inspection
    Generate a csv report with all raw captures
    """
    rawRead_concat = pd.DataFrame()
    list_file_total = []
    while cycle_id < cycle + 1:

        oneRead,list_file = concat_all_data(tempC=False,
                                            search_key='cycle' + str(cycle_id) + '-')
    #     ''' detect a time-shift in signal '''
    #     # avg = _find_avg( echoes_index )
    #     # for i, element in enumerate(echoes_index):
    #     #     if abs( element - avg ) > 1:
    #     #         print ("shift %s" % str(i))
    #     #         with open(address + 'bad-shift.txt', 'ab') as writeout:
    #     #             writeout.writelines(str(cycle_id) + '-' + str(i) + '\n')
    #     #         writeout.close()
    #
        '''  generate all Raw data sets csv report
            Comment out the next 2 lines if don't use '''
        rawRead_concat = pd.concat([rawRead_concat, oneRead], axis=1)           # concat the avg data into dataframe

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

        cycle_id += 1

    rawRead_concat = rawRead_concat.T
    rawRead_concat.to_csv(address + 'allRawData.csv')


    """
    (3) plot avg of each cycle. Save avg (mean) to csv file
    """
    # avgTable_concat = pd.DataFrame()
    #
    # plt.figure(3)
    # plt.interactive(False)
    #
    # while cycle_id < cycle + 1:
    #     # if cycle_id == 39:
    #     #     cycle_id +=25
    #
    #     oneRead, list_file = concat_all_data(tempC=False,
    #                                          key='cycle' + str(cycle_id) + '-')
    #     [row, column] = oneRead.shape
    #
    #     # temp = oneRead.iloc[:, 0:(cycle_id * avgNum)]                     #
    #     avg = np.mean(oneRead, axis=1)                                          # average 64 captures
    #     # avg = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)        # apply bandpass
    #
    #     col_header = cycle_id
    #     avgTable = pd.DataFrame({col_header : avg})
    #     avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)        # concat the avg data into dataframe
    #
    #     x = np.arange(0, 1.38888889e-7 * row, 1.38888889e-7)
    #     plt.plot(x, avg, label='Cycle %s ' % str(cycle_id))
    #     plt.title('SoC vs Time for average data |' + ' Me01 S0H = 100 | echo-E')
    #     plt.xlim((0, 0.00005))
    #     plt.xlabel('time')
    #     plt.ylabel('amplitude')
    #     cycle_id += 1
    #
    # avgTable_concat.to_csv(address + 'avgData-bandpass.csv')
    # plt.legend()
    # plt.show()

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
    # with open(address + 'temp.csv') as outfile:
    #     tempTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()

    # calculate the value at 30ns
    # cyc, temp_value = [], []
    # while cycle_id < cycle + 1:
    #     cyc.append(cycle_id)
    #     temp_value.append(tempTable['Temperature_top'][ cycle_id - 1])
    #     cycle_id += 1
    #
    # plt.figure(5)
    # plt.scatter(cyc, temp_value)
    # plt.title('Temperature vs Cycle | SOC = 0%')
    # plt.xlabel('Cycle')
    # plt.interactive(False)
    # plt.show()

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


    return
#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
address = '/media/jean/Data/titan-echo-board/echo-E/Me01-H100_181015-echo-e/data/primary/'
echoes_index = []
backgrd = []

avgPos = 0  # number of capture in each cycle
avgNum = 64
cycle = 99
cycle_id = 1

ME = 4
ME_id = 1

# with open(address + 'noise.dat') as my_file:
#     y_str = my_file.read()
#     y_str = y_str.splitlines()
#
#     for num in y_str:
#         backgrd.append(float(num))
#
# my_file.close()

echoes_dsp = echoes_signals( 7200000.0 )
if __name__ == '__main__':
    main()