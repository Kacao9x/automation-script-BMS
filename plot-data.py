import matplotlib.pyplot as plt
import numpy as np
import subprocess
# import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *
from lib.echoes_database import *
from bson import ObjectId


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
        # print (list_file)
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
        # print (list_file)
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



def _unsued_method():
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
    
    def find_dup_run( x, isPrimary ):
        # return max(x) == min(x)   # for echo C + D
        max_value = max( x )
        min_value = min( x )

        if isPrimary:
            return max_value - min_value < 0.4
        else:
            return ( max_value - min_value < 0.015 or
                    max_value - min_value > 0.5 )                                   # for echo B


    def _locate_2ndEcho_index( data ):
        data = data[ 140 : 260 ]
        return 140 + data.index( max(data) )

    def _locate_1stEcho_index( data ):
        '''
        For checking Mercedes data
        '''
        data = data[ 108: 131 ]
        return 108 + data.index( max(data))

    def _find_avg( numbers ):
        return (sum(numbers)) / max(len(numbers), 1)


    global cycle
    global cycle_id
    while cycle_id < cycle + 1:
        print ('capture: {}'.format(cycle_id))
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
                print ("cycle : {}".format( cycle_id + 1 ))
                with open(address + 'bad-flat.txt', 'ab') as writeout:
                    writeout.writelines(filename + '\n')
                writeout.close()

            ''' detect a time-shift in signal
                by checking differnce of 2nd echo position against average'''
            # echo_idx = _locate_2ndEcho_index(data)
            echo_idx = _locate_1stEcho_index(data)
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

