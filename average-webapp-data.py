import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd
import json, re
from pathlib import Path

from lib.echoes_signalprocessing import *


def sort_folder_by_name_universal(path, key):
    """
    Sort out EchOES data in numeric order
    :param path: the path to data directory
    :param key: keyword to filter file
    :return: a list of File in desired order
    """
    def tryint(s):
        try:
            return int(s)
        except:
            return s

    def alphanum_key(s):
        return [ tryint(c) for c in re.split('([0-9]+)', s.name) ]


    print (path)
    dirFiles = [i for i in path.glob(key)]
    print (dirFiles)

    dirFiles.sort( key=alphanum_key )
    print ('\ndirFiles {}, len {}'.format(dirFiles, len(dirFiles)))

    return dirFiles

def data_processing(key='*.json', remove_bad_samp=False, bandpass=True):
    """
    Processing the raw data in EchOES board and plot up the compiled signal
    for dianostic purpose
    :param key: (string) keyword to filter the data
    :param remove_bad_samp: (bool) A custom function to remove bad sample
    :param bandpass: (bool) To enable bandpass filter
    :return:
    """
    filter_concat       = pd.DataFrame()
    Fs = 7200000.0
    ped = 1E6/Fs                                                                # = 1.389e-1 convert s to microsec


    list_file = sort_folder_by_name_universal(Path(address), key)
    print (list_file)

    count = 0
    for cnt, oneFile in enumerate(list_file):
        count += 1

        strip_name = oneFile.name.split('_')
        captureID =  (strip_name[0].split('capture'))[1]
        print ('item {}, capture ID: {}'.format(cnt, captureID))


        with open(str(address / oneFile)) as json_file:
            echo_data = json.load(json_file)
        json_file.close()

        if echo_data['raw_data']:
            echo_data['raw_data'] = [i for i in echo_data['raw_data'] if i != None] # Remove a null in data array

            raw_set_pd = pd.DataFrame()
            for idx, raw in enumerate(echo_data['raw_data']):
                single_set = pd.DataFrame({idx: raw})                           # concat all data set into a singl dataframe
                raw_set_pd = pd.concat([raw_set_pd, single_set], axis=1,
                                       ignore_index=True)                       # Contruct a data frame for all raw signal

            [row, column] = raw_set_pd.shape                                    # Retrieve the size of data frame. Row = num of data pts

            avg = np.mean(raw_set_pd, axis=1)  # average 64 captures
            if bandpass:
                avg_bandpass = echoes_dsp.apply_bandpass_filter(avg, 300000,
                                                                1200000, 51)    # apply bandpass



            ''' -------   plot the avg for checking clean data    ---- '''
            x_1 = np.arange(0, ped * row, ped)
            plt.title(plot_title)
            plt.plot(x_1, avg_bandpass, label='capture {}'.format(int(captureID)))
            plt.xlim(0,70)                                                      # Limit the x-scale to 70us
            plt.grid('on')                                                      # display the grid on plot
            plt.legend(loc='upper right')                                       # select location to display description

            # plt.show()                                                          # plot an individual signal
        else:
            print ('no data')
            avg_bandpass = []

        '''Save all average data into Dataframe'''

        avg_filter = pd.DataFrame({captureID : avg_bandpass})                   # Construct data frame for average data
        filter_concat = pd.concat([filter_concat, avg_filter], axis=1)

    plt.interactive(False)
    plt.show()

    ''' Save Processed Data to csv '''
    filter_concat = filter_concat.T
    filter_concat.to_csv(Path(address + captureID + '-bandpass-avg.csv'))
    
    print ("complete")
    return


#==============================================================================#
def main():
    data_processing(key='*.json', bandpass=True)
    return

#==============================================================================#
collection_name      = 'Downloads'
plot_title  = '{}| bandpass [0.3 - 1.2] Mhz | Gain 0.55'.format(collection_name)

address     = '/home/kacao/{}'.format(collection_name)
echoes_dsp  = echoes_signals( 7200000.0 )


if __name__ == '__main__':
    main()