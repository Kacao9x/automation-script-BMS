import numpy as np
import pandas as pd

import subprocess
import datetime as dt
import thLib as th

keyword         = 'cycle'
name            = '180914_Me02-H100'
# path            = 'Me02-H100_180814/'
path = th.ui.getdir('Pick your directory') + '/'                                # prompts user to select folder
cycler_path     = path + name + '.csv'
cycler_path_new = path + name + '_new.csv'
final_log_path  = path + name + '_sorted.csv'
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
        if last < x[i]:
            count += 1

    return (count > 10)


# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    file_name = []
    list_cmd = ('ls '+ path +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip().split('-echoes')[0])

    return file_name


# Merge the capacity between stage 1,2 and 4
# only works with the cycler data logs
def merge_column(table):
    print (table.head().to_string())
    print (table.shape)
    row, col = table.shape

    NAN_finder = table['id'].notna()  # a boolean list of ID columns
    global ind
    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)

    print (ind)
    id_num = table.columns.get_loc("id_num")
    capmAh = table.columns.get_loc("cap(mAh)")

    #add 21.00 for real capacity
    # for i in range(0, int(ind[1])):
    #     table.iat[i, capmAh] = 38 + table.iat[i, capmAh]

    for i in range(len(ind) -1 ):

        # Addition of cap for CV and CC cycle (step 1 and 2)
        if (table.iat[int(ind[i]), id_num] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), id_num]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, capmAh]                                 # store the capacity
            diff = int(ind[i + 1]) - int(ind[i])                                # find the length of the stage

            for j in range(diff):
                table.iat[int(ind[i]) + j, capmAh] += tot
        # step 3 and 2
        elif (table.iat[int(ind[i]), id_num] == 'CC_Chg' and
              table.iat[int(ind[i - 1]), id_num] == 'CV_Chg'):

            tot = table.iat[int(ind[i]) - 1, capmAh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, capmAh] += tot


        # Keep the same capacity of CV_charge for rest cycle
        elif (table.iat[int(ind[i]), id_num] == 'Rest' and
              table.iat[int(ind[i - 1]), id_num] == 'CC_Chg' and
              table.iat[int(ind[i + 1]), id_num] == 'CC_DChg'):

            tot = table.iat[int(ind[i]) - 1, capmAh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, capmAh] += tot

        elif (table.iat[int(ind[i]), id_num] == 'Rest' and
              table.iat[int(ind[i - 1]), id_num] == 'CCCV_Chg'):

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
                table.iat[int(ind[i]) + j, capmAh] = tot - \
                                                     table.iat[int(ind[i]) + j, capmAh]

        # else:
        #     tot = table.iat[len(table.index) - 1, capmAh]
        #     diff = int(len(table.index) - int(ind[i + 1]))
        #     for j in range(diff):
        #         table.iat[int(ind[i + 1]) + j, capmAh] = tot - table.iat[
        #             int(ind[i + 1]) + j, capmAh]

    return table


def _read_time(table):
    # time_begin = int(table.index[ table['id'].str.contains(1) ].tolist())
    start_time = table['Date/Time'][_start_row]
    return start_time


# calculate the time difference in seconds. Return int
def calculate_time(begin, end, unit):
    end_dt      = _convert_to_time_object(end)

    if unit == 'sec':
        start_dt = _convert_to_time_object_fix(begin)
    elif unit == 'min':
        start_dt = _convert_to_time_object(begin)


    sec = 0
    diff = (end_dt - start_dt)
    if ( diff.days == 0 ):
        sec += diff.seconds
    else:
        sec += diff.days*24*60*60 + diff.seconds

    m, s = divmod(sec, 60)
    if unit == 'sec':
        return sec
    elif unit == 'min':
        return m


