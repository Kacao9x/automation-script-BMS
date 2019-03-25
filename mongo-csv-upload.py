from datetime import time
import pandas as pd
import subprocess
from pprint import pprint
from bson import ObjectId
import json, logging, random


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


def _get_timestamp( filename ):
    timest = {}
    i = filename.split('-')

    (timest['year'], timest['month'], timest['day'])    = int(i[2]), int(i[3]), int(i[4])
    (timest['hour'], timest['min'], timest['sec'])      = int(i[5]), int(i[6]), int(i[7])

    # (timest['year'], timest['month'], timest['day']) = int(i[3]), int(
    #     i[4]), int(i[5])
    # (timest['hour'], timest['min'], timest['sec']) = int(i[6]), int(i[6]), int(
    #     i[8])


    return timest

def _get_cycle_number( filename ):
    name_strip = filename.split('-')
    cycle = name_strip[0].split('cycle')[1]
    print cycle
    return int(cycle)


def post_csv_report():

    global bucket
    with open(address + filename) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    print (len(table.index))

    cycle = len(table.index)
    cycle_id = 70

    while cycle_id < cycle + 1:

        # if cycle_id == 127:
        #     cycle_id = 128
        row = cycle_id - 1                                                      # row in PANDAS table start from 0

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
                'SoH'           : float(table['SoH'][cycle_id - 1]),
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

    cycle = 150
    cycle_id = 1

    while cycle_id < cycle + 1:


        if pd.isnull(table.at[cycle_id-1,'volt']) or pd.isnull(table.at[cycle_id-1,'0']):
            print ('IGNORE %s' % str(cycle_id))
            cycle_id += 1
            continue


        bucket = {}

        timest = _get_timestamp(table['FileName'][cycle_id - 1])
        bucket['timestamp'] = datetime.datetime(timest['year'], timest['month'],
                                                timest['day'], timest['hour'],
                                                timest['min'], timest['sec'])


        bucket['battery_id']    = battery_id
        bucket['transducer_id'] = {
            'primary'       : 67143,
            'secondary'     : 0
        }

        bucket['echoes_id']     = 'echoes-a'
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

        bucket['SoH']           = float(table['SoH'][cycle_id - 1])
        bucket['SoC']           = float(table['SoC'][cycle_id - 1])
        bucket['temperature']  = {
            'top'   : float(table['Temperature_top'][cycle_id -1]),
            'bottom': float(table['Temperature_bottom'][cycle_id -1])
        }
        bucket['battery_details']  = {
            'power(Wh)'     : float(table['power(Wh)'][cycle_id -1]),
            'cap(Ah)'       : float(table['cap(Ah)'][cycle_id -1]),
            'current'       : float(table['current'][cycle_id -1]),
            'volt'          : float(table['volt'][cycle_id -1]),
            'charging'      : int(table['charging'][cycle_id -1])
        }


        row = cycle_id - 1                                                  # row in PANDAS table start from 0

        data = list(table.iloc[row, -512 : ].values)
        capture_num = _get_cycle_number( table['FileName'][cycle_id - 1])

        bucket['average_data'] = data
        bucket['capture_number'] = capture_num
        bucket['raw_data'] = []

        # pprint (bucket['capture_number'])

        oneRead, list_file = concat_all_data(tempC=False, search_key='cycle' +
                                            str(capture_num) + '-')

        if not list_file:
            cycle_id +=1
            continue


        [row, column] = oneRead.shape
        print (column)

        avgPos = 1
        while avgPos < column + 1:
            value = list(oneRead.loc[:, avgPos - 1].values)
            # print (value)
            
            
            bucket['raw_data'].append(
                value
                # {'run': avgPos, 'value': value}
            )
            

            avgPos += 1  # go to next column


        res = echoes_db.insert_capture(record=bucket, collection=cabinet)
        print (res)

        # try:
        #     res = echoes_db.insert_capture(record=bucket, collection=cabinet)
        #     print (res)
        # except pymongo.errors.ConnectionFailure, e:
        #     print ('No connection: %s' % e)
        cycle_id += 1


    return


#==============================================================================#

battery_id      = 'TC04'    #input('Input Battery ID: \n')
SoH             = 74        #input('Input SoH value: \n')
date            = 181113    #input('Testing date: \n')

input_channel   = 'secondary'
cabinet         = 'tuna-can-testing'
examiner        = 'Khoi'
project         = 'Phase1-Build_SoH_Model'


print("Initializing database")
echoes_db       = database(database='echoes-captures')
echoes_db.mongo_db = cabinet



filename = battery_id + '-H' + str(SoH) + '_' + str(date) + '_' +input_channel + '-sorted.csv'
bucket = {}
address = '/media/kacao/Ultra-Fit/titan-echo-boards/Echo-A/TC04-H74_181113/' + input_channel + '/'
#
#

