import numpy as np
import pandas as pd

import subprocess
import datetime as dt
import thLib as th


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


# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    file_name = []
    list_cmd = ('ls '+ path +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip())

    return file_name


def concat_custom_data( key ):
    tC_1, tC_2 = [], []
    file_name = pd.DataFrame()
    list_file = display_list_of_file(key)
    print (list_file)
    for filename in list_file:

        with open(path + filename) as my_file:
            y_str = my_file.read()
            y_str = y_str.splitlines()
        my_file.close()
        data = []
        for i, num in enumerate(y_str):
            if i < len(y_str) - 1:
                data.append(float(num))

            else:
                # print (len(num.split() ))
                if len(num.split()) > 2:
                    tC_1.append( num.split()[1] )
                    tC_2.append( num.split()[2] )
                else:
                    data.append(float(num))
    # with 0s rather than NaNs
    file_name = file_name.fillna(0)

    return file_name, tC_2, tC_1


def concat_all_data(cycle = int, tempC = bool):

    big_set = pd.DataFrame()

    list_file = display_list_of_file('cycle' + str(cycle) + '-')
    # print (list_file)
    for captureID, filename in enumerate( list_file ):

        with open(path + filename) as my_file:
            y_str = my_file.read()
            y_str = y_str.splitlines()
            data = []
            for i, num in enumerate(y_str):
                data.append(float(num))
        my_file.close()
        #===== end-loop to read data ===== #

        # concat all data set into a singl dataframe
        single_set = pd.DataFrame({captureID: data})
        big_set = pd.concat([big_set, single_set], axis=1, ignore_index=True)

    # with 0s rather than NaNs
    big_set = big_set.fillna(0)

    return big_set, list_file


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
    return line, table['cap(mAh)'][line], table['current'][line], \
           table['volt'][line]



def _get_timestamp_from_filename( filename ):

    i = filename.split('-')

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
    volt = []
    current = []
    charging = []

    for i, element in enumerate( filelist ):

        endtime = _get_timestamp_from_filename( element )
        row, c, curr, voltage  = find_capacity(starttime, endtime, table)

        cap.append(c)
        current.append(curr)
        volt.append(voltage)
        index.append(row)
        filename.append(element)

        if curr < 0:
            charging.append( -1 )
        else:
            charging.append( 1 )

    print ("start sorting")
    column = ['index', 'charging', 'volt', 'current', 'cap(mAh)', 'FileName']

    table_sorted = pd.DataFrame({'index': index,
                                 'charging': charging,
                                 'volt': volt,
                                 'current': current,
                                 'cap(mAh)': cap,
                                 'FileName': filename},
                                columns=column)                                 # columns=[] used to set order of columns

    del table_sorted['index']
    # table_sorted = table_sorted.sort_values('index')
    print ("done sorting")
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

    tb.columns = ['id','id_num', 'time', 'volt', 'current',
                    'cap(mAh)', 'Date/Time']
    tb.sort_values('id')
    # del tb['extra']

    return tb


def clean_test_data(fix = bool):

    with open(path + name + '.txt', 'r') as my_file:
        lines = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                            error_bad_lines=False, engine='python')
        my_file.close()

    cycler_data = lines.iloc[:, 0:10]
    # cycler_data = lines.iloc[::50, 0:10]
    print (cycler_data.shape)
    header_list = ['id_num', 'time', 'volt', 'current',
                   'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                   'en(microWh)', 'Date/Time']
    cycler_data.columns = header_list
    del cycler_data['del2'], cycler_data['en(mWh)'], \
        cycler_data['en(microWh)'], cycler_data['cap(microAh)']


    # added extra 'id' columns to shift the first rows
    header_list = ['id', 'id_num', 'time', 'volt','current',
                   'cap(mAh)', 'Date/Time']
    cycler_data = cycler_data.reindex(columns=header_list)
    print (cycler_data.head())
    cycler_data.to_csv(cycler_path)

    '''
        search for rows that need to shift
    '''

    ind = []
    # for good cycler data with 5s interval
    ind = (cycler_data.index[cycler_data['time'].str.contains('Chg')].tolist())\
        + (cycler_data.index[cycler_data['time'].str.contains('Rest')].tolist())

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

    ''' select data in 5s interval.
    Fix=True if the general report captured data every 0.1s '''
    # table = clean_test_data(fix = False)
    # return


    with open(cycler_path) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    table = merge_column(table)                                                 # Merge capactity of CC and CV stages
    table.to_csv(cycler_path_new)

    '''
        Determining rows to check the value based on the time differnce
    '''
    starttime = _read_time(table)                                               # when the test kicked-off
    print ('start-time: ' + str(starttime))

    filelist = display_list_of_file(keyword)                                    # store the list of filename
    battery_id_list = [battery_id for _ in range(len( filelist ))]              # fill up the whole list with battery_id
    SoH_list        = [SoH for _ in range(len( filelist ))]

    # grasp the datetime from the filename
    datetime_list = []
    for single_name in filelist:
        st = _get_timestamp_from_filename( single_name )
        datetime_list.append( st )

    table_sorted = sort_by_name(filelist, starttime, table)                     # grasp the data instance and sort
    table_sorted['battery_id']      = battery_id_list                           # add battery id list into the report dateframe
    table_sorted['SoH']             = SoH_list                                  # add SOH list into the report dateframe
    table_sorted['collection_date'] = datetime_list                             # add collection date list into report dateframe


    table_sorted.to_csv(final_log_path)

    '''
        For enerating average data + tempC report
    '''
    # concat average sorted data sets
    # with open(path + 'avgData-bandpass.csv') as outfile:
    #     ampTable_concat = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()
    # ampTable_concat = ampTable_concat.T
    # ampTable_concat.to_csv(path + 'avg_data_transpose.csv')
    #
    # # concat temperature
    # tempTable = pd.DataFrame()
    # oneRead, tC_1, tC_2 = concat_custom_data('cycle')
    # tempTable['Temperature_bottom'] = tC_1                                      # construct a dataframe format for tempC
    # tempTable['Temperature_top'] = tC_2                                         # construct a dataframe format for tempC
    #
    # table_sorted = pd.concat([table_sorted, tempTable['Temperature_bottom'],
    #                           tempTable['Temperature_bottom']],
    #                          axis=1)  # add new column (diff index) into exisiing Dataframe
    # del tempTable
    # del ampTable_concat


    ''' 
        For generating raw data report 
        Select data/primary folder that contain the raw files
    '''


    return

#==============================================================================#
#                                                                              #
#                       constant variable                                      #
#                                                                              #
#==============================================================================#


keyword         = 'cycle'
battery_id      = 'Me01'
SoH             = '100'
name            = battery_id + '-H' + SoH + '_181017'
path            = '/media/jean/Data/titan-echo-board/echo-E/Me01-H100_181017-echo-e/data/primary/'
# path = th.ui.getdir('Pick your directory') + '/'                                # prompts user to select folder
cycler_path     = path + name + '.csv'
cycler_path_new = path + name + '_new.csv'
final_log_path  = path + name + '_rawData_sorted.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove
ind = []                                                                        #list of stage index



if __name__ == '__main__':
    main()