# grasp the capacity corresponding to the filename
# return line and value
def find_capacity(begin, end, table):
    line = _start_row
    diff = calculate_time(begin, end, 'sec')


    # while diff > __PERIOD__:
    #     line += int(diff / __PERIOD__)
    #     #identify the index to grasp the proper row of data instance
    #     check = pd.isnull(table.at[line,'Date/Time'])
    #     if check:
    #         line += 2
    #
    #     end_temp = table['Date/Time'][line]
    #     diff = calculate_time(end_temp, end, 'sec')


    line += int( diff / __PERIOD__ )
    # identify the index to grasp the proper row of data instance
    end_temp = table['Date/Time'][line]
    check = pd.isnull(table.at[line, 'Date/Time'])

    if check:
        end_temp = table['Date/Time'][line + 2]


    diff = calculate_time(end_temp, end, 'sec')
    line += int(diff / 5)
    print ('end_temp: ' + str(end_temp))
    print ("diff: %s" % str(line))
    return line, table['cap(mAh)'][line], table['current'][line]


# add a new header for the column to store echoes amplitude
def _SOC_header_creator():
    header = []
    filelist = display_list_of_file(keyword)

    for i in range(len(filelist)):
        header.append('SoC_' + str(i+1))
    return header


def _get_timestamp_from_filename( filename ):

    i = filename.split('-')
    # cycle1 - raw - 0 - 2018 - 08 - 31 - 16 - 44 - 34 - echoes - d
    if i[1] == 'temp':
        endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' \
                  + i[5] + ':' + i[6] + ':' + i[7]
        print ('endtime raw: ' + endtime)

    else:
        endtime = '2018' + '-' + i[4] + '-' + i[5] + ' ' \
                  + i[6] + ':' + i[7] + ':' + i[8]
        print ('endtime filtered: ' + endtime)

    return endtime


# return a sorted table with capacity, filename, index
def sort_by_name(filelist, starttime, table):
    cap     = []
    filename= []
    index   = []
    timeDelta = []
    current = []
    cycle1_time = _get_timestamp_from_filename( filelist[ 0 ] )

    for i, element in enumerate( filelist ):

        endtime = _get_timestamp_from_filename( element )
        row, c, curr  = find_capacity(starttime, endtime, table)

        if i == 0:
            timeDelta.append( 0 )
        else:
            diff = calculate_time(cycle1_time, endtime, 'min')
            timeDelta.append( diff )

        cap.append(c)
        current.append(curr)
        index.append(row)
        filename.append(element)


    column = ['index', 'cap(mAh)', 'current', 'FileName', 'TimeDelta']

    table_sorted = pd.DataFrame({'index': index,
                                 'cap(mAh)': cap,
                                 'current': current,
                                 'FileName': filename,
                                 'TimeDelta': timeDelta},
                                columns=column)                                 # columns=[] used to set order of columns

    table_sorted = table_sorted.sort_values('index')

    return table_sorted


# This function help grasp the data instance of 5 second interval
def _filter_data_by_timeInterval(table, sec):
    """
    merge the table with a time step of 0.1s
    :param table:
    """

    NAN_finder = table['id'].notna()                                            # result is in a boolean list

    global ind
    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)
    print (ind)
    np.sort(ind)


    tb = pd.DataFrame()

    for i in range(len(ind) -1):
        table_stage = table.loc[[int(ind[i])]]                                  # grasp the stage id
        print (table_stage.head())

        tb = pd.concat([tb, table_stage], axis=0)
        table_data = table.iloc[ int(ind[i]) + 1 : int(ind[i + 1]) : sec * 10].copy()  #grasp the data instance
        print (table_data.head().to_string())

        tb = pd.concat([tb, table_data], axis=0)

    tb.columns = ['extra','id','id_num', 'time', 'current',
                    'cap(mAh)', 'Date/Time']
    tb.sort_values('id')
    del tb['extra']

    return tb


