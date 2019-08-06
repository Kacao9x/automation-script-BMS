import matplotlib.pyplot as plt
import numpy as np
import subprocess

# import thLib as th
import pandas as pd
from lib.echoes_signalprocessing import *
from lib.echoes_database import *

import json
from lib.commandline import *
from datetime import datetime,timedelta

def check_data_quality_mongo(collection):
    """
    This functions detect bad sampling in a capture.
    The first method detect a flat curve
    Second method detect a time shift more than 2 data points
    """

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

    def remove_bad_samples(aCapture_signal):
        # These constants are sensitive to VGA change. VGA default is 0.55
        START_DATA_PTS = 58                                                     #evaluate signal after 8us
        HIGH_BOUND = 0.2                                                        #arbitrary value for Toyota cell
        LOW_BOUND  = 0.09

        idx = []
        for i, sample in enumerate(aCapture_signal):
            # x_arr = np.absolute(signal)                                         #compare standard deviation with threshold

            std_value = np.std(sample[START_DATA_PTS : ], ddof=1)
            # print ('std val: {}'.format(std_value))
            if std_value > HIGH_BOUND or std_value < LOW_BOUND:
                idx.append(i)
            else:
                None

        print("bad sampling {}".format(idx))

        aCapture_signal = np.delete(aCapture_signal, idx, axis=0).tolist()      # delete bad sampling by index

        return aCapture_signal


    echoes_db = database(database='echoes-captures')

    query = {
        'capture_number': {'$gt':1242},
    }

    #1: ascending, -1: descending, 0: hidden
    projection = {
        # 'echoes_id':1,
        # 'test_examiner':0,
        # 'transducer_id':0,
        'raw_data': 1,
        'capture_number':1,
        'timestamp': 1,
        'test_setting.master.temp_sense_a_1': 1,
        '_id': 0,
        'input_channel':1
    }
    data_cursor = echoes_db.search(query=query, projection=projection,
                              collection=collection)

    count = 0
    for aCapture in data_cursor:
        count += 1
        print ("capture ID: {}\t".format(aCapture['capture_number']))

        # time_obj = datetime.strptime(aCapture['timestamp'], '%Y-%m-%dT%H:%M:%S')
        # aCapture['timestamp'] = time_obj - timedelta(hours=4)  # convert UTC to EDT timezone
        # aCapture['timestamp'] = aCapture['timestamp'] - timedelta(hours=4)      #convert UTC to EDT timezone

        aCapture['raw_data'] = [i for i in aCapture['raw_data'] if i != None]
        aCapture['raw_data'] = remove_bad_samples(aCapture['raw_data'])

        print ("saving data to disk\n")
        # Used to separate dataset doesn't have input channel info
        # if count % 2 == 1:
        #     path = address + 'primary/'
        # else:
        #     path = address + 'secondary/'

        if aCapture['input_channel'] == 1:
            path = address + 'primary/'
        else:
            path = address + 'secondary/'

        with open(path + 'capture{}-{}.json'.format(aCapture['capture_number'], aCapture['timestamp']), 'w') as writeout:
            # aCapture['timestamp'] = aCapture['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
            writeout.write(json.dumps(aCapture))
        writeout.close()

    echoes_db.close()

    return

def plot_signal_from_mongo(collection):
    echoes_db = database(database='echoes-captures')
    query = {
        'capture_number':{'$lt':8, '$gt':3}
    }
    projection={
        'raw_data':1
        # 'temperature':1,
        # 'echoes_setting':1
    }
    data_cursor = echoes_db.search(query=query,projection=projection,
                                     collection=collection)

    for aCapture in data_cursor:
        # pprint (aCapture)
        sample = 0
        # print (len(aCapture['raw_data'][0]))
        while sample < len(aCapture['raw_data']):
            dt = 1.38888E-1                     #float(1/7200000)
            row = 512
            x = np.arange(0, dt * row, dt)
            filter_data = echoes_dsp.apply_bandpass_filter(aCapture['raw_data'][sample],
                                                   300000, 1000000, 51)
            plt.figure(1)
            plt.title('Signal Plot')
            plt.interactive(False)
            plt.plot(x, filter_data, label='Sample 0{} '.format( str(sample +1)))
            plt.grid('on')
            plt.xlabel('time (us)')
            plt.ylabel('amplitude')

            plt.legend(loc='upper right')

            sample += 1
        plt.show()

    echoes_db.close()
    return