def check_signal_plot(bandpass=False, backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    global cycle
    global cycle_id
    avgTable_concat = pd.DataFrame()

    plt.figure(1)
    plt.interactive(False)
    ped = 1.38888889e-1         #* 1000000
    while cycle_id < cycle + 1:

        cycle_id += 1
        oneRead, list_file = concat_all_data(tempC=False,
                                             search_key='cycle' + str(cycle_id) + '-')
        # oneRead, list_file = concat_all_data(tempC=False,
        #                                      search_key='echo-primary-v' + str(cycle_id))
        
        if not list_file:
            continue


        [row, column] = oneRead.shape
        print ("capture: {}, row {} col {}".format(str(cycle_id), str(row), str(column)))

        avg = np.mean(oneRead, axis=1)                                          # average 64 captures
        
        if bandpass:
            avg = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)      # apply bandpass
            # avg = echoes_dsp.apply_lowpass_filter(avg, 2500000, 51)

        if backgrd_subtract:
            avg = [a_i - b_i for a_i, b_i in zip( avg, backgrd )]                 # subtract background

        col_header = cycle_id
        avgTable = pd.DataFrame({col_header : avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)        # concat the avg data into dataframe

        x_1 = np.arange(0, ped * row, ped)
        ax1 = plt.subplot(212)
        ax1.margins(0.05)
        ax1.plot(x_1, avg, label='Cycle %s ' % str(cycle_id))
        plt.xlim((0, 50))
        plt.xlabel('time (us)')
        plt.ylabel('amplitude')
        plt.grid('on')
        ax1.set_title('ME06 - H98 | Bandpass 0.3M - 1.2Mhz | gain 0.55')
        ax1.legend(loc='upper right')
        
        if primary_channel:
            x_2 = np.arange(108 * ped, 144 * ped, ped)                           # for gel
            avg_2 = avg[108: 144]
            
        
            ax2 = plt.subplot(221)
            ax2.margins()
            ax2.plot(x_2, avg_2)
            ax2.set_title('Echo 1')
            ax2.grid('on')
        
            x_3 = np.arange(208*ped, 252*ped, ped)                              # for gel
            avg_3 = avg[208 : 252]
            
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
            ax4.set_title(battery_id + SoH + ' | Transmission | Raw-data')

        ''' -------   plot the avg for checking clean data    ---- '''
        # print ("{:.1f}".format(float(22/10)))
        # x_1 = np.arange(0, ped * row, ped)
        # # x_1 = [1000000.0*ped for i in range(0, row)]                 #convert to micro-sec unit scale
        # plt.plot(x_1, avg,label='Cycle {:.1f}'.format(cycle_id))
        # plt.title(' ME06 | bandpass [0.3 - 1.2] Mhz | Gain 0.55')
        # # plt.xlim((0, 0.00005))
        # plt.xlim(0,50)
        # plt.xlabel('time (usec)')
        # plt.ylabel('amplitude')
        # plt.grid('on')
        # plt.legend(loc='upper right')


    ## avgTable_concat = avgTable_concat.mean( axis =1 )                         # avg all cycle
    avgTable_concat = avgTable_concat.T
    avgTable_concat.to_csv(address + input_channel + '-raw-avg-1.csv')


    # plt.legend(loc="upper right")
    plt.show()
    return


def check_data_quality_mongo():
    def find_dup_run(x, isPrimary):
        # return max(x) == min(x)   # for echo C + D
        max_value = max(x)
        min_value = min(x)

        if isPrimary:
            return max_value - min_value < 0.4
        else:
            return (max_value - min_value < 0.015 or
                    max_value - min_value > 0.5)  # for echo B

    def _locate_2ndEcho_index(data):
        data = data[140: 260]
        return 140 + data.index(max(data))

    def _locate_1stEcho_index( data ):
        '''
        For checking Mercedes data
        '''
        data = data[ 108: 131 ]
        return 108 + data.index( max(data))


    def _find_avg(numbers):
        return (sum(numbers)) / max(len(numbers), 1)

    echoes_db = database(database='echoes-captures')

    query = {
        'capture_number': {
            '$lt': 1500
        },
        'test_setting.captureAdc' : 0
    }
    projection = {
        'raw_data': 1,
        '_id': 1,
    }
    data_cursor = echoes_db.search(query=query, projection=projection,
                              collection="Me06")

    count = 0
    for oneCapture in data_cursor:
        count += 1
        echoes_index = []
        print(len(oneCapture['raw_data']))

        sample = 0
        dup = []
        while sample < len(oneCapture['raw_data']):
            primary_channel = True
            
            if find_dup_run(oneCapture['raw_data'][sample], primary_channel):
                dup.append(sample)

            echo_idx = _locate_1stEcho_index(oneCapture['raw_data'][sample])
            echoes_index.append(echo_idx)
            sample += 1

        ''' DETECT a time-shift in signal '''
        avg = _find_avg( echoes_index )
        print ('avg is: %s' % str(avg))
        for i, element in enumerate(echoes_index):
            if abs( element - avg ) > 2:
                print ("capture shift: {} - {}".format(str(count),str(i + 1)))
            

        print("duplicate {}".format(dup))
        print ("capture ID: {}".format(count))



    echoes_db.close()
    # global cycle
    # global cycle_id
    # while cycle_id < cycle + 1:
    #     echoes_index = []
    #     list_file = display_list_of_file('cycle' + str(cycle_id) + '-')
    #     print(list_file)
    #
    #     ''' Loop through every sample data in a read/capture '''
    #     for filename in list_file:
    #         with open(address + filename) as my_file:
    #             y_str = my_file.read()
    #             y_str = y_str.splitlines()
    #         my_file.close()
    #
    #         data = [float(num) for num in y_str]  # convert string to float
    #         ''' DETECT a long streak in a sample '''
    #         if find_dup_run(data, primary_channel):
    #             print("cycle : %s" % str(cycle_id + 1))
    #             with open(address + 'bad-flat.txt', 'ab') as writeout:
    #                 writeout.writelines(filename + '\n')
    #             writeout.close()
    #
    #         ''' detect a time-shift in signal
    #             by checking differnce of 2nd echo position against average'''
    #         echo_idx = _locate_2ndEcho_index(data)
    #         echoes_index.append(echo_idx)
    #
    #     ''' DETECT a time-shift in signal '''
    #     avg = _find_avg(echoes_index)
    #     print('avg is: %s' % str(avg))
    #     for i, element in enumerate(echoes_index):
    #         if abs(element - avg) > 2:
    #             print("shift %s" % str(i + 1))
    #             with open(address + 'bad-shift.txt', 'ab') as writeout:
    #                 writeout.writelines(str(cycle_id) + '-' + str(i + 1) + '\n')
    #             writeout.close()
    #
    #     cycle_id += 1

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
    (2) plot avg of each capture. Save avg (mean) to csv file
    """
    # check_signal_plot(bandpass = True, backgrd_subtract = False)

    """
    (3) Check quality each capture. Query data from mongodb
    """
    check_data_quality_mongo()
    """
    (4) Plot all 64 samplings in a capture. Query data from Mongodb
    """
    # echoes_db = database(database='echoes-captures')

    # query = {}
    # projection={
    #     'raw_data':1
    #     # 'temperature':1,
    #     # 'echoes_setting':1
    # }
    # data = echoes_db.search(query=query,projection=projection,
    #                                  collection="Me06")


    # sample = 0
    # print (len(data['raw_data'][0]))
    # while sample < len(data['raw_data']):
    #     dt = 1.38888E-7#float(1/7200000)
    #     row = 512
    #     x = np.arange(0, dt * row, dt)
    #     filter_data = echoes_dsp.apply_bandpass_filter(data['raw_data'][sample],
    #                                            100000, 1000000, 51)
    #     plt.figure(1)
    #     plt.title('Signal Plot')
    #     plt.interactive(False)
    #     # plt.plot(x, data['raw_data'][sample])
    #     plt.plot(x, data['raw_data'][sample], label='Sample 0{} '.format( str(sample +1)))
    #     plt.grid('on')
    #     plt.legend(loc='upper right')

    #     sample += 1
    # plt.show()

    # echoes_db.close()





    return
#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

input_channel = 'primary'
primary_channel = (input_channel == 'primary')
print (str(primary_channel))

battery_id  = 'TC02-'
SoH         = 'H77.23'
day         = '_190123'


address = '/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/ME06/primary/'
echoes_index = []
backgrd = []

avgPos  = 0  # number of capture in each cycle
avgNum  = 64
cycle   = 500
cycle_id = 0

ME = 4
ME_id = 1

# with open(address + 'background.dat') as my_file:
#     y_str = my_file.read()
#     y_str = y_str.splitlines()
#
#     for num in y_str:
#         backgrd.append(float(num))
# my_file.close()


echoes_dsp = echoes_signals( 7200000.0 )
if __name__ == '__main__':
    main()