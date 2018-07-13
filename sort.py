import numpy as np
import glob
import pandas as pd

import subprocess, sys, os
import csv
import datetime as dt


keyword         = 'cycle'
path            = 'data/Filtered/Filtered/'
cycler_path     = path + 'Cycler_Data_Apple_180713.csv'
final_log_path  = path + 'test_log_sorted.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove



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


def display_list_of_file(key):
    file_name = []
    list_cmd = ('ls '+ path +' -1v' + " | grep '" + key + "'")
    print list_cmd
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip().split('-echoes')[0])

    return file_name


def read_Dataframe_from_file(filepath):
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
# only works with the cycler data logs
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

    table.to_csv(cycler_path)
    return


def _read_time(table):
    print table.iat[0,1]
    start_time = table.iat[1, 8]
    if( table.iat[0,1] == 'CC_Chg' ):
        start_time = table.iat[1, 8]

    # else:
        # for i in table.iterrows():
        # table[table['']]
        # df[df['model'].str.match('Mac')]
        # # I=table.apply(lambda row: 0 if row['id'] == False else _addition_value(row['cap(mAh)']),axis=1)
    return start_time

# calculate the time difference in seconds. Return int
def calculate_time(begin, end):
    start_dt    = _convert_to_time_object(begin)
    end_dt      = _convert_to_time_object(end)

    sec = 0
    diff = (end_dt - start_dt)
    if ( diff.days == 0 ):
        sec += diff.seconds
    else:
        sec += diff.days*24*60*60 + diff.seconds

    return sec


def find_capacity(begin, end, table):
    diff = calculate_time(begin, end)

    line = _line_to_capture(diff)
    print "diff: %s" % str(line)

    # cap = table.iat[line, 4]                                                  #grasp manually
    return line, table['cap(mAh)'][line]

def _SOC_header_creator():
    header = []
    filelist = display_list_of_file(keyword)

    for i in range(len(filelist)):
        header.append('SoC_' + str(i))
    return header

def main():

    table = read_Dataframe_from_file('data/Filtered/Filtered/Apple-18-07-13.txt')
    merge_column(table)

    starttime = _read_time(table)
    print str(starttime)

    cap     = []
    filename= []
    index   = []
    SoC     = []

    filelist = display_list_of_file(keyword)
    for element in filelist:
        print '#3' + element
        i = element.split('-')
        print i
        if i[1] == '2018':

            endtime = '2018' + '-' + i[2] + '-' + i[3] + ' ' \
                      + i[4] + ':' + i[5] + ':' + i[6]
            print endtime

            i, c = find_capacity(starttime, endtime, table)
            cap.append( c )
            index.append( i )
            filename.append(element)

        else:

            endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' \
                      + i[5] + ':' + i[6] + ':' + i[7]
            print endtime

            i, c = find_capacity(starttime, endtime, table)
            cap.append(c)
            index.append(i)
            filename.append(element)

            temp =[]
            with open(path+element+'-echoes-b.dat') as fobj:
                for line in fobj:
                    temp.append(float(line.rstrip()))
            fobj.close()
            SoC.append(temp)
    # print SoC

    column = ['index', 'cap(mAh)', 'FileName']
    column.append(_SOC_header_creator())

    table_sorted = pd.DataFrame({'index': index,
                                 'cap(mAh)': cap,
                                 'FileName': filename,
                                 'SoC': SoC},
                                columns=column)      #columns=[] used to set order of columns

    table_sorted = table_sorted.sort_values('index')



    # table_sorted.to_csv(final_log_path)
    table_sorted.to_csv(path+'test.csv')

    # print table_sorted.to_string()

    # a, b = 9, 11
    #
    # print "a: %2.f, b: %2.0f" % (a,b)
    return
if __name__ == '__main__':
    main()
