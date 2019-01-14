from datetime import time
import pandas as pd
import subprocess
from pprint import pprint
from bson import ObjectId
import json


from lib.echoes_database import *



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


def _get_timestamp( filename ):
    timest = {}
    i = filename.split('-')

    (timest['year'], timest['month'], timest['day'])    = int(i[2]), int(i[3]), int(i[4])
    (timest['hour'], timest['min'], timest['sec'])      = int(i[5]), int(i[6]), int(i[7])


    return timest

def post_csv_report():

    global bucket
    with open(address + filename) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    print (len(table.index))

    cycle = 70  #len(table.index)
    cycle_id = 70

    while cycle_id < cycle + 1:

        if cycle_id == 127:
            cycle_id = 128
        row = cycle_id - 1                                                      # row in PANDAS table start from 0
        print ('row %s' % str(row))

        res = echoes_db.search(query={'test_apparatus.battery_id': battery_id,
                                      'test_results.capture_number': cycle_id,
                                      'test_setting.input_channel': input_channel},
                               collection=cabinet)

        for post in res:
            pprint(post['_id'])
            data = list(table.iloc[row, -512 : -1].values)                      # retrieve signal data from the report

            # post['test_results']['average'] = data
            post['test_results'].update({
                'temperature'   : {
                    'top'   : float(table['Temperature_top'][cycle_id -1]),
                    'bottom': float(table['Temperature_bottom'][cycle_id -1])
                },
                'cap(mAh)'      : float(table['cap(mAh)'][cycle_id -1]),
                'current'       : float(table['current'][cycle_id -1]),
                'volt'          : float(table['volt'][cycle_id -1]),
                'charging'      : int(table['charging'][cycle_id -1]),
                'average'       : data
            })
            echoes_db.update(post, {'_id': post['_id']},
                             collection=cabinet)

            # echoes_db.delete({'test_results.average':[]},
            #                  collection='tuna-can-sample')

        cycle_id += 1                                                           # move to next row


    print('completed upserting AVG data')

    return


def post_raw_data():
    global bucket

    with open(address + filename) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    cycle = 71
    cycle_id = 71

    while cycle_id < cycle + 1:
        bucket = {}

        if cycle_id == 127:
            cycle_id = 128

        timest = _get_timestamp(table['FileName'][cycle_id - 1])
        bucket['timestamp'] = datetime.datetime(timest['year'], timest['month'],
                                                timest['day'], timest['hour'],
                                                timest['min'], timest['sec'])

        bucket['test_apparatus'] = {
            'battery_id'    : battery_id,
            'transducer_id' : 67143,
            'echoes_id'     : 'echoes-a'
        }

        bucket['project_name']  = project
        bucket['test_examiner'] = examiner

        bucket['test_setting']  = {
            'impulse_volt'  : 85,
            'vga_gain'      : 0.55,
            'delay_ms'      : 25,
            'sampling_rate' : 7200000,
            'impulse_type'  : 'neg-bipolar',
            'input_channel' : input_channel
        }

        bucket['test_results']  = {
            'capture_number': cycle_id
            # 'temperature'   : {
            #     'top'   : float(table['Temperature_top'][cycle_id -1]),
            #     'bottom': float(table['Temperature_bottom'][cycle_id -1])
            # },
            # 'cap(mAh)'      : float(table['cap(mAh)'][cycle_id -1]),
            # 'current'       : float(table['current'][cycle_id -1]),
            # 'volt'          : float(table['volt'][cycle_id -1]),
            # 'charging'      : int(table['charging'][cycle_id -1])
        }

        res = echoes_db.insert_capture(record=bucket, collection=cabinet)
        print (res)
        print ('completed inserting')

        #------- upsert every run each capture into 'test-results' --------#
        # bucket = {
        #   dat : [
        #       {"id": 110, "data": {"Country": "ES", "Count": [64,65,66]}},
        #       {"id": 112, "data": {"Country": "ES", "Count": 5}},
        #       {"id": 114, "data": {"Country": "UK", "Count": 3}}
        #   ]
        #}
        # db.test_collection.find({"data.Country": "ES"})
        # db.test_collection.find({"data.Count": {"$lt": 6}})

        oneRead, list_file = concat_all_data(tempC=False, search_key='cycle' +
                                                        str(cycle_id) + '-')

        [row, column] = oneRead.shape
        print (column)

        res = echoes_db.search(query={'test_apparatus.battery_id':battery_id,
                                      'test_results.capture_number': cycle_id,
                                      'test_setting.input_channel':input_channel},
                               collection=cabinet)


        for post in res:
            pprint(post['_id'])
            post['test_results']['raw_data'] = []

            avgPos = 1
            while avgPos < column + 1:

                value = list(oneRead.loc[:, avgPos -1].values)
                # print (value)

                post['test_results']['raw_data'].append(
                    {'run': avgPos, 'result': value}
                )
                avgPos += 1 #go to next column
                # pprint(post['test_results'])
            echoes_db.update(post, {'_id': post['_id']},
                             collection=cabinet)


        print ("completed uploading cycle %s" % str(cycle_id))
        cycle_id += 1

    return



battery_id      = 'TC16-H73'
input_channel   = 'secondary'
cabinet         = 'tuna-sample'
examiner        = 'Khoi'
project         = 'TUNA016-Phase1-Build_ML_Model'

print("Initializing database")
echoes_db       = database(database='echoes-captures')
echoes_db.mongo_db = cabinet


filename = battery_id + '_181219_' + input_channel + '-sorted.csv'
bucket = {}
address = '/media/kacao-titan/Ultra-Fit/titan-echo-boards/echo-A/TC16-H73_181219/' + input_channel + '/'


if __name__ == '__main__':

    post_raw_data()
    post_csv_report()

    res = echoes_db.search(query={'test_apparatus.battery_id': battery_id,
                                  'test_results.capture_number': 71,
                                  'test_setting.input_channel': input_channel},
                           collection=cabinet)

    res_2 = echoes_db.find_one(query={'test_apparatus.battery_id': battery_id,
                                      'test_results.capture_number': 71,
                                      'test_setting.input_channel': input_channel},
                               collection=cabinet)




    pprint(res_2['test_results']['raw_data'][0]['result'])

    # pprint(res_2)
    # pprint(res)
    # for post in res:
    #     pprint(post)

    # echoes_db.delete(query={'test_apparatus.battery_id': battery_id,
    #                               'test_results.capture_number': 46,
    #                               'test_setting.input_channel': input_channel},
    #                        collection=cabinet)


    # for run in res_2['test_results']['raw_data']:
    #     if run['run'] == 60:
    #         pprint(res_2['test_results']['temperature'])

    echoes_db.close()