class Test(unittest.TestCase):


    def test_random(self):

        print('checking mismatch query data vs csv data')

        battery_id = 'TC32'  # input('Input Battery ID: \n')
        SoH = 86.28  # input('Input SoH value: \n')
        date = 190302  # input('Testing date: \n')

        input_channel = 'secondary'
        cabinet = 'tuna-can-official'


        with open(address + filename) as outfile:
            table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
        outfile.close()

        db = database(database='echoes-captures')

        db.insert_capture({'name': 'kacao-test'}, collection='tuna-can')

        rad_test = [65, 100, 150]
        # cycle_num = _get_cycle_number( table['FileName'][index - 1])


        for cycle_num in rad_test:
            res = db.find_one({'battery_id': battery_id,
                               'capture_number': cycle_num,
                               'test_setting.input_channel': input_channel},
                              collection=cabinet)

            if res is None:
                continue


            check_volt = (res['battery_details']['volt'] == table['volt'][cycle_num - 1])
            print('voltage: ' + str(check_volt))
            self.assertEqual(check_volt, True)

            check_cap = (res['battery_details']['cap(Ah)']) == table['cap(Ah)'][
                cycle_num - 1]
            print('cap: ' + str(check_cap))
            self.assertEqual(check_cap, True)

            # check_name = ( _get_cycle_number(table['Filename'][cycle_num - 1]) == cycle_num)
            # self.assertEqual(check_name, True)
        #
        #
        #     check_data_1 = (res['average_data'][0]) == table['0'][cycle_num - 1]
        #     print(res['average_data'][0])
        #     print(table['0'][cycle_num - 1])
        #     print('data_1 match: ' + str(check_data_1))
        #     self.assertEqual(check_data_1, True)
        #
        #     check_data_512 = (res['average_data'][511]) == table['511'][cycle_num - 1]
        #     print('data_512 match: ' + str(check_data_512))
        #     self.assertEqual(check_data_512, True)


    echoes_db.close()


if __name__ == '__main__':

    # battery_id = 'TC32'  # input('Input Battery ID: \n')
    # SoH = 86.28  # input('Input SoH value: \n')
    # date = 190302  # input('Testing date: \n')
    #
    # input_channel = 'secondary'
    # cabinet = 'tuna-can-official'
    # examiner = 'Khoi'
    # project = 'Phase1-Build_SoH_Model'
    #
    # print("Initializing database")
    # echoes_db = database(database='echoes-captures')
    # echoes_db.mongo_db = cabinet
    #
    # filename = battery_id + '-H' + str(SoH) + '_' + str(
    #     date) + '_' + input_channel + '-sorted.csv'
    # bucket = {}
    # address = '/media/kacao/Ultra-Fit/titan-echo-boards/Echo-A/TC32-H86.28_190302/' + input_channel + '/'

    # unittest.main()


    post_raw_data()

    # echoes_db.rename_field('battery_details.power(mWh)', 'battery_details.power(Wh)', collection=cabinet)

    # echoes_db.remove_field('average_data', collection=cabinet)

    # post_csv_report()

    # echoes_db.createIndex( [( 'test_apparatus.battery_id', pymongo.ASCENDING )],
    #                         unique=False, collection=cabinet)
    # echoes_db.createIndex( [( 'test_results.SoH', pymongo.ASCENDING )],
    #                         unique=False, collection=cabinet)
    # echoes_db.createIndex( [( 'timestamp', pymongo.ASCENDING )],
    #                         unique=True, collection=cabinet)


    # res = echoes_db.search(query={'battery_id': battery_id,
    #                               'test_setting.input_channel': input_channel},
    #                        collection=cabinet)
    #
    # res_2 = echoes_db.find_one(query={'battery_id': battery_id,
    #                                   'capture_number': 76,
    #                                   'test_setting.input_channel': input_channel},
    #                            collection=cabinet)
    #
    # start   = datetime.datetime(2019,3,4,4,24,10)
    # end     = datetime.datetime(2019,3,4,4,55,59)
    # res_3 = echoes_db.search(query={"capture_number": {'$gte':129}}, collection=cabinet)
    # res_4 = echoes_db.search(query={'timestamp': {'$gte':start,'$lt': end}}, collection=cabinet).sort({'timestamp': -1})


    # for post in res_2:
    #     pprint(post)
    # pprint(res_2)
    # pprint(res)
    # for post in res:
    #     pprint(post)


    ## echoes_db.delete(query={'battery_id': battery_id,
    #                         'test_setting.input_channel': input_channel},
    #                        collection=cabinet)

    print('checking mismatch query data vs csv data')

    with open(address + filename) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    db = database(database='echoes-captures')
    rad_test = [65, 100, 150]
    # cycle_num = _get_cycle_number( table['FileName'][index - 1])

    for cycle_num in rad_test:
        res = db.find_one({'battery_id': battery_id,
                           'capture_number': cycle_num,
                           'test_setting.input_channel': input_channel},
                          collection=cabinet)

        if res is None:
            continue

        check_volt = (res['battery_details']['volt'] == table['volt'][
            cycle_num - 1])
        print('voltage: ' + str(check_volt))
        # self.assertEqual(check_volt, True)

        check_cap = (res['battery_details']['cap(Ah)']) == table['cap(Ah)'][
            cycle_num - 1]
        print('cap: ' + str(check_cap))
        # self.assertEqual(check_cap, True)
    #
    #     check_name = (_get_cycle_number(
    #         table['Filename'][cycle_num - 1]) == cycle_num)
    #     # self.assertEqual(check_name, True)
    #
    #     check_data_1 = (res['average_data'][0]) == table['0'][cycle_num - 1]
    #     print(res['average_data'][0])
    #     print(table['0'][cycle_num - 1])
    #     print('data_1 match: ' + str(check_data_1))
    #     # self.assertEqual(check_data_1, True)
    #
    #     check_data_512 = (res['average_data'][511]) == table['511'][
    #         cycle_num - 1]
    #     print('data_512 match: ' + str(check_data_512))
    #     # self.assertEqual(check_data_512, True)

    echoes_db.close()


