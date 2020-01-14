import matplotlib.pyplot as plt
import numpy as np
import subprocess

# import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *
from lib.echoes_database import *
from bson import ObjectId
from bson import json_util
import json
from lib.commandline import *
from pathlib import *



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

            with open(addr + filename) as my_file:
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

            with open(addr + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float

            single_set = pd.DataFrame({captureID: data})                        # concat all data set into a singl dataframe
            big_set = pd.concat([big_set, single_set], axis=1,
                                ignore_index=True)

        big_set = big_set.fillna(0)                                             # with 0s rather than NaNs

        return big_set, list_file


def isBadSample(aSample_signal):
    # These constants are sensitive to VGA change. VGA default is 0.55
    START_DATA_PTS = 58  # evaluate signal after 8us
    HIGH_BOUND = 0.12  # arbitrary value for Toyota cell
    LOW_BOUND = 0.04


    std_value = np.std(aSample_signal[START_DATA_PTS:], ddof=1)
    print ('std val: {}'.format(std_value))
    if std_value > HIGH_BOUND or std_value < LOW_BOUND:
        return True
    else:
        return False

def convert_time(timest):
    time_pcs = timest.split('-')
    # datetime.strptime(aCapture['timestamp'], '%Y-%m-%dT%H:%M:%S')

    return '{}-{}-{}T{}:{}:{}'.format(time_pcs[3],time_pcs[4],time_pcs[5],
                                      time_pcs[6],time_pcs[7],time_pcs[8])


def grasp_tempC(cycle_id):
    tempC = []
    # tempc_file = display_list_of_file(addr + 'tempC/',
    #                                   'cycle{}-'.format(cycle_id))

    key         = 'cycle{}-*.dat'.format(cycle_id)
    tempc_file = sort_folder_by_name_universal(path=addr/'tempC', key=key)


    if tempc_file:
        for file in tempc_file:
            print ('tempC file: {}'.format(file))
            with open(str(file)) as my_file:
                y_str = my_file.read()
            my_file.close()

            print (y_str)
            y_split = y_str.split()
            tempC.append(float(y_split[1]))
            tempC.append(float(y_split[2]))

    return tempC


def convert_dat_to_json():
    global cycle
    global cycle_id
    while cycle_id < cycle + 1:
        print ('capture: {}'.format(cycle_id))

        tempC = grasp_tempC(cycle_id)

        # list_file_signal = display_list_of_file(address, 'cycle{}-'.format(cycle_id))
        key = 'cycle{}-*.dat'.format(cycle_id)
        list_file_signal = sort_folder_by_name_universal(addr / sub_addr, key)

        if list_file_signal:
            aCapture = {}
            raw_data = []
            ''' Loop through every sample data in a read/capture '''
            for filename in list_file_signal:
                print ('filename {}'.format(filename))
                with open(str(filename)) as my_file:
                    y_str = my_file.read()
                    y_str = y_str.splitlines()
                my_file.close()

                data = [float(num) for num in y_str]  # convert string to float
                ''' DETECT a flat curve in a sample '''
                if isBadSample(data):
                    print ("cycle : {}".format(cycle_id))
                    print ('bad sample: {}'.format(filename))
                    # with open(addr/sub_addr/'bad-flat.txt', 'ab', encoding='utf-8') as writeout:
                    #     writeout.writelines(filename + '\n')
                    # writeout.close()

                raw_data.append(data)

            aCapture['raw_data']        = raw_data
            aCapture['input_side']   = 1 if 'primary' in input_side else 2
            aCapture['source'] = 'echoes-a'
            aCapture['test_setting']    = {
                'voltage_rails' : 85,
                'impulse'       : 'neg-bipolar',
                'gain'          : 0.55,
            }
            aCapture['timestamp']       = convert_time( list_file_signal[0].name )
            aCapture['capture_number']  = cycle_id
            aCapture['temperature']     = tempC
            aCapture['source']          = '{}-{}'.format(list_file_signal[0].name.split('-')[9],
                                                         list_file_signal[0].name.split('-')[10].split('.')[0])

            jsonName = '{}_json/capture{}_{}.json'.format(input_side, cycle_id,
                                                     aCapture['timestamp'])
            pathname = addr/Path(jsonName)
            print (pathname)
            # pathname.touch()
            # pathname.write_text('write')
            with open(str(pathname), 'w') as writeout:
                writeout.write(json.dumps(aCapture))
            writeout.close()

        cycle_id += 1


    return


def check_data_quality():
    """
    This functions detect bad sampling in a capture.
    The first method detect a flat curve
    Second method detect a time shift more than 2 data points
    """
    # These constants are sensitive to VGA change. VGA default is 0.55

    PRIMARY_AMP_RANGE = 0.4
    SECONDARY_AMP_RANGE_LOW = 0.015
    SECONDARY_AMP_RANGE_HIGH = 0.5
    def find_dup_run(x, isPrimary):
        if x != None:
            max_value = max(x)
            min_value = min(x)

        if isPrimary:
            return max_value - min_value < PRIMARY_AMP_RANGE
        else:
            return (max_value - min_value < SECONDARY_AMP_RANGE_LOW or
                    max_value - min_value > SECONDARY_AMP_RANGE_HIGH)                                   # for echo B


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
        # list_file = display_list_of_file('cycle' + str(cycle_id) + '-')
        list_file = sort_folder_by_name_universal('cycle' + str(cycle_id) + '-')
        print (list_file)

        ''' Loop through every sample data in a read/capture '''
        for filename in list_file:
            with open(addr + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float
            ''' DETECT a flat curve in a sample '''
            if find_dup_run(data, primary_side):
                print ("cycle : {}".format( cycle_id + 1 ))
                with open(addr + 'bad-flat.txt', 'ab') as writeout:
                    writeout.writelines(filename + '\n')
                writeout.close()

            ''' DETECT a time-shift in signal
                by checking differnce of 1st/2nd echo position against average'''
            # echo_idx = _locate_2ndEcho_index(data)
            echo_idx = _locate_1stEcho_index(data)
            echoes_index.append(echo_idx)

        ''' DETECT a time-shift in signal '''
        avg = _find_avg( echoes_index )
        print ('avg is: %s' % str(avg))
        for i, element in enumerate(echoes_index):
            if abs( element - avg ) > 2:
                print ("shift %s" % str(i + 1))
                with open(addr + 'bad-shift.txt', 'ab') as writeout:
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
        
        if primary_side:
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
    avgTable_concat.to_csv(addr + input_side + '-raw-avg-1.csv')


    # plt.legend(loc="upper right")
    plt.show()
    return



def plot_v1v2_from_json():
    with open(addr + input_side + '-bandpass-avg-channel-A-sec.csv') as outfile:
        tempTable_A = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    # print (tempTable_A.head().to_string())
    print (tempTable_A.at[3,'index'])
    signal = list(tempTable_A.iloc[0, -512:].values)
    print (signal[-1])

    ped = 1.38888889e-1
    x_1 = np.arange(0, ped * 512, ped)
    for row in range (0, 22):
        signal = list(tempTable_A.iloc[row, -512:].values)
        
        if row < 11:
            print (row)
            plt.subplot(211)
            plt.title(' Acrylic - channel-A-secondary | R = 0 - 100 | bandpass [0.3 - 1.2] Mhz | Gain 0.55')
            plt.plot(x_1, signal,label='Ohm {}0'.format(int(tempTable_A.at[row,'index'])))
            plt.xlim(0,70)
            plt.grid('on')
            plt.legend(loc='upper right')

        else:
            print ('row-B: {}'.format(row))
            plt.subplot(212)
            plt.title(' Acrylic - channel-B-secondary | R = 0 - 100 | bandpass [0.3 - 1.2] Mhz | Gain 0.55')
            plt.plot(x_1, signal,label='Ohm {}0'.format(int(tempTable_A.at[row,'index'])))
            plt.xlim(0,70)
            plt.grid('on')
            plt.legend(loc='upper right')

    plt.interactive(False)
    # plt.savefig(address + 'channel-B-798.png', dpi = 500)
    plt.show()

    return
#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():

    """
        (1) Check data quality: detect flat curve, missing echo
    """
    # check_data_quality()
    # check_data_quality_json()
    convert_dat_to_json()

    """
    (2) plot avg of each capture. Save avg (mean) to csv file
    """
    # check_signal_plot(bandpass = True, backgrd_subtract = False)
    # plot_signal_from_json(bandpass=True, backgrd_subtract= False)
    # plot_v1v2_from_json()


    return
#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

input_side = 'primary'
primary_side = (input_side == 'primary')
print (str(primary_side))

battery_id  = 'Me05'
SoH         = 'H77.23'
day         = '_190123'

# addr    = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/{}-190227'.format(battery_id))
addr = Path('/home/kacao/TitanAES/Python-scripts/data/result.json')
sub_addr= input_side

echoes_index = []
backgrd = []

avgPos  = 0  # number of capture in each cycle
avgNum  = 64
cycle   = 800
cycle_id = 1

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