def clean_test_data(fix = bool):

    with open(path + name + '.txt', 'r') as my_file:
        lines = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                            error_bad_lines=False, engine='python')
        my_file.close()

    cycler_data = lines.iloc[:, 0:10]
    # cycler_data = lines.iloc[::50, 0:10]
    print (cycler_data.shape)

    header_list = ['id_num', 'time', 'del', 'current',
                   'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                   'en(microWh)', 'Date/Time']
    cycler_data.columns = header_list
    del cycler_data['del'], cycler_data['del2'], cycler_data['en(mWh)'], \
        cycler_data['en(microWh)'], cycler_data['cap(microAh)']


    # added extra 'id' columns to shift the first rows
    header_list = ['id', 'id_num', 'time', 'current',
                   'cap(mAh)', 'Date/Time']
    cycler_data = cycler_data.reindex(columns=header_list)
    print (cycler_data.head())
    cycler_data.to_csv(cycler_path)

    '''
        search for rows that need to shift
    '''

    ind = []
    # for good cycler data with 5s interval
    ind = (cycler_data.index[cycler_data['time'].str.contains('Chg')].tolist()) \
          + (cycler_data.index[
                 cycler_data['time'].str.contains('Rest')].tolist())

    print (ind)

    # transpose the dataframe for shifting rows
    cycler_data_t = cycler_data.T

    for i in ind:
        cycler_data_t[i] = cycler_data_t.iloc[:, i].shift(-1).tolist()

    cycler_data = cycler_data_t.T

    ''' filter data of 5 sec interval '''
    if fix:
        cycler_data = _filter_data_by_timeInterval( cycler_data, 5 )

    cycler_data.to_csv(cycler_path)
    return cycler_data


def main():

    with open(cycler_path) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    ''' select data in 5s interval '''
    # table = clean_test_data(fix = False)


    table = merge_column(table)                                                 # Merge capactity of CC and CV stages
    table.to_csv(cycler_path_new)


    starttime = _read_time(table)                                               # when the test kicked-off
    print ('start-time: ' + str(starttime))

    # display the list of logfile and grasp the endtime
    filelist = display_list_of_file(keyword)                                    # get the endtime instance in filename
    print (filelist)

    table_sorted = sort_by_name(filelist, starttime, table)                     # grasp the data instance and sort
    table_sorted.to_csv(final_log_path)

    '''
    Add SoC data values into data frame
    '''
    # tC, delta = [], []
    # ampTable_concat = pd.DataFrame()
    # for i, name in enumerate( filelist ):
    #
    #     with open(path + name +'-echoes-d.dat') as readout:
    #         y_str = readout.read()
    #         y_str = y_str.splitlines()
    #         amp = []
    #         for j, num in enumerate(y_str):
    #             if j < len(y_str) - 1:
    #                 amp.append(float(num))
    #             else:
    #                 if len(num.split()) > 2:
    #                     temp = num.rstrip().split('Temperature:')[1]
    #                     temp = temp.split('oC')[0]
    #                     tC.append(float(temp))
    #                 else:
    #                     amp.append(float(num))
    #     readout.close()

        # col_header = table_sorted['cap(mAh)'][i]  # read the corresponding capacity
        # ampTable = pd.DataFrame({col_header: amp})
        #
        #
        # ampTable_concat = pd.concat([ampTable_concat, ampTable], axis=1)
        # # table_sorted = pd.concat([table_sorted, ampTable], axis=1)  # add new column (diff index) into exisiing Dataframe
        # del amp[:], ampTable

    # table_sorted.sort('index')

    # table_sorted['Temperature'] = tC
    with open(path + 'avgData.csv') as outfile:
        ampTable_concat = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    with open(path + 'temp.csv') as outfile:
        tempTable = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()
    tC = tempTable['Temperature']

    table_sorted = pd.concat([table_sorted, tC],
                             axis=1)  # add new column (diff index) into exisiing Dataframe
    table_sorted = pd.concat([table_sorted, ampTable_concat],
                             axis=1)  # add new column (diff index) into exisiing Dataframe
    table_sorted.to_csv(final_log_path)

    return


if __name__ == '__main__':
    main()
