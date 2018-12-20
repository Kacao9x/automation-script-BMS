from datetime import time
import pandas as pd
import subprocess



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



def _get_timestamp_from_filename( filename ):

    i = filename.split('-')

    if i[1] == 'temp':
        endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' \
                  + i[5] + ':' + i[6] + ':' + i[7]
        print ('endtime raw: ' + endtime)

    else:
        endtime = '2018' + '-' + i[4] + '-' + i[5] + ' ' \
                  + i[6] + ':' + i[7] + ':' + i[8]
        print ('endtime filtered: ' + endtime)

    return endtime


def post_csv_report():
    # this format captures objects instead of attributes
    # bucket= {"cars":[
    #     {"mercedes":["c","e","s"]},
    #     {"bmw":["5601", "5301"]},
    #     {"64":["suv","cabriolet"]}
    #             ]
    #
    #        }

    with open('data/' + filename) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    print (len(table.index))

    for col in range(1,3):
        print ('col %s' % str(col))

        bucket = {}

        bucket['test_apparatus'] = {
            'battery_id': 'TC05-H75',
            'transducer_id': 67143,
            'echoes_id': 'TC05'
        }

        bucket['test_setting'] = {
            'impulse-volt': 85,
            'vga_gain': 0.55,
            'delay_ms': 25,
            'sampling_rate': 7200000,
            'impulse_type': 'neg-bipolar',
            'input-channel': 'primary'
        }

        bucket['test_results'] = {}                                             # empty the json

        timest = _get_timestamp_from_filename( table['FileName'][col] )
        print (timest.split(' ')[0].split('-')[0] + '-' + timest.split(' ')[0].split('-')[1])
        bucket['timestamp'] = timest
        bucket['timestamp-day'] = timest.split(' ')[0].split('-')[2]
        bucket['timestamp-month'] = timest.split(' ')[0].split('-')[0] \
                                                    + '-' + timest.split(' ')[0].split('-')[1]

        bucket['test_results'] = {
            'temperature'       :   {
                'top'       :float(table['Temperature_top'][col]),
                'bottom'    :float(table['Temperature_bottom'][col])
            },
            'cap(mAh)'          :   float(table['cap(mAh)'][col]),
            'current'           :   float(table['current'][col]),
            'volt'              :   float(table['volt'][col]),
            'charging'          :   int(table['charging'][col])
        }

        data = list(table.iloc[col, 12:].values)                                # retrieve test value from the report
        bucket['test_results']['value']    = data

        echoes_db.insert_capture(record=bucket, collection='captures')


    print('completed uploading')

    echoes_db.close()
    return


def post_raw_data():
    cycle = 3
    cycle_id = 1

    while cycle_id < cycle + 1:
        oneRead, list_file = concat_all_data(tempC=False, search_key='cycle' +
                                                        str(cycle_id) + '-')
        print (list_file)

    return



print("Initializing database")
echoes_db       = database(database='echoes-testing')
echoes_db.mongo_db = 'captures'

filename = 'TC05-H75_181114_primary-sorted.csv'



address = '/media/'
if __name__ == '__main__':
    post_raw_data()


