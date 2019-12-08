import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import sys, json
from datetime import datetime,timedelta

from lib.echoes_signalprocessing import *
from lib.echoes_models import *
from lib.commandline import *

__SAMPLING_RATE__   = 7200000.0
__SORT_KEY__        = '*.json'


class Preprocessing_Data(object):

    def __init__(self, address, chunkSize):

        self.echoes_dsp = echoes_signals( __SAMPLING_RATE__ )
        self.data_folder = Path(address)
        # check if the address exists #

        self.chunkSize = chunkSize
        return

    @staticmethod
    def _sort_file_by_name(address=Path(), key=''):
        def tryint(s):
            try:
                return int(s)
            except:
                return s

        def alphanum_key(s):
            # int_sort_list = []
            # for c in re.split('([0-9]+)', s.name):
            #     int_sort_list.append(tryint(c))
            # return int_sort_list
            return [tryint(c) for c in re.split('([0-9]+)', s.name)]

        # print ('path: {}'.format(path))
        # dirFiles = (os.listdir(os.path.join(path, key)))  # list of directory files

        print(address)
        dirFiles = [i for i in address.glob(key)]
        print(dirFiles)

        dirFiles.sort(key=alphanum_key)
        print('\ndirFiles {}, len {}'.format(dirFiles, len(dirFiles)))

        return dirFiles


    def sort_file_in_order(self):
        key = __SORT_KEY__
        list_file = self._sort_file_by_name(self.data_folder, key)           # sort out the datafile in alphabet order
        print(list_file)
        return list_file

    def detect_outlier(self, aCapture=[]):
        '''
        find an outlier in sampling data using standard deviation
        :param aCapture_signal: an array of all sampling data (64 samples/captures)
        :return: an array list of good sampling data in a single capture
        '''
        ''' https://towardsdatascience.com/5-ways-to-detect-outliers-that-every-data-scientist-should-know-python-code-70a54335a623'''
        # These constants are sensitive to VGA change. VGA default is 0.55
        START_DATA_PTS = 58  # evaluate signal after 8us
        HIGH_BOUND = 0.15  # arbitrary value for TunaCan
        LOW_BOUND = 0.001

        index_bad_sampling = []                                                 # an index list of bad samples
        for i, sample in enumerate(aCapture):
            # x_arr = np.absolute(signal)                                       #compare standard deviation with threshold

            std_value = np.std(sample[START_DATA_PTS:], ddof=1)
            # print ('std val: {}'.format(std_value))
            if std_value > HIGH_BOUND or std_value < LOW_BOUND:
                index_bad_sampling.append(i)
            else:
                None
        print("bad sampling {}".format(index_bad_sampling))

        return index_bad_sampling

    def remove_bad_sample(self, aCapture=[], idx=[]):
        aCapture_signal = np.delete(aCapture, idx, axis=0).tolist()             # delete bad sampling by index
        return aCapture_signal


    def remove_background(self, aCapture=[], backgrd=[]):
        return aCapture


    def process_json_file(self, removeBadSample=False, bandpass=False,
                          listFiles=[]):
        """
        Remove the outlier from sampling data. Average and apply bandpass filter
        Plot up the entire dataset and save it into .csv file.
        """

        raw_signal_dict = {}
        avg_filtered_dict = {}
        temp_combined_dict = {}


        period = 1E6/__SAMPLING_RATE__                                          #1.38888889e-1  # period if micro-second
        chunk_count = 0  # threshold to break the dataset into chunks

        for cnt, oneFile in enumerate(listFiles):
            chunk_count += 1

            strip_name = oneFile.name.split('_')
            # print (strip_name)
            captureID = (strip_name[0].split('capture'))[
                1]  # retrieve the capture number from filename

            print('item {}, capture ID: {}'.format(cnt, captureID))

            with open(str(address / oneFile)) as json_file:
                echo_data = json.load(json_file)
            json_file.close()


            if echo_data['raw_data']:
                echo_data['raw_data'] = [i for i in echo_data['raw_data'] if
                                         i != None]  # remove NULL data from the raw-data list
                if removeBadSample is True:
                    echo_data['raw_data'] = self.remove_bad_sample(echo_data['raw_data'])

                raw_set_pd = pd.DataFrame()
                for idx, raw in enumerate(echo_data['raw_data']):
                    single_set = pd.DataFrame({idx: raw})                       # concat all data set into a singl dataframe
                    raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
                                           ignore_index=True)

                [row,column] = raw_set_pd.shape                                 # get the size of the dataframe

                avg = np.mean(raw_set_pd, axis=1)  # average 64 captures
                if bandpass:
                    avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000,
                                                                    1200000, 51)# apply bandpass

                # ''' -------   plot the avg for checking clean data    ---- '''
                # x_1 = np.arange(0, period * row, period)
                # plt.title(plot_title)
                # plt.plot(x_1, avg_bandpass,
                #          label='capture {}'.format(int(captureID)))
                # plt.grid('on')
                # plt.legend(loc='upper right')

            else:
                print('no raw_data')
                avg = []
                avg_bandpass = []

            ''' Save all data as dict, then convert it to dataframe'''
            avg_filtered_dict.update({captureID: avg_bandpass})
            raw_signal_dict.update({captureID: avg})


            if chunk_count > self.chunkSize or cnt == len(listFiles) - 1:
                filtered_concat = pd.DataFrame.from_dict(avg_filtered_dict,
                                                         orient='index')
                raw_data_concat = pd.DataFrame.from_dict(raw_signal_dict,
                                                         orient='index')
                __avgFilteredData__ = pd.DataFrame.from_dict(temp_combined_dict,
                                                             orient='index',
                                                             columns=['capture_number', 'temp_1'])
                __avgRawData__ = pd.DataFrame.from_dict(temp_combined_dict,
                                                        orient='index',
                                                        columns=['capture_number', 'temp_1'])

                # print (filtered_concat.head().to_string())
                ''' Concat single capture dataframe to the compiled one'''
                __avgFilteredData__ = pd.concat(
                    [__avgFilteredData__, filtered_concat], axis=1)
                __avgRawData__ = pd.concat(
                    [__avgFilteredData__, raw_data_concat], axis=1)
                __avgFilteredData__.to_csv(Path(address + data_folder +
                                                '-{}-{}-filter.csv'.format(
                                                    cnt + 1 - chunk_count,
                                                    cnt + 1)))
                __avgRawData__.to_csv(Path(address + data_folder +
                                           '-{}-{}-raw.csv'.format(
                                               cnt + 1 - chunk_count,
                                               cnt + 1)))
                avg_filtered_dict = {}
                temp_combined_dict = {}
                chunk_count = 0

                del __avgFilteredData__
                print('count {}, cnt {}'.format(chunk_count, cnt))

                # plt.show()

        print("complete")

        return

    def plot_fft(self, df):
        period = 1E6 / __SAMPLING_RATE__  # 1.38888889e-1  # period if micro-second
        return

    def plot_time_series(self, df):
        period = 1E6 / __SAMPLING_RATE__  # 1.38888889e-1  # period if micro-second

        # plot dataframe
        # ''' -------   plot the avg for checking clean data    ---- '''
        # x_1 = np.arange(0, period * row, period)
        # plt.title(plot_title)
        # plt.plot(x_1, avg_bandpass,
        #          label='capture {}'.format(int(captureID)))
        # plt.grid('on')
        # plt.legend(loc='upper right')
        return

    def generate_report(self,type='', datafr=pd.DataFrame()):
        if type == 'csv':
            pass
        elif type == 'xlsx':
            pass
        else:
            print ('file not supported')
            return


