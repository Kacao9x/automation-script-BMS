
import matplotlib.pyplot as plt
import numpy as np
import os, subprocess
import thLib as th
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

def concat_custom_data( key ):
    tC_1, tC_2 = [], []
    file_name = pd.DataFrame()
    list_file = display_list_of_file(key)
    print (list_file)
    for filename in list_file:

        my_file = open(address + filename)
        y_str = my_file.read()
        y_str = y_str.splitlines()

        data = []
        for i, num in enumerate(y_str):
            if i < len(y_str) - 1:
                data.append(float(num))

            else:
                # print (len(num.split() ))
                if len(num.split()) > 2:
                    tC_1.append( num.split()[1] )
                    tC_2.append( num.split()[2] )
                else:
                    data.append(float(num))
    # with 0s rather than NaNs
    file_name = file_name.fillna(0)

    return file_name, tC_2, tC_1


def concat_all_data(cycle, key):
    global bad_data, echoes_index
    echoes_index[:] = []
    file_name = pd.DataFrame()
    tC = []

    list_file = display_list_of_file('cycle'+str(cycle)+'-')
    # list_file = display_list_of_file(key + '-')
    print (list_file)
    for captureID, filename in enumerate( list_file ):

        my_file = open(address + filename)
        y_str = my_file.read()
        y_str = y_str.splitlines()
        data = []
        for i, num in enumerate(y_str):
            if i < len(y_str) -1 :
                data.append(float(num))

            else:
                # print (len(num.split() ))
                if len( num.split() ) > 2:
                    temp = num.rstrip().split('Temperature:')[1]
                    temp = temp.split('oC')[0]
                    tC.append(float(temp))
                else:
                    data.append(float(num))
        #===== end-loop to read data ===== #

        # concat all data set into a singl dataframe
        data_fr = pd.DataFrame(data)
        file_name = pd.concat([file_name, data_fr], axis=1,
                              ignore_index=True)

        # detect a a flat steak read
        # if find_dup_run( data ):
        #     print ("streak : %s" % str(captureID + 1))
        #     with open(address + 'bad-flat.txt', 'ab') as writeout:
        #         writeout.writelines( filename + '\n')
        #     writeout.close()
        #
        # # detect a time-shift signal
        # echo_idx = _locate_2ndEcho_index( data )
        # echoes_index. append( echo_idx )

    # with 0s rather than NaNs
    file_name = file_name.fillna(0)

    return file_name, tC

def _save_avg_data(num, y):
    fn = "avg/" + 'cycle' + str(num) + "-echoes-d.dat"
    filehandle = open(fn, "w")
    for samp in y:
        filehandle.write(str(samp) + "\n")
    filehandle.close()
    return


def _find_avg( numbers ):
    return (sum(numbers)) / max(len(numbers), 1)

#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():
    global avgPos
    global avgNum
    global cycle
    global cycle_id
    #cycle number to plot

    """
    plot a single data RAW data set
    """
    # while avgPos < avgNum + 1:
    #     testResults, tC = concat_all_data(cycle_id, 'raw-' + str(avgPos))
    #     [row, column] = testResults.shape
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
    #         plt.plot(x, testResults.loc[:, i - 1])
    #         plt.xlim((0, 0.00005))
    #         plt.xlabel('time')
    #         plt.ylabel('amplitude')
    #         i += 10
    #
    #     plt.legend()
    #     plt.show()
    #     del tC, testResults

    """
    plot all 64 raw data in one cycle
    detect a bad read by visual inspection
    """
    # while cycle_id < cycle + 1:
    #
    #     testResults, tC = concat_all_data(cycle_id, 'raw')
    #     avg = _find_avg( echoes_index )
    #     for i, element in enumerate(echoes_index):
    #         if abs( element - avg ) > 2:
    #             print ("shift %s" % str(i))
    #             with open(address + 'bad-shift.txt', 'ab') as writeout:
    #                 writeout.writelines(str(cycle_id) + '-' + str(i) + '\n')
    #             writeout.close()
    #
    #     cycle_id += 1
    #
    #     print (testResults.shape)
    #     [row, column] = testResults.shape
    #
    #     dt = float(1/7200000)
    #     x = np.arange(0, 1.38888889e-7*row, 1.38888889e-7)
    #
    #     plt.figure(2)
    #     plt.title('SoC vs Time')
    #     plt.interactive(False)
    #
    #     avgPos = 1
    #     while avgPos < column:
    #         # change the integers inside this routine as (number of rows, number of columns, plotnumber)
    #         plt.plot(x,testResults.loc[:, avgPos])
    #         plt.xlim((0, 0.00005))
    #         plt.xlabel('time')
    #         plt.ylabel('amplitude')
    #         avgPos += 1
    #     plt.legend()
    #     plt.show()



    """
    plot avg of each cycle. Save avg (mean) to csv file
    """
    avgTable_concat = pd.DataFrame()

    plt.figure(3)
    plt.interactive(False)
    # black_list = list( range(138, 147))
    # black_list.append( 83 )
    # print (black_list)

    while cycle_id < cycle + 1:
        if cycle_id == 467:
            cycle_id +=1
        # if (cycle_id == ele for ele in black_list):
        #     continue
        # plt.subplot(5, 2, i) #change the integers inside this routine as (number of rows, number of columns, plotnumber)
        testResults, tC = concat_all_data( cycle_id, 'raw')
        [row, column] = testResults.shape
        temp = testResults.iloc[:, 0:(cycle_id * avgNum)]

        avg1 = np.mean(temp, axis=1)
        col_header = cycle_id
        avgTable = pd.DataFrame({col_header : avg1})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)

        x = np.arange(0, 1.38888889e-7 * row, 1.38888889e-7)
        plt.plot(x, avg1, label='Cycle %s ' % str(cycle_id))
        plt.title('SoC vs Time for average data |' + ' TC03')
        plt.xlim((0, 0.00005))
        plt.xlabel('time')
        plt.ylabel('amplitude')
        tC.append(avg1[round(0.0000295 * 7200000)])
        cycle_id += 1

    avgTable_concat.to_csv(address + 'avgData-secondary.csv')
    plt.legend()
    plt.show()

    """
    Plot Temperature vs Amplitude at 30us
    """
    # concat temperature
    # tempTable = pd.DataFrame()
    # testResults, tC_1, tC_2 = concat_custom_data('cycle')
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
    Temperature Plot
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

#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
address = '/media/jean/Data/titan-echo-board/180928-TC03-H-echo-d/data/secondary/'
bad_data = []
echoes_index = []

avgPos = 1  # number of capture in each cycle
avgNum = 64
cycle = 500
cycle_id = 1
# cycle number to plot

if __name__ == '__main__':
    main()