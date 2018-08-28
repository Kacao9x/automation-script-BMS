
import matplotlib.pyplot as plt
import numpy as np
import os, subprocess
import thLib as th
import glob
import pandas as pd
from scipy.interpolate import interp1d


#=============================================================================#

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
#=============================================================================#

# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls '+ address +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name


def count_good_value ( x ):
    boundary = 0.025        #pick a threshold from the plot. removing DC offset may affect the value
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


def concat_all_data(cycle=int):
    global bad_data
    file_name = pd.DataFrame()
    tC = []

    list_file = display_list_of_file('cycle'+str(cycle)+'-')
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

        # # check good read and bad read
        # count = count_good_value(data)
        # print ('Cycle %s: %s' % (str(i + 1), str(count)))
        # std_value = find_data_std(data)
        # print ('value: %s' % str(std_value))
        #
        # if (count > 15 and std_value > 0.0020):
        #     print ('good data')
        # else:
        #     print ('bad bad')
        #     bad_data.append(filename)


        # concat all data set into a singl dataframe
        data = pd.DataFrame( data )
        file_name = pd.concat([file_name, data], axis=1, ignore_index=True)


    # with 0s rather than NaNs
    file_name = file_name.fillna(0)

    return file_name, tC

def _save_avg_data(num, y):
    fn = "avg/" + 'cycle' + str(num) + "-echoes-d.dat"
    filehandle = open(fn, "w")
    for samp in y:
        filehandle.write(str(samp) + "\n")
    filehandle.close()
    return


#=============================================================================#
#======================== MAIN FUNCTION ======================================#
def main ():
    with open(address + 'avgData-thursday.csv') as outfile:
        avgTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
        # avgTable.drop('Unnamed: 0', axis=1)
    outfile.close()

    with open(address + 'Me02-H100_180823_sorted.csv') as outfile:
        tempTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    [row, column ] = avgTable.shape
    print (avgTable.shape)
    print (avgTable.head())

    tC = tempTable['Temperature'][:150]

    #calculate the value at 30ns

    dt = float(1 / 7200000)
    row_id = int(round(30e-6 / (1.38888889e-7)))
    print (row_id)

    value = avgTable.iloc[row_id][1:]
    print (value)

    #plot data
    plt.figure(1)
    plt.scatter(tC, value)
    plt.title('Temperature vs Amp')
    plt.interactive(False)
    plt.show()
    return

#==============================================================================#
address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
bad_data = []

if __name__ == '__main__':
    main()