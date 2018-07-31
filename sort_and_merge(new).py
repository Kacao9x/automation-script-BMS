import numpy as np
import pandas as pd

import subprocess
import datetime as dt


keyword         = 'cycle'
path            = 'Me01-H100_180728/Filtered/'
cycler_path     = path + 'Cycler_Data_Merc_180728.csv'
final_log_path  = path + 'filtered_sorted_logs.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove
ind = []

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

def _convert_to_time_object_fix(str_obj):
    return dt.datetime.strptime(str_obj, '%m/%d/%Y %H:%M:%S')

def _line_to_capture(second):
    return _start_row + int(second/__PERIOD__)
    # return _start_row + int(second)

# return the number of row
def _row_count(filename):
    # return sum(1 for row in open(filename))
    sum = 0
    with open(filename) as readout:
        for _ in readout:
            sum +=1
    readout.close()
    return sum


# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    file_name = []
    list_cmd = ('ls '+ path +' -1v' + " | grep '" + key + "'")
    print list_cmd
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip().split('-echoes')[0])

    return file_name

# convert a csv/txt table into Pandas dataframe
# with a custom columns
def read_Dataframe_from_file(filepath):
    with open(filepath) as outfile:
        table = pd.read_csv(outfile, header=3, sep='\t', error_bad_lines=False)
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
    end_row = _row_count(path + 'outfile_raw_.csv')
    NAN_finder = table['id'].notna()                                            # result is in a boolean list
    ind = []
    print ("\n\n")
    print (table.head().to_string())
    print (table.shape)

    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)

    print (ind)
    for i in range(len(ind)):
        # ind[ ] need to be changed due to the change of cycling order
        if (table.iat[int(ind[i]), 1] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), 1]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, 4]                                 # store the capacity
            # diff = int(ind[i + 1]) - int(ind[i])                                # find the length of the stage
            diff = int(end_row - int(ind[i])) - 1

            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

        # #Subtraction
        # elif i == len(ind) - 1:
        #
        #     tot = table.iat[int(len(NAN_finder) - 1), 4]
        #     diff = int(len(NAN_finder)) - int(ind[i])
        #     for j in range(diff):
        #         table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

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

# grasp the timestamp in the dataframe
# return datetime Object
# def _read_time(table):
#     print table.iat[0,1]
#     start_time = table.iat[1, 8]
#     if( table.iat[0,1] == 'CC_Chg' ):
#         start_time = table.iat[1, 8]
#
#     # grasp automatically instead
#     # else:
#         # for i in table.iterrows():
#         # table[table['']]
#         # df[df['model'].str.match('Mac')]
#         # # I=table.apply(lambda row: 0 if row['id'] == False else _addition_value(row['cap(mAh)']),axis=1)
#     return start_time

def _read_time(table):
    print table.iat[0,2]
    print table.iat[ _start_row , 9 ]
    start_time = table.iat[_start_row , 9]

    if( table.iat[0,1] == 'Record ID' ):
        start_time = table.iat[0, 8]

    # grasp automatically instead
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
    # start_dt      = _convert_to_time_object_fix(begin)
    sec = 0
    diff = (end_dt - start_dt)
    if ( diff.days == 0 ):
        sec += diff.seconds
    else:
        sec += diff.days*24*60*60 + diff.seconds

    return sec

# grasp the capacity corresponding to the filename
# return line and value
def find_capacity(begin, end, table):
    diff = calculate_time(begin, end)

    line = _line_to_capture(diff)
    print "diff: %s" % str(line)

    sum = 0
    if (diff / 5) > ind[0] and (diff / 5) < ind[1]:
        sum += 0
    elif (diff / 5) > ind[1] and (diff / 5) < ind[2]:
        sum += 3
    elif (diff / 5) > ind[2] and (diff / 5) < ind[3]:
        sum += 5
    elif (diff / 5) > ind[3] and (diff / 5) < ind[4]:
        sum += 8
    elif (diff / 5) > ind[4] and (diff / 5) < ind[5]:
        sum += 12
    elif (diff / 5) > ind[5]:
        sum += 12

    # cap = table.iat[line, 4]                                                  #grasp manually
    # return line, table['cap(mAh)'][line]
    return line, table['cap(mAh)'][line]

# add a new header for the column to store echoes amplitude
def _SOC_header_creator():
    header = []
    filelist = display_list_of_file(keyword)

    for i in range(len(filelist)):
        header.append('SoC_' + str(i+1))
    return header

# return a sorted table with capacity, filename, index
def sort_by_name(filelist, starttime, table):
    cap     = []
    filename= []
    index   = []

    for element in filelist:

        i = element.split('-')
        print i

        if i[1] == '2018':
            endtime = '2018' + '-' + i[2] + '-' + i[3] + ' ' \
                      + i[4] + ':' + i[5] + ':' + i[6]
            print 'endtime raw: ' + endtime

        else:
            endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' \
                      + i[5] + ':' + i[6] + ':' + i[7]
            print 'endtime filtered: ' + endtime

        i, c = find_capacity(starttime, endtime, table)
        cap.append(c)
        index.append(i)
        filename.append(element)


    column = ['index', 'cap(mAh)', 'FileName']

    table_sorted = pd.DataFrame({'index': index,
                                 'cap(mAh)': cap,
                                 'FileName': filename},
                                columns=column)                                 # columns=[] used to set order of columns

    table_sorted = table_sorted.sort_values('index')

    return table_sorted


def main():

    table = read_Dataframe_from_file(path + 'Me01-H100_180728.txt')
    table.to_csv(path + 'outfile_raw_.csv')
    merge_column(table)


    with open(cycler_path) as outfile:
        table = pd.read_csv(outfile, header=0, sep=',')
    outfile.close()


    starttime = _read_time(table)
    print 'start-time: ' + str(starttime)

    # display the list of logfile and grasp the endtime
    filelist = display_list_of_file(keyword)
    print (filelist)

    table_sorted = sort_by_name(filelist, starttime, table)
    table_sorted.to_csv(final_log_path)

    # Add SoC data values into data frame

    for i, name in enumerate( filelist ):
        temp = []
        with open(path + name +'-echoes-b.dat') as readout:
            for line in readout:
                temp.append(float(line.rstrip()))
        readout.close()

        col_header = table_sorted.iat[ i, 1 ]                                   #read the corresponding capacity
        tempTable = pd.DataFrame({col_header: temp})

        table_sorted = pd.concat([table_sorted, tempTable],
                                 axis=1)  # add new column (diff index) into exisiing Dataframe
        del temp[:], tempTable

    table_sorted.to_csv(final_log_path)

    return
if __name__ == '__main__':
    main()