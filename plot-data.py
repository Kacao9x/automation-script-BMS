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


import subprocess

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

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
        list_file = display_list_of_file('cycle' + str(cycle_id) + '-')
        print (list_file)

        ''' Loop through every sample data in a read/capture '''
        for filename in list_file:
            with open(address + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float
            ''' DETECT a flat curve in a sample '''
            if find_dup_run(data, primary_channel):
                print ("cycle : {}".format( cycle_id + 1 ))
                with open(address + 'bad-flat.txt', 'ab') as writeout:
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


def check_data_quality_mongo(collection):
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

        max_value = max(x)
        min_value = min(x)

        if isPrimary:
            return max_value - min_value < PRIMARY_AMP_RANGE
        else:
            return (max_value - min_value < SECONDARY_AMP_RANGE_LOW or
                    max_value - min_value > SECONDARY_AMP_RANGE_HIGH)

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
        # 'capture_number': 1,
        'test_setting.captureAdc' : 0
    }
    projection = {
        'raw_data': 1,
        'capture_number':1,
        'timestamp': 1,
        '_id': 0,
    }
    data_cursor = echoes_db.search(query=query, projection=projection,
                              collection=collection)

    count = 0
    for aCapture in data_cursor:
        # count += 1
        print ("capture ID: {}".format(aCapture['capture_number']))
        print('length raw_data: {}'.format(len(aCapture['raw_data'])))

        sample = 0
        dup = []
        echoes_index = []

        aCapture['raw_data'] = [i for i in aCapture['raw_data'] if i != None]
        while sample < len(aCapture['raw_data']):

            # find the flat signal
            if find_dup_run(aCapture['raw_data'][sample], primary_channel):
                dup.append(sample)

            # locate 1st/2nd peak to detect time shift later
            # echo_idx = _locate_1stEcho_index(aCapture['raw_data'][sample])
            # echoes_index.append(echo_idx)


            sample += 1

        print("duplicate {}".format(dup))
        aCapture['raw_data'] = np.delete(aCapture['raw_data'], dup, axis=0).tolist()     # delete bad sampling by index
        # for idx in dup:
        #     del aCapture['raw_data'][idx]

        with open(address + 'capture{}-{}.json'.format(aCapture['capture_number'], aCapture['timestamp']), 'w') as writeout:
            aCapture['timestamp'] = aCapture['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
            writeout.write(json.dumps(aCapture))
        writeout.close()
    print ('count {}'.format(count))


        #     # record = {'$unset': {'raw_data.{}': 1}}
        #     # res = echoes_db.update(record ={"$unset": {"raw_data.0": 1, "raw_data.2": 1}},
        #     #                  match  ={"_id": oneCapture['_id']},
        #     #                  collection='TC28constant3A')
        #     # print (res)
        #
        # ''' DETECT a time-shift in signal '''
        # avg = _find_avg( echoes_index )
        # print ('avg is: {}'.format(avg))
        # for i, element in enumerate(echoes_index):
        #     if abs( element - avg ) > 2:
        #         print ("capture shift: {} - {}".format(str(count),str(i + 1)))




    echoes_db.close()

    return

def plot_signal_from_mongo():
    echoes_db = database(database='echoes-captures')

    query = {}
    projection={
        # 'raw_data':1
        'temperature':1,
        'echoes_setting':1
    }
    data = echoes_db.search(query=query,projection=projection,
                                     collection="Me06")

    for element in data:
        pprint (element)
        
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

    echoes_db.close()
    return


def check_data_quality_json():
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



    global cycle_id


    echoes_index = []
    list_file = display_list_of_file_by_date(address)
    print (list_file)

    ''' Loop through every sample data in a read/capture '''
    for captureID, filename in enumerate(list_file):

        with open(address + filename) as json_file:
            aCapture = json.load(json_file)
        json_file.close()

        dup = []
        for idx in range(len(aCapture['raw_data'])):

            ''' DETECT a flat curve in a sample '''
            if find_dup_run(aCapture['raw_data'][idx], primary_channel):
                dup.append(idx)
                # with open(address + 'bad-flat.txt', 'ab') as writeout:
                #     writeout.writelines(str(captureID) + '-' + str(idx) + '\n')
                # writeout.close()

            ''' DETECT a time-shift in signal
                by checking differnce of 1st/2nd echo position against average'''

            # echo_idx = _locate_1stEcho_index(aCapture['raw_data'][idx])
            # echoes_index.append(echo_idx)
        print("duplicate {}".format(dup))
        aCapture['raw_data'] = np.delete(aCapture['raw_data'], dup, axis=0).tolist()  # delete bad sampling by index

        avg = np.mean(aCapture['raw_data'], axis=0)
        aCapture['average_data'] = avg.tolist()
        with open(address + '{}.json'.format(aCapture['capture_number']), 'w') as writeout:
            writeout.write(json.dumps(aCapture))
        writeout.close()

    return

def plot_signal_from_json(bandpass=False, backgrd_subtract=False):
    """
    (2) plot avg of each cycle. Save avg (mean) to csv file
    """
    global cycle
    global cycle_id
    avgTable_concat = pd.DataFrame()
    filter_concat = pd.DataFrame()
    
    ped = 1.38888889e-1         #* 1000000


    key='.json'
    list_file = display_list_of_file(address, key)
    print (list_file)

    for oneFile in list_file:
        strip_name = oneFile.split('-')
        captureID =  (strip_name[0].split('capture'))[1]
        print ('capture ID: {}'.format(captureID))

        with open(address + oneFile) as json_file:
            echo_data = json.load(json_file)
        json_file.close()

        raw_set_pd = pd.DataFrame()
        for idx, raw in enumerate( echo_data['raw_data'] ):
            single_set = pd.DataFrame({idx: raw})                        # concat all data set into a singl dataframe
            raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
                                    ignore_index=True)

        
        [row,column] = raw_set_pd.shape
        # print ("capture: {}, row {} col {}".format(str(echo_data['capture_number']), 
                                                    # str(row), str(column)))

        avg = np.mean(raw_set_pd, axis=1)                                          # average 64 captures
        if bandpass:
            avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000, 1200000, 51)      # apply bandpass

        if backgrd_subtract:
            avg = [a_i - b_i for a_i, b_i in zip( avg, backgrd )]

        # if normalize:


        ''' -------   plot the avg for checking clean data    ---- '''
        # plt.subplot(211)
        x_1 = np.arange(0, ped * row, ped)
        # x_1 = [1000000.0*ped for i in range(0, row)]                 #convert to micro-sec unit scale
        plt.title(' TC02 - 2 | bandpass [0.3 - 1.2] Mhz | Gain 0.55 | 2019 Jun 14')
        plt.plot(x_1, avg_bandpass, label='capture 0{}'.format(int(captureID)))
        plt.xlim(0,70)
        plt.grid('on')
        plt.legend(loc='upper right')

        # plt.show() # plot an individual signal


        # Save all average data into Dataframe
        avgTable = pd.DataFrame({captureID : avg})
        avgTable_concat = pd.concat([avgTable_concat, avgTable], axis=1)

        avg_filter = pd.DataFrame({captureID : avg_bandpass})
        filter_concat = pd.concat([filter_concat, avg_filter], axis=1)

    plt.interactive(False)
    # plt.savefig(address + 'channel-B-798.png', dpi = 500)
    plt.show()
    

    
    # avgTable_concat = avgTable_concat.mean( axis =1 )
    avgTable_concat = avgTable_concat.T
    avgTable_concat.to_csv(address + input_channel + '-raw-avg-sec.csv')

    # filter_concat = filter_concat.mean( axis=1 )
    filter_concat = filter_concat.T
    filter_concat.to_csv(address + input_channel + '-bandpass-avg-sec.csv')
    # avgTable_concat.to_csv(address + input_channel + '-raw-avg-9-channel-A.csv')
    
    print ("complete")
    return



def plot_v1v2_from_json():
    with open(address + input_channel + '-bandpass-avg-channel-A-sec.csv') as outfile:
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
    global avgPos
    global avgNum
    global cycle
    global cycle_id
    global backgrd

    """
        (1) Check data quality: detect flat curve, missing echo
    """
    # check_data_quality()
    # check_data_quality_json()
    check_data_quality_mongo(collection='TC02-2')
    """
    (2) plot avg of each capture. Save avg (mean) to csv file
    """
    # check_signal_plot(bandpass = True, backgrd_subtract = False)
    # plot_signal_from_json(bandpass=True, backgrd_subtract= False)
    # plot_v1v2_from_json()


    """
    (4) Plot all 64 samplings in a capture. Query data from Mongodb
    """
    # plot_signal_from_mongo()

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

input_channel = 'primary'
primary_channel = (input_channel == 'primary')
print (str(primary_channel))

battery_id  = 'TC02-'
SoH         = 'H77.23'
day         = '_190123'


address = '/media/kacao/Ultra-Fit/titan-echo-boards/Nissan-Leaf/TC02-2-H_190524/primary/'
echoes_index = []
backgrd = []

avgPos  = 0  # number of capture in each cycle
avgNum  = 64
cycle   = 5
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