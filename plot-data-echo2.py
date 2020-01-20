import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import sys, timeit


# import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *
from lib.echoes_models import *
from lib.echoes_database import *

import json
from lib.commandline import *
from datetime import datetime,timedelta
from scipy.fftpack import fft, rfft, ifft

def find_outlier(aCapture_signal):
    return


def remove_bad_samples(aCapture_signal):
    # These constants are sensitive to VGA change. VGA default is 0.55
    START_DATA_PTS = 58  # evaluate signal after 8us
    HIGH_BOUND = 0.15#0.013  # arbitrary value for Toyota cell
    LOW_BOUND = 0.001

    idx = []
    for i, sample in enumerate(aCapture_signal):
        # x_arr = np.absolute(signal)                                           #compare standard deviation with threshold

        std_value = np.std(sample[START_DATA_PTS:], ddof=1)
        if std_value > HIGH_BOUND or std_value < LOW_BOUND:
            print('std val: {}'.format(std_value))
            idx.append(i)
        else:
            None

    print("bad sampling {}".format(idx))

    aCapture_signal = np.delete(aCapture_signal, idx,axis=0).tolist()           # delete bad sampling by index

    return aCapture_signal


def check_data_quality_json():
    """
    This functions detect bad sampling in a capture.
    The first method detect a flat curve
    Second method detect a time shift more than 2 data points
    """
    # These constants are sensitive to VGA change. VGA default is 0.55

    key = '.json'
    # list_file = display_list_of_file(address, key)
    list_file = display_list_of_file(address, key)

    ''' Loop through every sample data in a read/capture '''
    for captureID, filename in enumerate(list_file):

        with open(address + filename) as json_file:
            aCapture = json.load(json_file)
        json_file.close()

        print ("capture ID: {}\t".format(aCapture['capture_number']))

        # strp = (aCapture['timestamp']).split('-04')[0]
        # echoes_endtime = datetime.strptime(strp,
        #                                    '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        time_object = datetime.strptime(aCapture['timestamp'], '%Y-%m-%dT%H:%M:%S-04:00')
        # aCapture['timestamp'] = time_object - timedelta(hours=4)                # convert UTC to EDT timezone

        aCapture['raw_data'] = [i for i in aCapture['raw_data'] if i != None]
        aCapture['raw_data'] = remove_bad_samples(aCapture['raw_data'])

        with open(address + 'capture{}-{}.json'.format(aCapture['capture_number'], aCapture['timestamp']), 'w') as writeout:
            aCapture['timestamp'] = aCapture['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
            # aCapture['input_side'] = 2
            writeout.write(json.dumps(aCapture))
        writeout.close()

    return


def plot_signal_from_json_new(remove_bad_samp=False, bandpass=False,
                          backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """


    folder_list = ['data',]


    for input_side in folder_list:
        plot_title = '{}| bandpass [0.3 - 1.2] Mhz | Gain 0.55'.format(
            input_side)

        address     = '/home/kacao/TitanAES/Python-scripts/data/'#{}/'.format(input_side)

        raw_signal_dict = {}
        avg_filtered_dict = {}
        temp_combined_dict = {}

        ped = 1.38888889e-1  # microsec, * 1000000

        key = 'capture*.json'

        list_file = sort_folder_by_name_universal(Path(address), key)
        print(list_file)

        count = 0
        for cnt, oneFile in enumerate(list_file):
            count += 1

            strip_name = oneFile.name.split('_')
            # print (strip_name)
            captureID = (strip_name[0].split('capture'))[1]
            # str = (oneFile.split('_'))[0]
            # captureID = str.split('cycle')[1]
            print('item {}, capture ID: {}'.format(cnt, captureID))

            #try catch here if error to open file
            with open(str(address / oneFile)) as json_file:
                echo_data = json.load(json_file)
            json_file.close()

            ''' Read temperature'''
            # tempC_1.append(echo_data['temperature'][0])
            # tempC_2.append(echo_data['temperature'][1])
            tempC = []
            if 'master' in echo_data['test_setting']:
                if echo_data['test_setting']['master'] != False:
                    tempC.append(
                        echo_data["test_setting"]["master"]["temp_sense_a_1"])
                else:
                    tempC.append(None)
            elif 'temperature' in echo_data:
                tempC.append(echo_data['temperature'][0])
                tempC.append(echo_data['temperature'][1])
            else:
                tempC.append(None)

            if echo_data['raw_data']:
                echo_data['raw_data'] = [i for i in echo_data['raw_data'] if
                                         i != None]
                if remove_bad_samp:
                    echo_data['raw_data'] = remove_bad_samples(
                        echo_data['raw_data'])

                raw_set_pd = pd.DataFrame()
                for idx, raw in enumerate(echo_data['raw_data']):
                    single_set = pd.DataFrame({idx: raw})                           # concat all data set into a singl dataframe
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


                ''' -------   plot the avg for checking clean data    ---- '''
                # plt.subplot(211)
                x_1 = np.arange(0, ped * row, ped)
                # x_1 = [1000000.0*ped for i in range(0, row)]                        #convert to micro-sec unit scale
                plt.title(plot_title)
                plt.plot(x_1, avg_bandpass,
                         label='capture {}'.format(int(captureID)))
                # plt.xlim(0, 70)
                plt.grid('on')
                plt.legend(loc='upper right')

                plt.show() # plot an individual signal
            else:
                print('no raw_data')
                avg = []
                avg_bandpass = []

            ''' New exe: Save all data as dict, then convert it to dataframe'''
            avg_filtered_dict.update({captureID: avg_bandpass})
            # raw_signal_dict.update({captureID : avg})
            temp_combined_dict.update({captureID: tempC})

            if count > 700 or cnt == len(list_file) - 1:
                filtered_concat = pd.DataFrame.from_dict(avg_filtered_dict,
                                                       orient='index')
                raw_data_concat = pd.DataFrame.from_dict(raw_signal_dict,
                                                         orient='index')
                __avgFilteredData__ = pd.DataFrame.from_dict(temp_combined_dict,
                                                        orient='index', columns=['temp_1'])
                # __avgRawData__      = pd.DataFrame.from_dict(temp_combined_dict,
                #                                         orient='index', columns=['temp_1'])

                # print (filtered_concat.head().to_string())
                __avgFilteredData__ = pd.concat([__avgFilteredData__, filtered_concat], axis=1)
                # __avgRawData__      = pd.concat([__avgFilteredData__, raw_data_concat], axis=1)
                __avgFilteredData__.to_csv(Path(address + input_side +
                                          '-{}-{}-filter.csv'.format(cnt + 1 - count,
                                                              cnt + 1)))
                # __avgRawData__.to_csv(Path(address + input_side +
                #                                 '-{}-{}-raw.csv'.format(cnt + 1 - count,
                #                                                     cnt + 1)))
                avg_filtered_dict = {}
                temp_combined_dict = {}
                count = 0
                del __avgFilteredData__
                print('count {}, cnt {}'.format(count, cnt))

                plt.show()
                plt.figure(figsize=(12.0, 7.0))
                plt.savefig(str(Path(
                    address + collection + "-{}-{}".format(input_side, cnt) + '-bandpass.png')))

    print("complete")
    return

def plot_signal_from_json(remove_bad_samp=False, bandpass=False, backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    avgTable_concat     = pd.DataFrame()
    filter_concat       = pd.DataFrame()
    signal_combined_dict= {}
    temp_combined_dict  = {}
    
    ped = 1.38888889e-1                                                         #microsec, * 1000000


    key='*.json'
    # list_file = display_list_of_file(address, key)

    list_file = sort_folder_by_name_universal(Path(address), key)
    print (list_file)

    tempC_1, tempC_2 = [], []
    count = 0
    for cnt, oneFile in enumerate(list_file):
        count += 1

        strip_name = oneFile.name.split('_')
        # print (strip_name)
        captureID =  (strip_name[0].split('capture'))[1]
        # str = (oneFile.split('_'))[0]
        # captureID = str.split('cycle')[1]
        print ('item {}, capture ID: {}'.format(cnt, captureID))


        with open(str(address / oneFile)) as json_file:
            echo_data = json.load(json_file)
        json_file.close()

        ''' Read temperature'''
        # tempC_1.append(echo_data['temperature'][0])
        # tempC_2.append(echo_data['temperature'][1])

        if 'master' in echo_data['test_setting']:
            if echo_data['test_setting']['master'] != False:
                tempC_1.append(echo_data["test_setting"]["master"]["temp_sense_a_1"])
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
                echo_data['raw_data'] = remove_bad_samples(echo_data['raw_data'])


            raw_set_pd = pd.DataFrame()
            for idx, raw in enumerate( echo_data['raw_data'] ):
                single_set = pd.DataFrame({idx: raw})                           # concat all data set into a singl dataframe
                raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
                                        ignore_index=True)


            [row,column] = raw_set_pd.shape

            avg = np.mean(raw_set_pd, axis=1)                                   # average 64 captures
            if bandpass:
                avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)      # apply bandpass

            if backgrd_subtract:
                avg = [a_i - b_i for a_i, b_i in zip( avg, backgrd )]


            ''' -------   plot the avg for checking clean data    ---- '''
            # plt.subplot(211)
            x_1 = np.arange(0, ped * row, ped)
            # x_1 = [1000000.0*ped for i in range(0, row)]                        #convert to micro-sec unit scale
            # plt.figure(dpi=200,  figsize=(12.0, 7.0))
            plt.title(plot_title)
            plt.plot(x_1, avg_bandpass, label='capture {}'.format(int(captureID)))
            plt.xlim(0,70)
            plt.grid('on')
            plt.legend(loc='upper right')

            plt.show() # plot an individual signal
        else:
            print ('no raw_data')
            avg = []
            avg_bandpass = []



        # # Save all average data into Dataframe
        avgTable = pd.DataFrame({captureID : avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)

        avg_filter = pd.DataFrame({captureID : avg_bandpass})
        filter_concat = pd.concat([filter_concat, avg_filter], axis=1)


    # plt.savefig(address + 'channel-B-798.png', dpi = 500)
    # plt.savefig(str(Path(address + collection + "-" + input_side + '-bandpass.png')))
    plt.interactive(False)
    plt.show()

    ''' Save Processed Data to csv '''
    # filter_concat = filter_concat.mean( axis=1 )
    filter_concat = filter_concat.T
    filter_concat.insert(loc=0, column='tempC_1', value=tempC_1)
    # filter_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    filter_concat.to_csv(Path(address + input_side + '-bandpass-avg.csv'))


    # avgTable_concat = avgTable_concat.mean( axis =1 )
    avgTable_concat = avgTable_concat.T
    avgTable_concat.insert(loc=0, column='tempC_1', value=tempC_1)
    # avgTable_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    avgTable_concat.to_csv(Path(address + input_side + '-raw-avg-sec.csv'))


    
    print ("complete")
    return


def plot_signal_from_pickle(remove_bad_samp=False, bandpass=False,
                          backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    avgTable_concat = pd.DataFrame()
    filter_concat = pd.DataFrame()
    signal_combined_dict = {}
    temp_combined_dict = {}

    ped = 1.38888889e-1  # microsec, * 1000000

    ''' Read pickle or json object '''
    obj_pickle = {}
    with open('/home/kacao/TitanAES/Python-scripts/data/nobatt.pickle',
              'rb') as pickle_readout:
        pickle_data = pickle.load(pickle_readout)
        while 1:
            try:
                obj_pickle.update(pickle.load(pickle_readout))
            except EOFError:
                break
    pickle_readout.close()



    print(len(pickle_data))
    print(len(obj_pickle))

    pprint (obj_pickle)
    for key, val in obj_pickle.items():
        pet = pickle_data[key]
        print('id: {}, cap_number: {}'.format(key, pet['capture_number']))
        # pprint.pprint('val {}'.format(val))
        # pprint.pprint(len(pet['raw_data']))



    # tempC_1, tempC_2 = [], []
    # count = 0
    # for cnt, oneFile in enumerate(list_file):
    #     count += 1
    #
    #     strip_name = oneFile.name.split('_')
    #     # print (strip_name)
    #     captureID = (strip_name[0].split('capture'))[1]
    #     # str = (oneFile.split('_'))[0]
    #     # captureID = str.split('cycle')[1]
    #     print('item {}, capture ID: {}'.format(cnt, captureID))
    #
    #     with open(str(address / oneFile)) as json_file:
    #         echo_data = json.load(json_file)
    #     json_file.close()
    #
    #     ''' Read temperature'''
    #     # tempC_1.append(echo_data['temperature'][0])
    #     # tempC_2.append(echo_data['temperature'][1])
    #
    #     if 'master' in echo_data['test_setting']:
    #         if echo_data['test_setting']['master'] != False:
    #             tempC_1.append(
    #                 echo_data["test_setting"]["master"]["temp_sense_a_1"])
    #         else:
    #             tempC_1.append(None)
    #     elif 'temperature' in echo_data:
    #         tempC_1.append(echo_data['temperature'][0])
    #         tempC_2.append(echo_data['temperature'][1])
    #     else:
    #         tempC_1.append(None)
    #
    #     if echo_data['raw_data']:
    #         echo_data['raw_data'] = [i for i in echo_data['raw_data'] if
    #                                  i != None]
    #         if remove_bad_samp:
    #             echo_data['raw_data'] = remove_bad_samples(
    #                 echo_data['raw_data'])
    #
    #         raw_set_pd = pd.DataFrame()
    #         for idx, raw in enumerate(echo_data['raw_data']):
    #             single_set = pd.DataFrame(
    #                 {idx: raw})  # concat all data set into a singl dataframe
    #             raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
    #                                    ignore_index=True)
    #
    #         [row, column] = raw_set_pd.shape
    #
    #         avg = np.mean(raw_set_pd, axis=1)  # average 64 captures
    #         if bandpass:
    #             avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000,
    #                                                             1200000,
    #                                                             51)  # apply bandpass
    #
    #         if backgrd_subtract:
    #             avg = [a_i - b_i for a_i, b_i in zip(avg, backgrd)]
    #
    #         ''' -------   plot the avg for checking clean data    ---- '''
    #         # plt.subplot(211)
    #         x_1 = np.arange(0, ped * row, ped)
    #         # x_1 = [1000000.0*ped for i in range(0, row)]                        #convert to micro-sec unit scale
    #         # plt.figure(dpi=200,  figsize=(12.0, 7.0))
    #         plt.title(plot_title)
    #         plt.plot(x_1, avg_bandpass,
    #                  label='capture {}'.format(int(captureID)))
    #         plt.xlim(0, 70)
    #         plt.grid('on')
    #         plt.legend(loc='upper right')
    #
    #         plt.show()  # plot an individual signal
    #     else:
    #         print('no raw_data')
    #         avg = []
    #         avg_bandpass = []
    #
    #     # # Save all average data into Dataframe
    #     avgTable = pd.DataFrame({captureID: avg})
    #     avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)
    #
    #     avg_filter = pd.DataFrame({captureID: avg_bandpass})
    #     filter_concat = pd.concat([filter_concat, avg_filter], axis=1)
    #
    # # plt.savefig(address + 'channel-B-798.png', dpi = 500)
    # # plt.savefig(str(Path(address + collection + "-" + input_side + '-bandpass.png')))
    # plt.interactive(False)
    # plt.show()
    #
    # ''' Save Processed Data to csv '''
    # # filter_concat = filter_concat.mean( axis=1 )
    # filter_concat = filter_concat.T
    # filter_concat.insert(loc=0, column='tempC_1', value=tempC_1)
    # # filter_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    # filter_concat.to_csv(Path(address + input_side + '-bandpass-avg.csv'))
    #
    # # avgTable_concat = avgTable_concat.mean( axis =1 )
    # avgTable_concat = avgTable_concat.T
    # avgTable_concat.insert(loc=0, column='tempC_1', value=tempC_1)
    # # avgTable_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    # avgTable_concat.to_csv(Path(address + input_side + '-raw-avg-sec.csv'))
    #
    # print("complete")
    # return




def plot_signal_from_json_autonomous(remove_bad_samp=False, bandpass=False,
                          backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    avgTable_concat = pd.DataFrame()
    filter_concat = pd.DataFrame()
    signal_combined_dict = {}
    temp_combined_dict = {}

    ped = 1.38888889e-1  # microsec, * 1000000

    key = '*.json'
    # list_file = display_list_of_file(address, key)

    list_file = sort_folder_by_name_universal(Path(address), key)
    print(list_file)

    count = 0
    for cnt, oneFile in enumerate(list_file):
        count += 1

        strip_name = oneFile.name.split('_')
        # print (strip_name)
        captureID = (strip_name[0].split('capture'))[1]
        # str = (oneFile.split('_'))[0]
        # captureID = str.split('cycle')[1]
        print('item {}, capture ID: {}'.format(cnt, captureID))

        with open(str(address / oneFile)) as json_file:
            echo_data = json.load(json_file)
        json_file.close()


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

            ''' -------   plot the avg for checking clean data    ---- '''
            # plt.subplot(211)
            x_1 = np.arange(0, ped * row, ped)
            # x_1 = [1000000.0*ped for i in range(0, row)]                        #convert to micro-sec unit scale
            # plt.figure(dpi=200,  figsize=(12.0, 7.0))
            plt.title(plot_title)
            plt.plot(x_1, avg_bandpass,
                     label='capture {}'.format(int(captureID)))
            plt.xlim(0, 70)
            plt.grid('on')
            plt.legend(loc='upper right')

            # plt.show()  # plot an individual signal
        else:
            print('no raw_data')
            avg = []
            avg_bandpass = []

        # # Save all average data into Dataframe
        avgTable = pd.DataFrame({captureID: avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)

        avg_filter = pd.DataFrame({captureID: avg_bandpass})
        filter_concat = pd.concat([filter_concat, avg_filter], axis=1)

    # plt.savefig(address + 'channel-B-798.png', dpi = 500)
    # plt.savefig(str(Path(address + collection + "-" + input_side + '-bandpass.png')))
    plt.interactive(False)
    plt.show()

    ''' Save Processed Data to csv '''
    # filter_concat = filter_concat.mean( axis=1 )
    filter_concat = filter_concat.T
    # filter_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    filter_concat.rename(columns={'': 'captureID'}, inplace=True)
    filter_concat.to_csv(Path(address + input_side + '-bandpass-avg.csv'))

    # avgTable_concat = avgTable_concat.mean( axis =1 )
    avgTable_concat = avgTable_concat.T
    # avgTable_concat.insert(loc=1, column='tempC_2', value=tempC_2)
    avgTable_concat.rename(columns={'': 'captureID'}, inplace=True)
    avgTable_concat.to_csv(Path(address + input_side + '-raw-avg-sec.csv'))

    print("complete")
    return


def plot_fft_signal():
    def y_fm(x, y):
        return ('{:2.2e}'.format(x).replace('e', 'x10^'))

    filename = 'capture3_2019-02-26T09:49:57.json'
    with open(str(address / filename)) as json_file:
        aCapture = json.load(json_file)
    json_file.close()
    
    avg = np.mean(aCapture['raw_data'], axis=0)                                   # average 64 captures
    if True:
        avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)      # apply bandpass
    print ('len avg: {}'.format(len(avg_bandpass)))
    
    y_intp = interp(interp(avg_bandpass, 10), 10)
    yf = fft(y_intp)
    N = len(y_intp)
    print ('len N {}'.format(N))
    T = 1.38888889e-1 #1/7.2e-6
    # x = np.linspace(0.0, N*T, N)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

    fig = plt.figure()

    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    plt.xlabel("Frequency [$10^{x} hz]$")
    # logfmt = matplotlib.ticker.LogFormatterExponent(base=10.0, labelOnlyBase=True)
    # ax.xaxis.set_major_formatter(logfmt)

    plt.xlim([0, 0.025])
    plt.grid()
    plt.show()

    return


def upload_json_to_mongo():
    print("Initializing database")
    echoes_db = database(database=dtb)

    batch_size = 100
    insert_list = []
    count = 0

    key = '*.json'

    # list_file = display_list_of_file(address, key)
    list_file = sort_folder_by_name_universal(Path(address), key)
    print (list_file)

    ''' Loop through every sample data in a read/capture '''
    for idx, filename in enumerate(list_file):
        # with open(address + filename) as json_file:
        with open(str(address / filename)) as json_file:
            aCapture = json.load(json_file)
        json_file.close()

        print ("capture ID: {}\t".format(aCapture['capture_number']))

        # aCapture['input_side'] = input_sd
        # aCapture['source'] = 'echoes-a'
        if aCapture['timestamp'] is not None:
            aCapture['timestamp'] = datetime.strptime(aCapture['timestamp'],
                                               '%Y-%m-%dT%H:%M:%S')

        count+= 1
        insert_list.append( aCapture )

        # insert a batch of 100 obj or the end of filelist
        if count >= batch_size or idx == len(list_file) - 1:
            print ('idx {}'.format(idx))
            result = echoes_db.insert_multiple(insert_list, collection=collection)
            print (result)

            count = 0
            insert_list = []


    echoes_db.close()
    return
#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():
    global backgrd

    """
        (1) Check data quality: detect flat curve, missing echo
    """
    # check_data_quality_json()
    # check_data_quality_mongo(remove_bad_samp=True, collection=collection)
    # """
    # (2) plot avg of each capture. Save avg (mean) to csv file
    # """
    plot_signal_from_json_new(remove_bad_samp=False, bandpass=True, backgrd_subtract= False)
    # plot_signal_from_pickle()
    # plot_signal_from_mongo(collection=collection)
    # plot_fft_signal()

    # upload_json_to_mongo()
    """
    (4) Plot all 64 samplings in a capture. Query data from Mongodb
    """
    # plot_signal_from_mongo(collection=collection)

    # echoes_db = database(database='echoes-captures')
    #
    # query = {
    #     'capture_number': 701,
    #     'test_setting.captureAdc': 0
    # }
    # projection = {
    #     'raw_data': 1,
    #     '_id': 1,
    # }
    # data_cursor = echoes_db.search(query=query, projection=projection,
    #                                collection="TC28constant3A")
    #
    # for oneCapture in data_cursor:
    #     avg = np.mean(oneCapture['raw_data'], axis=0)
    #     print (avg)
    #
    #     res = echoes_db.update(record ={"$unset": {"raw_data.0": 1, "raw_data.2": 1}},
    #                      match  ={"_id": oneCapture['_id']},
    #                      collection='TC28constant3A')
    #     print (res)
    #
    #
    #
    # data_cursor_2 = echoes_db.search(query=query, projection=projection,
    #                                collection="TC28constant3A")
    # for oneCap in data_cursor_2:
    #     print(oneCap['raw_data'][0])
    #
    #     raw = [i for i in oneCap['raw_data'] if i != None]
    #     avg_1 = np.mean(raw, axis=0)
    #     print (avg_1)
    #     res = echoes_db.upsert(record ={"average_data": avg_1.tolist()},
    #                      uid  = oneCap['_id'],
    #                      collection='TC28constant3A')
    #     print (res)


    # match_stage={'$match':{'capture_number':706}}
    #
    # field = 'raw_data'
    # unwind_stage={'$unwind': '$'+field  }
    #
    # group_stage = {'$group': {
    #     '_id': 0,
    #     'average': {'$avg': '$'+'raw_data'}
    #     # 'average': {'$push': '$avg_raw'}
    # }},
    #
    # field = 'raw_data'
    # projection={'$project': {
    #     '_id': 1,
    #     # 'avg_raw': {'$avg':'$'+field},
    #     'raw_data':1,
    #     'capture_number':1,
    # }}
    #
    # out_stage = {
    #     '$out': 'TC28cont3test'
    # }
    #
    #
    #
    # pipeline = [match_stage,
    #             # unwind_stage,
    #             group_stage,
    #             projection,
    #             out_stage
    #             ]
    # res = echoes_db.aggregation(pipeline, collection='TC28constant3A')
    # print (res)

    # db.response.aggregate([
    #     {'$project':{
    #         "job_details.label_name": 1,
    #         '_id': 0 }},
    #     {'$unwind': "$job_details.label_name"},
    #     {'$group':{
    #         '_id': "$job_details.label_name",
    #         count: {'$sum': 1}}
    #     }
    # ])


    # echoes_db.close()
    return
#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

# is_64bits = sys.maxsize > 2**32
# print ('is 64bit {}'.format(is_64bits))
# import struct
# print(struct.calcsize("P") * 8)

dtb         = 'Tuna-Can'
collection  = 'Toyota'

input_side      = '2-batch'
input_sd        = 1 if 'primary' in input_side else 2
plot_title  = '{}| bandpass [0.3 - 1.2] Mhz | Gain 0.55'.format(input_side)


address     = '/media/kacao/Echoes-data-2/Tuna-can-11/{}/'.format(input_side)
# address = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/Me05-190227/primary_json/')


echoes_dsp = echoes_signals( 7200000.0 )
if __name__ == '__main__':
    main()
    # elapsed_time = timeit.timeit(main, number=100) / 100
    # print(elapsed_time)