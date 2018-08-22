
import matplotlib.pyplot as plt
import numpy as np
import os, subprocess
import thLib as th
import glob
import pandas as pd
from scipy.signal import filtfilt, firwin, upfirdn



#==============================================================================#

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


def count_good_value ( x ):
    boundary = 0.025
    count = 0
    for i in range (0, len(x)):
        if boundary < abs (x[i]):
            count += 1

    return count

def find_data_std( x ):
    x_arr = np.array( x )
    x_arr = np.absolute( x_arr )
    return np.std( x_arr[50:-1], ddof=1 )


def concat_custom_data( ):

    file_name = pd.DataFrame()
    list_file = display_list_of_file('cycle')
    for filename in list_file:
    # for filename in glob.glob(os.path.join(address, "*.dat")):
        my_file = open(filename)
        y_str = my_file.read()
        y_str = y_str.splitlines()
        y = []
        for i, num in enumerate(y_str):
            if i < len(y_str) - 1:
                y.append(float(num))
        y = pd.DataFrame(y)
        file_name = pd.concat([file_name, y], axis=1, ignore_index=True)
    # with 0s rather than NaNs
    file_name = file_name.fillna(0)

    return file_name

def concat_all_data( ):
    file_name = pd.DataFrame()
    tC = []
    list_file = display_list_of_file('cycle')
    print (list_file)
    for filename in list_file:
    # for filename in glob.glob(os.path.join(address, "*.dat")):
        my_file = open(address + filename)
        y_str = my_file.read()
        y_str = y_str.splitlines()
        data = []
        for i, num in enumerate(y_str):
            if i < len(y_str) -1 :
                data.append(float(num))

            else:
                # print (len(num.split() ))
                if len( num.split() ) > 2:
                    temp = num.rstrip().split('Temperature:')[1]
                    temp = temp.split('oC')[0]
                    tC.append(float(temp))
                else:
                    data.append(float(num))

        # check good read and bad read
        count = count_good_value(data)
        print ('Cycle %s: %s' % (str(i + 1), str(count)))
        std_value = find_data_std(data)
        if (count > 15):
            print ('solution 1 works')
        if (std_value > 0.0020):
            print ('good value')
        print ('value: %s' % str(std_value))

        # concat all data set into a singl dataframe
        data = pd.DataFrame( data )
        file_name = pd.concat([file_name, data], axis=1, ignore_index=True)


    # with 0s rather than NaNs
    file_name = file_name.fillna(0)

    return file_name, tC




#==============================================================================#
#======================== MAIN FUNCTION =======================================#
def main ():

    testResults, tC = concat_all_data()

    plt.figure(1)
    plt.plot(tC)
    plt.title('Temperature vs Cycle')
    plt.interactive(True)
    plt.show()

    print (testResults.shape)
    [row, column] = testResults.shape

    # fs = 7200000*4
    # nyq_rate = fs*0.5
    # filterlen = 301
    # b = firwin(filterlen, 100000.0/fs, window="hamming", pass_zero=False)
    # i = 0
    # while i < column:
    #     file_name.loc[:, i] = filtfilt(b, 1.0, file_name.loc[:, i])
    #     i = i+1
    # amp_upsample = pd.DataFrame()
    # upsample_rate = 4
    # fs = fs*4
    # nyq_rate = fs*0.5
    # b = firwin(101, 1.0 / upsample_rate)
    # i = 0
    # while i < column:
    #     y = pd.DataFrame(upfirdn(b, file_name.loc[:, i], up=upsample_rate))
    #     amp_upsample = pd.concat([amp_upsample, y], axis=1, ignore_index=True)
    #     i = i+1
    #
    # print(amp_upsample.shape)
    #
    # N = len(amp_upsample.loc[:, 0])
    # dt = float(1/fs)
    # print (dt)
    #
    # x = np.arange(0, dt*N, 3.47222222e-8)

    i = 1
    dt = float(1/7200000)
    x = np.arange(0, 3.47222222e-8*row, 3.47222222e-8)

    plt.figure(2)
    plt.title('SoC vs Time')
    plt.interactive(False)
    while i < column+1:
        #plt.subplot(column/2, 2, i)
        #change the integers inside this routine as (number of rows, number of columns, plotnumber)
        plt.plot(testResults.loc[:, i-1])
        #plt.xlim((0, 0.00005))
        i = i+1

    # plt_2.legend()
    plt.show()

#==============================================================================#
address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder


if __name__ == '__main__':
    main()