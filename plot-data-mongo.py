import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
from lib.echoes_signalprocessing import *
from lib.echoes_models import *
from lib.echoes_database import *

import json
from lib.commandline import *
from datetime import datetime, timedelta
from scipy.fftpack import fft, rfft, ifft


def find_outlier(aCapture_signal):
    return


def remove_bad_samples(aCapture_signal):
    # These constants are sensitive to VGA change. VGA default is 0.55
    START_DATA_PTS = 58  # evaluate signal after 8us
    HIGH_BOUND = 0.15  # 0.013  # arbitrary value for Toyota cell
    LOW_BOUND = 0.001

    idx = []
    for i, sample in enumerate(aCapture_signal):
        # x_arr = np.absolute(signal)                                         #compare standard deviation with threshold

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


def check_data_quality_mongo(remove_bad_samp, collection):
    """
    This functions detect bad sampling in a capture.
    The first method detect a flat curve
    Second method detect a time shift more than 2 data points
    """

    echoes_db = database(database='echoes-captures')

    query = {
        'capture_number': {'$gte': 1243},
    }

    # 1: ascending, -1: descending, 0: hidden
    projection = {
        # 'echoes_id':1,
        # 'test_examiner':0,
        # 'transducer_id':0,
        # 'test_setting.master.temp_sense_a_1': 1,
        'timestamp': 1,
        'capture_number': 1,
        'input_side': 1,
        'raw_data': 1,
        'test_setting.master': 1,
        'source': 1,
        '_id': 0,

    }
    data_cursor = echoes_db.search(query=query, projection=projection,
                                   collection=collection)

    count = 0
    for aCapture in data_cursor:
        count += 1
        print("capture ID: {}\t".format(aCapture['capture_number']))

        # aCapture['timestamp'] = aCapture['timestamp'] - timedelta(hours=4)      #convert UTC to EDT timezone

        time_obj = datetime.strptime(aCapture['timestamp'],
                                     '%Y-%m-%dT%H:%M:%S')  # convert to time object for calculation
        aCapture['timestamp'] = time_obj - timedelta(
            hours=4)  # convert UTC to EDT timezone

        aCapture['raw_data'] = [i for i in aCapture['raw_data'] if i != None]
        if remove_bad_samp:
            aCapture['raw_data'] = remove_bad_samples(aCapture['raw_data'])

        print("saving data to disk\n")
        # Used to separate dataset doesn't have input channel info
        # if count % 2 == 1:
        #     path = address + 'primary/'
        # else:
        #     path = address + 'secondary/'

        if aCapture['input_side'] == 1:
            path = addr_to_extract + 'primary-upload/'
        else:
            path = addr_to_extract + 'secondary-upload/'

        with open(path + 'capture{}-{}.json'.format(aCapture['capture_number'],
                                                    aCapture['timestamp']),
                  'w') as writeout:
            aCapture['timestamp'] = aCapture['timestamp'].strftime(
                '%Y-%m-%dT%H:%M:%S')
            writeout.write(json.dumps(aCapture))
        writeout.close()

    echoes_db.close()

    return