class Test(unittest.TestCase):
    data_folder = '/media/kacao/EchoesData/Tuna-Can-2/TC38-E2_secondary/'
    processData = Preprocessing_Data(address=data_folder, chunkSize=700)


    def test_sort_file(self, processData = processData):
        dirFiles = processData.sort_file_in_order()
        print (dirFiles)

    def test_compile_data(self, processData = processData):

        pass







def plot_signal_from_json(remove_bad_samp=False, bandpass=False):
    """
    Remove the outlier from sampling data. Average and apply bandpass filter
    Plot up the entire dataset and save it into .csv file.
    """
    raw_signal_dict         = {}
    avg_filtered_dict       = {}
    temp_combined_dict      = {}

    key = '*.json'
    list_file = sort_folder_by_name_universal(Path(address), key)               # sort out the datafile in alphabet order
    print(list_file)

    period = 1.38888889e-1                                                      # period if micro-second
    chunk_size = 0                                                              # threshold to break the dataset into chunks
    for cnt, oneFile in enumerate(list_file):
        chunk_size += 1

        strip_name = oneFile.name.split('_')
        # print (strip_name)
        captureID = (strip_name[0].split('capture'))[1]                         # retrieve the capture number from filename

        print('item {}, capture ID: {}'.format(cnt, captureID))

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
                                     i != None]                                 # remove NULL data from the raw-data list
            if remove_bad_samp is True:
                echo_data['raw_data'] = remove_bad_samples(echo_data['raw_data'])

            raw_set_pd = pd.DataFrame()
            for idx, raw in enumerate(echo_data['raw_data']):
                single_set = pd.DataFrame({idx: raw})                           # concat all data set into a singl dataframe
                raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
                                       ignore_index=True)

            [row, column] = raw_set_pd.shape                                    # get the size of the dataframe

            avg = np.mean(raw_set_pd, axis=1)  # average 64 captures
            if bandpass:
                avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000,
                                                                1200000, 51)    # apply bandpass



            ''' -------   plot the avg for checking clean data    ---- '''
            x_1 = np.arange(0, period * row, period)
            plt.title(plot_title)
            plt.plot(x_1, avg_bandpass, label='capture {}'.format(int(captureID)))
            plt.grid('on')
            plt.legend(loc='upper right')

        else:
            print('no raw_data')
            avg = []
            avg_bandpass = []

        ''' Save all data as dict, then convert it to dataframe'''
        avg_filtered_dict.update({captureID: avg_bandpass})
        raw_signal_dict.update({captureID : avg})
        temp_combined_dict.update({captureID: tempC})

        if chunk_size > 715 or cnt == len(list_file) - 1:
            filtered_concat = pd.DataFrame.from_dict(avg_filtered_dict,
                                                   orient='index')
            raw_data_concat = pd.DataFrame.from_dict(raw_signal_dict,
                                                     orient='index')
            __avgFilteredData__ = pd.DataFrame.from_dict(temp_combined_dict,
                                                    orient='index', columns=['temp_1'])
            __avgRawData__      = pd.DataFrame.from_dict(temp_combined_dict,
                                                    orient='index', columns=['temp_1'])

            # print (filtered_concat.head().to_string())
            ''' Concat single capture dataframe to the compiled one'''
            __avgFilteredData__ = pd.concat([__avgFilteredData__, filtered_concat], axis=1)
            __avgRawData__      = pd.concat([__avgFilteredData__, raw_data_concat], axis=1)
            __avgFilteredData__.to_csv(Path(address + data_folder +
                                      '-{}-{}-filter.csv'.format(cnt + 1 - chunk_size,
                                                          cnt + 1)))
            __avgRawData__.to_csv(Path(address + data_folder +
                                            '-{}-{}-raw.csv'.format(cnt + 1 - chunk_size,
                                                                cnt + 1)))
            avg_filtered_dict = {}
            temp_combined_dict = {}
            chunk_size = 0

            del __avgFilteredData__
            print('count {}, cnt {}'.format(chunk_size, cnt))

            plt.show()

    print("complete")
    return

#==============================================================================#
#======================== MAIN FUNCTION ======================================-#
def main ():
    plot_signal_from_json(remove_bad_samp=True, bandpass=True, backgrd_subtract= False)
    return
#==============================================================================#

data_folder      = 'TC09-E2_primary'
input_sd        = 1 if 'primary' in data_folder else 2
plot_title  = '{}| bandpass [0.3 - 1.2] Mhz | Gain 0.55'.format(data_folder)


address     = '/media/kacao/EchoesData/Tuna-Can/{}/'.format(data_folder)

echoes_dsp = echoes_signals( 7200000.0 )
if __name__ == '__main__':
    main()
