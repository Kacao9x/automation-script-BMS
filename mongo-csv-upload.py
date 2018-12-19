from datetime import time
import pandas as pd


from lib.echoes_database import *


def _save_capture_to_Mongodb( cycleID=int, key=str, data=[], temper=bool,
                              record = {} ):
    ts = time.time()
    st = 'cycle' + str(cycleID + 1) + '-' + key + '-' \
         + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

    packet = {}
    packet['test_results'] = {}
    packet['test_setting'] = {}
    packet['test_apparatus'] = {}

    record = echoes_1.get_session_data()
    packet['test_results']['data'] = data
    packet['test_results']['cycle_number'] = cycleID + 1
    packet['test_results']['avg_number'] = key.split('-')[1]
    packet['test_results']['timestamp'] = st


    packet['test_setting']['impulseVoltage']= record['impulseVoltage']
    packet['test_setting']['impulseType']  = record['impulseType']
    packet['test_setting']['vgaGain']      = record['vgaGain']

    packet['test_apparatus']['session'] = 'Me02-H100'


    if temper:
        # tempC_1 = temp_sense_primary.get_average_temperature_celcius(16)
        # tempC_2 = temp_sense_secondary.get_average_temperature_celcius(16)
        packet['test_results']['temperature_1'] = \
            temp_sense_primary.get_average_temperature_celcius(16)
        packet['test_results']['temperature_2'] = \
            temp_sense_secondary.get_average_temperature_celcius(16)

    echoes_db.insert_capture(packet)
    return


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


def main():

    packet = {}
    packet['test_results'] = {}
    packet['test_setting'] = {}
    packet['test_apparatus'] = {}

    packet['test_apparatus']['SoH']         = '75'
    packet['test_apparatus']['battery_id']      = 'TC05'
    packet['test_apparatus']['transducer_id']   = '67143'
    packet['test_apparatus']['echo_id']         = 'TC05'


    with open('data/' + filename) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    # print (table.head().to_string())
    print (len(table.index))


    data, data_2 = [], []
    for col in range(1,2):
        # data = ( table.iloc[col, 12:20].values.item() )                                     # retrieve test value from the report
        # print (data)
        for x in range (10):
            data_2.append( table.loc[str(x)][col] )
        print data_2

        timest = _get_timestamp_from_filename( table['FileName'][col] )
        print (timest.split(' ')[0].split('-')[0] + '-' + timest.split(' ')[0].split('-')[1])
        packet['test_results']['timestamp'] = timest
        packet['test_results']['timestamp-day'] = timest.split(' ')[0].split('-')[2]
        packet['test_results']['timestamp-month'] = timest.split(' ')[0].split('-')[0] \
                                                    + '-' + timest.split(' ')[0].split('-')[1]

        packet['test_results']['temperature_top']   = table['Temperature_top'][col]
        packet['test_results']['temperature_bottom'] = table['Temperature_bottom'][col]
        packet['test_results']['cap(mAh)']          = table['cap(mAh)'][col]
        packet['test_results']['current']           = table['current'][col]
        packet['test_results']['volt']             	= table['volt'][col]
        packet['test_results']['charging']          = table['charging'][col]

        packet['test_results']['value']             = data_2
        print (packet['test_results']['value'])

    # echoes_db.insert_capture(record=packet, collection='captures')
    print('completed uploading')

    echoes_db.close()
    return


print("Initializing database")
echoes_db       = database(database='echoes-testing')
echoes_db.mongo_db = 'captures'

filename = 'TC05-H75_181114_primary-sorted.csv'


if __name__ == '__main__':
    main()