def plot_signal_from_mongo(collection):
    echoes_db = database(database='echoes-captures')
    query = {
        'capture_number': {'$lt': 8, '$gt': 3}
    }
    projection = {
        'raw_data': 1
        # 'temperature':1,
        # 'echoes_setting':1
    }
    data_cursor = echoes_db.search(query=query, projection=projection,
                                   collection=collection)

    for aCapture in data_cursor:
        # pprint (aCapture)
        sample = 0
        # print (len(aCapture['raw_data'][0]))
        while sample < len(aCapture['raw_data']):
            dt = 1.38888E-1  # float(1/7200000)
            row = 512
            x = np.arange(0, dt * row, dt)
            filter_data = echoes_dsp.apply_bandpass_filter(
                aCapture['raw_data'][sample],
                300000, 1000000, 51)
            plt.figure(1)
            plt.title('Signal Plot')
            plt.interactive(False)
            plt.plot(x, filter_data,
                     label='Sample 0{} '.format(str(sample + 1)))
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

    key = '.json'
    # list_file = display_list_of_file(address, key)
    list_file = display_list_of_file(address, key)

    ''' Loop through every sample data in a read/capture '''
    for captureID, filename in enumerate(list_file):
        with open(address + filename) as json_file:
            aCapture = json.load(json_file)
        json_file.close()

        print("capture ID: {}\t".format(aCapture['capture_number']))

        # strp = (aCapture['timestamp']).split('-04')[0]
        # echoes_endtime = datetime.strptime(strp,
        #                                    '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        time_object = datetime.strptime(aCapture['timestamp'],
                                        '%Y-%m-%dT%H:%M:%S-04:00')
        # aCapture['timestamp'] = time_object - timedelta(hours=4)                # convert UTC to EDT timezone

        aCapture['raw_data'] = [i for i in aCapture['raw_data'] if i != None]
        aCapture['raw_data'] = remove_bad_samples(aCapture['raw_data'])

        with open(
                address + 'capture{}-{}.json'.format(aCapture['capture_number'],
                                                     aCapture['timestamp']),
                'w') as writeout:
            aCapture['timestamp'] = aCapture['timestamp'].strftime(
                '%Y-%m-%dT%H:%M:%S')
            # aCapture['input_side'] = 2
            writeout.write(json.dumps(aCapture))
        writeout.close()

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
    print(list_file)

    ''' Loop through every sample data in a read/capture '''
    for idx, filename in enumerate(list_file):
        # with open(address + filename) as json_file:
        with open(str(address / filename)) as json_file:
            aCapture = json.load(json_file)
        json_file.close()

        print("capture ID: {}\t".format(aCapture['capture_number']))

        # aCapture['input_side'] = input_sd
        # aCapture['source'] = 'echoes-a'
        if aCapture['timestamp'] is not None:
            aCapture['timestamp'] = datetime.strptime(aCapture['timestamp'],
                                                      '%Y-%m-%dT%H:%M:%S')

        count += 1
        insert_list.append(aCapture)

        # insert a batch of 100 obj or the end of filelist
        if count >= batch_size or idx == len(list_file) - 1:
            print('idx {}'.format(idx))
            result = echoes_db.insert_multiple(insert_list,
                                               collection=collection)
            print(result)

            count = 0
            insert_list = []

    echoes_db.close()
    return


# ==============================================================================#
# ======================== MAIN FUNCTION ======================================-#
def main():
    global backgrd

    """
        (1) Check data quality: detect flat curve, missing echo
    """
    # check_data_quality_json()
    # check_data_quality_mongo(remove_bad_samp=True, collection=collection)
    # """
    # (2) plot avg of each capture. Save avg (mean) to csv file
    # """
    plot_signal_from_json_new(remove_bad_samp=True, bandpass=True,
                              backgrd_subtract=False)
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


# ==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

# is_64bits = sys.maxsize > 2**32
# print ('is 64bit {}'.format(is_64bits))
# import struct
# print(struct.calcsize("P") * 8)

dtb = 'Tuna-Can'
collection = 'Toyota'

input_side = 'Natural-Rubber-Th,062_secondary'
input_sd = 1 if 'primary' in input_side else 2
plot_title = '{}| bandpass [0.3 - 1.2] Mhz | Gain 0.55'.format(input_side)

# addr_to_extract = '/media/kacao/Ultra-Fit/titan-echo-boards/Lenovo/Lenovo_1/primary_1/'
address = '/media/kacao/EchoesData/unCategorized/{}/'.format(input_side)
# address = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/Me05-190227/primary_json/')


echoes_dsp = echoes_signals(7200000.0)
if __name__ == '__main__':
    main()
    # elapsed_time = timeit.timeit(main, number=100) / 100
    # print(elapsed_time)