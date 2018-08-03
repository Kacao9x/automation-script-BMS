import numpy as np
import pandas as pd

import subprocess
import datetime as dt


keyword         = 'cycle'
path            = 'Me01-H100_180731/Filtered/'
cycler_path     = path + 'Cycler_Data_Merc_180731.csv'
cycler_path_new = path + 'Cycler_Data_Merc_180731_new.csv'
final_log_path  = path + 'filtered_sorted_logs.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove
ind = []                                                                        #list of stage index

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

# return the number of row
def _row_count(filename):
    # return sum(1 for row in open(filename))
    sum = 0
    with open(filename) as readout:
        for _ in readout:
            sum +=1
    readout.close()
    return sum


def is_dummy_data(x):
    last = 0.8
    count = 0
    for i in range(0, len(x)):
        if last > x[i]:
            count += 1

    if count > 10:
        return False
    else:
        return True


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
    # end_row = _row_count(path + 'outfile_raw_.csv')                           # in case the test endup by CC-CV stage
    NAN_finder = table['id'].notna()  # a boolean list of ID columns
    print (table.head().to_string())
    print (table.shape)

    global ind
    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True and table['id'][i] < 10:
            ind = np.append(ind, i)

    print (ind)
    id_num = table.columns.get_loc("id_num")
    capmAh = table.columns.get_loc("cap(mAh)")

    for i in range(len(ind) - 1):
        # ind[ ] need to be changed due to the change of cycling order
        # Addition of cap for CV and CC cycle
        if (table.iat[int(ind[i]), id_num] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), id_num]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, capmAh]                                 # store the capacity
            diff = int(ind[i + 1]) - int(ind[i])                                # find the length of the stage
            # diff = int(end_row - int(ind[i])) - 1                               # in case the test endup by CC-CV stage

            for j in range(diff):
                table.iat[int(ind[i]) + j, capmAh] += tot

        # # Subtraction for discharging cycle
        # elif i == len(ind) - 1:
        #
        #     tot = table.iat[int(len(NAN_finder) - 1), 4]
        #     diff = int(len(NAN_finder)) - int(ind[i])
        #     for j in range(diff):
        #         table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

        # Keep the same capacity of CV_charge for rest cycle
        elif (table.iat[int(ind[i]), id_num] == 'Rest' and
              table.iat[int(ind[i - 1]), id_num] == 'CV_Chg'):

            tot = table.iat[int(ind[i]) - 1, capmAh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, capmAh] += tot

        # Subtraction the capacity for dischage cycle
        elif (table.iat[int(ind[i + 1]), id_num] == 'Rest' and
              table.iat[int(ind[i]), id_num] == 'CC_DChg'):

            tot = table.iat[int(ind[i + 1]) - 1, capmAh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, capmAh] = tot - table.iat[
                    int(ind[i]) + j, capmAh]

    # for i in range(len(ind) - 1):
    #     # ind[ ] need to be changed due to the change of cycling order
    #     # Rest: remains capacity
    #     if (table['id_num'][ int(ind[i]) ] == 'Rest'):
    #
    #         tot = table['cap(mAh)'][int(ind[i]) - 1]                                 # store the capacity
    #         diff = int(ind[i + 1]) - int(ind[i])                                # find the length of the stage
    #         # diff = int(end_row - int(ind[i])) - 1                               # in case the test endup by CC-CV stage
    #
    #         for j in range(diff):
    #             table['cap(mAh)'][ int(ind[i]) + j ] = tot
    #
    #     elif (table['cap(mAh)'][int(ind[i])] == 'CC_DChg'):
    #         tot = table['cap(mAh)'][int(ind[i + 1]) - 1]
    #         diff = int(ind[i + 1]) - int(ind[i])                                # find the length of the stage
    #         for j in range(diff):
    #             table['cap(mAh)'][int(ind[i]) + j] = tot - table['cap(mAh)'][int(ind[i]) + j]

    table.to_csv(cycler_path_new)
    return


def _read_time(table):
    # time_begin = table.index[ table['id_num'].str.contains('1') ].values
    # print 'time begin: %s' % str(time_begin)
    # print table['Date/Time'][time_begin + 1]
    # start_time = table['Date/Time'][time_begin + 1]
    start_time = table['Date/Time'][_start_row]
    return start_time

# calculate the time difference in seconds. Return int
def calculate_time(begin, end):
    # start_dt    = _convert_to_time_object(begin)
    end_dt      = _convert_to_time_object(end)
    start_dt      = _convert_to_time_object_fix(begin)

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


    #identify the index to grasp the proper row of data instance
    end_temp = table['Date/Time'][line]
    check = pd.isnull(table.at[line,'Date/Time'])

    if check:
        end_temp = table['Date/Time'][line + 1]


    print 'end_temp: ' + str(end_temp)
    error = calculate_time(end_temp, end)
    line += int( error / 5 )

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
    # table = read_Dataframe_from_file(path + 'Me01-H100_180728.txt')                                          # create a custome Dataframe to work on
    with open(cycler_path) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    merge_column(table)                                                         # Merge capactity of CC and CV stages

    with open(cycler_path_new) as outfile:
        table = pd.read_csv(outfile, header=0, sep=',')
    outfile.close()

    starttime = _read_time(table)                                               # when the test kicked-off
    print 'start-time: ' + str(starttime)

    # display the list of logfile and grasp the endtime
    filelist = display_list_of_file(keyword)                                    # get the endtime instance in filename
    print (filelist)

    table_sorted = sort_by_name(filelist, starttime,table)                      # grasp the data instance and sort
    table_sorted.to_csv(final_log_path)

    '''
    Add SoC data values into data frame
    '''
    for i, name in enumerate( filelist ):
        temp = []
        with open(path + name +'-echoes-b.dat') as readout:
            for line in readout:
                temp.append(float(line.rstrip()))
        readout.close()

        if is_dummy_data(temp):
            temp[:] = []

        col_header = table_sorted['cap(mAh)'][ i ]                                   #read the corresponding capacity
        tempTable = pd.DataFrame({col_header: temp})

        table_sorted = pd.concat([table_sorted, tempTable],
                                 axis=1)  # add new column (diff index) into exisiing Dataframe
        del temp[:], tempTable

    table_sorted.to_csv(final_log_path)

    return
if __name__ == '__main__':
    main()