def check_data_quality_json():
    """
    This functions detect bad sampling in a capture.
    The first method detect a flat curve
    Second method detect a time shift more than 2 data points
    """
    # These constants are sensitive to VGA change. VGA default is 0.55

    def remove_bad_samples(aCapture_signal):
        # These constants are sensitive to VGA change. VGA default is 0.55
        START_DATA_PTS = 58                                                     #evaluate signal after 8us
        HIGH_BOUND = 0.2                                                        #arbitrary value for Toyota cell
        LOW_BOUND  = 0.09

        idx = []
        for i, sample in enumerate(aCapture_signal):
            # x_arr = np.absolute(signal)                                         #compare standard deviation with threshold

            std_value = np.std(sample[START_DATA_PTS : ], ddof=1)
            # print ('std val: {}'.format(std_value))
            if std_value > HIGH_BOUND or std_value < LOW_BOUND:
                idx.append(i)
            else:
                None

        print("bad sampling {}".format(idx))

        aCapture_signal = np.delete(aCapture_signal, idx, axis=0).tolist()      # delete bad sampling by index

        return aCapture_signal

    key = '.json'
    # list_file = display_list_of_file(address, key)
    list_file = sort_folder_by_name(address, key)

    ''' Loop through every sample data in a read/capture '''
    for captureID, filename in enumerate(list_file):

        with open(address + filename) as json_file:
            aCapture = json.load(json_file)
        json_file.close()

        print ("capture ID: {}\t".format(aCapture['capture_number']))

        time_object = datetime.strptime(aCapture['timestamp'], '%Y-%m-%dT%H:%M:%S')
        # aCapture['timestamp'] = time_object - timedelta(hours=4)                # convert UTC to EDT timezone

        aCapture['raw_data'] = [i for i in aCapture['raw_data'] if i != None]
        aCapture['raw_data'] = remove_bad_samples(aCapture['raw_data'])

        path = '/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/Me08/secondary_gap/'
        with open(path + 'capture{}-{}.json'.format(aCapture['capture_number'], aCapture['timestamp']), 'w') as writeout:
            # aCapture['timestamp'] = aCapture['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
            writeout.write(json.dumps(aCapture))
        writeout.close()


    return


def plot_signal_from_json(bandpass=False, backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    avgTable_concat     = pd.DataFrame()
    filter_concat       = pd.DataFrame()
    
    ped = 1.38888889e-1                                                         #microsec, * 1000000


    key='.json'
    list_file = display_list_of_file_by_date(address, key)
    # list_file = sort_folder_by_name(address, key)
    print (list_file)

    tempC_1, tempC_2 = [], []
    for oneFile in list_file:
        strip_name = oneFile.split('-')
        captureID =  (strip_name[0].split('capture'))[1]
        print ('capture ID: {}'.format(captureID))

        with open(address + oneFile) as json_file:
            echo_data = json.load(json_file)
        json_file.close()

        ''' Read temperature'''
        # tempC_1.append(echo_data['temperature'][0])
        # tempC_2.append(echo_data['temperature'][1])
        if 'master' in echo_data['test_setting']:
            tempC_1.append(echo_data["test_setting"]["master"]["temp_sense_a_1"])
        else:
            tempC_1.append(None)


        if echo_data['raw_data']:
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

            # if normalize:


            ''' -------   plot the avg for checking clean data    ---- '''
            # plt.subplot(211)
            x_1 = np.arange(0, ped * row, ped)
            # x_1 = [1000000.0*ped for i in range(0, row)]                        #convert to micro-sec unit scale
            plt.title(plot_title)
            plt.plot(x_1, avg_bandpass, label='capture 0{}'.format(int(captureID)))
            plt.xlim(0,70)
            plt.grid('on')
            plt.legend(loc='upper right')

            # plt.show() # plot an individual signal
        else:
            print ('no raw_data')
            avg = []
            avg_bandpass = []

        # Save all average data into Dataframe
        avgTable = pd.DataFrame({captureID : avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)

        avg_filter = pd.DataFrame({captureID : avg_bandpass})
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
    filter_concat.to_csv(address + input_channel + '-bandpass-avg-sec.csv')
    # avgTable_concat.to_csv(address + input_channel + '-raw-avg-9-channel-A.csv')
    
    print ("complete")
    return


#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():
    global cycle
    global cycle_id
    global backgrd

    """
        (1) Check data quality: detect flat curve, missing echo
    """
    # check_data_quality_json()
    check_data_quality_mongo(collection=collection)
    # """
    # (2) plot avg of each capture. Save avg (mean) to csv file
    # """
    # plot_signal_from_json(bandpass=True, backgrd_subtract= False)
    # plot_signal_from_mongo(collection=collection)

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

input_channel       = 'primary_2'
collection  = 'Me09'
plot_title  = ' Me09 - Reflection_2| bandpass [0.3 - 1.2] Mhz | Gain 0.55 | 2019 Aug 5th'


address     = '/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/Me09/'

# backgrd = []
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