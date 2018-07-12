import numpy as np
import glob
import pandas as pd

import subprocess, sys, os
import csv
import datetime as dt


keyword     = 'cycle'
path        = 'data/Cycler_Data_NIS3_180703.csv'
log_name    = 'data/testlog.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
__DIFF__    = 0                                                                 #the result of time difference btw start and stop
_start_row  = 1                                                                 #number of header to be remove
__CAP__     = 0                                                                 #capacity of batt
header      = ('id', 'id_num', 'time', 'del', 'current',
            'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
            'en(microWh)', 'Date/Time')

header_new  = ('index', 'cap(mAh)', 'FileName')


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
def _convert_to_time_object(str_obj):
    return dt.datetime.strptime(str_obj, '%Y-%m-%d %H:%M:%S')

def _line_to_capture(second):
    return _start_row + int(second/__PERIOD__)

# return the number of row
def _row_count(filename):
    # return sum(1 for row in open(filename))
    sum = 0
    with open(filename) as readout:
        for _ in readout:
            sum +=1
    readout.close()
    return sum

    return table


def make_Dataframe(filepath):
    with open(filepath) as outfile:
        table = pd.read_csv(outfile, header=3, sep='\t')
    outfile.close()

    table = table.iloc[:, 1:12]
    table.columns = ['id', 'id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                     'en(microWh)', 'Date/Time']
    del table['del'], table['del2']

    return table


# Merge the capacity between stage 1,2 and 4
# only works with the test logs from HP machine
def merge_column(table):
    # table: Dataframe with a custom header

    NAN_finder = table['id'].notna()                                            # result is in a boolean list
    ind = []
    print table

    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)

    for i in range(len(ind)):
        if (table.iat[int(ind[i]), 1] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), 1]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, 4]                                 # store the capacity
            diff = int(ind[i + 1]) - int(ind[i])

            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

        elif i == len(ind) - 1:

            tot = table.iat[int(len(NAN_finder) - 1), 4]
            diff = int(len(NAN_finder)) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

        elif (table.iat[int(ind[i]), 1] == 'Rest' and
              table.iat[int(ind[i - 1]), 1] == 'CV_Chg'):

            tot = table.iat[int(ind[i]) - 1, 4]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

        elif (table.iat[int(ind[i + 1]), 1] == 'Rest' and
              table.iat[int(ind[i]), 1] == 'CC_DChg'):

            tot = table.iat[int(ind[i + 1]) - 1, 4]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

    table.to_csv(path)
    return

def helper():

    return

def _read_start_time(table):
    print table.iat[0,1]
    if( table.iat[0,1] == 'CC_Chg' ):
        start_time = table.iat[1, 8]

    else:
        # for i in table.iterrows():
        table[]
        df[df['model'].str.match('Mac')]
        # I=table.apply(lambda row: 0 if row['id'] == False else _addition_value(row['cap(mAh)']),
                                        axis=1)
    return start_time


def main():

    table = make_Dataframe('data/NIS3_18-07-03.txt')
    merge_column(table)

    start_time = _read_start_time(table)
    print str(start_time)


    return
if __name__ == '__main__':
    main()
