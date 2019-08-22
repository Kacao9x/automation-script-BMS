import matplotlib.pyplot as plt
import numpy as np
import subprocess
from pathlib import Path

# import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *
from lib.echoes_database import *

import json
from lib.commandline import *
from datetime import datetime,timedelta


def remove_bad_samples(aCapture_signal):
    # These constants are sensitive to VGA change. VGA default is 0.55
    START_DATA_PTS = 58                                                         # evaluate signal after 8us
    HIGH_BOUND = 0.2                                                            # arbitrary value for Toyota cell
    LOW_BOUND = 0.09

    idx = []
    for i, sample in enumerate(aCapture_signal):
        # x_arr = np.absolute(signal)                                           #compare standard deviation with threshold

        std_value = np.std(sample[START_DATA_PTS:], ddof=1)
        # print ('std val: {}'.format(std_value))
        if std_value > HIGH_BOUND or std_value < LOW_BOUND:
            idx.append(i)
        else:
            None

    print("bad sampling {}".format(idx))

    aCapture_signal = np.delete(aCapture_signal, idx,
                                axis=0).tolist()  # delete bad sampling by index

    return aCapture_signal


def plot_signal_from_json(remove_bad_samp=False, bandpass=False,
                          backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    avgTable_concat = pd.DataFrame()
    filter_concat = pd.DataFrame()

    ped = 1.38888889e-1  # microsec, * 1000000

    key = '*.json'
    # list_file = display_list_of_file(address, key)

    list_file = sort_folder_by_name_universal(address, key)
    print(list_file)

    tempC_1, tempC_2 = [], []
    for oneFile in list_file:

        strip_name = oneFile.split('-')
        captureID = (strip_name[0].split('capture'))[1]

        # str = (oneFile.split('_'))[0]
        # captureID = str.split('cycle')[1]
        print('capture ID: {}'.format(captureID))

        addr = os.path.join(address, oneFile)
        addr = Path(addr)
        print('adddr {}'.format(addr))

        with open(addr) as json_file:
        # with open(address + oneFile) as json_file:
            echo_data = json.load(json_file)
        json_file.close()

        ''' Read temperature'''
        # tempC_1.append(echo_data['temperature'][0])
        # tempC_2.append(echo_data['temperature'][1])

        if 'master' in echo_data['test_setting']:
            if echo_data['test_setting']['master'] != False:
                tempC_1.append(
                    echo_data["test_setting"]["master"]["temp_sense_a_1"])
            else:
                tempC_1.append(None)
        elif 'temperature' in echo_data:
            tempC_1.append(echo_data['temperature'][0])
            tempC_2.append(echo_data['temperature'][1])
        else:
            tempC_1.append(None)

        if echo_data['raw_data']:
            echo_data['raw_data'] = [i for i in echo_data['raw_data'] if
                                     i != None]
            if remove_bad_samp:
                echo_data['raw_data'] = remove_bad_samples(
                    echo_data['raw_data'])

            raw_set_pd = pd.DataFrame()
            for idx, raw in enumerate(echo_data['raw_data']):
                single_set = pd.DataFrame(
                    {idx: raw})  # concat all data set into a singl dataframe
                raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
                                       ignore_index=True)

            [row, column] = raw_set_pd.shape

            avg = np.mean(raw_set_pd, axis=1)  # average 64 captures
            if bandpass:
                avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000,
                                                                1200000,
                                                                51)  # apply bandpass

            if backgrd_subtract:
                avg = [a_i - b_i for a_i, b_i in zip(avg, backgrd)]

            # if normalize:

            ''' -------   plot the avg for checking clean data    ---- '''
            # plt.subplot(211)
            x_1 = np.arange(0, ped * row, ped)
            # x_1 = [1000000.0*ped for i in range(0, row)]                        #convert to micro-sec unit scale
            plt.title(plot_title)
            plt.plot(x_1, avg_bandpass,
                     label='capture 0{}'.format(int(captureID)))
            plt.xlim(0, 70)
            plt.grid('on')
            plt.legend(loc='upper right')

            # plt.show() # plot an individual signal
        else:
            print('no raw_data')
            avg = []
            avg_bandpass = []

        # Save all average data into Dataframe
        avgTable = pd.DataFrame({captureID: avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)

        avg_filter = pd.DataFrame({captureID: avg_bandpass})
        filter_concat = pd.concat([filter_concat, avg_filter], axis=1)

    plt.interactive(False)
    # plt.savefig(address + 'channel-B-798.png', dpi = 500)
    plt.show()

    ''' Save Processed Data to csv '''
    # avgTable_concat = avgTable_concat.mean( axis =1 )
    avgTable_concat = avgTable_concat.T

    avgTable_concat.insert(loc=0, column='tempC_1', value=tempC_1)
    # avgTable_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    avgTable_concat.to_csv(address + input_channel + '-raw-avg-sec.csv')

    # filter_concat = filter_concat.mean( axis=1 )
    filter_concat = filter_concat.T
    filter_concat.insert(loc=0, column='tempC_1', value=tempC_1)
    # filter_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    filter_concat.to_csv(address + input_channel + '-bandpass-avg.csv')
    # avgTable_concat.to_csv(address + input_channel + '-raw-avg-9-channel-A.csv')

    print("complete")
    return


#==============================================================================#
#======================== MAIN FUNCTION =======================================#
def main ():

    plot_signal_from_json(remove_bad_samp=False, bandpass=True, backgrd_subtract= False)
    # plot_signal_from_mongo(collection=collection)

    return
#==============================================================================#


input_channel       = 'secondary'
input_chn   = 1 if input_channel == 'primary' else 2
plot_title  = ' Lenovo_01 - primary| bandpass [0.3 - 1.2] Mhz | Gain 0.55 | 2019 Aug 11th'


# dtb         = 'cycler-data'
# collection  = 'Me09'

addr_to_extract = '/media/kacao/Ultra-Fit/titan-echo-boards/Lenovo/Lenovo_1/primary_1/'
address     = r'/media/kacao/Ultra-Fit/titan-echo-boards/Lenovo/190718/{}/'.format(input_channel)
backgrd = []


echoes_dsp = echoes_signals( 7200000.0 )
if __name__ == '__main__':
    main()