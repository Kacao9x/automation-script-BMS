import numpy as np
import pandas as pd

import subprocess
import datetime as dt
# import thLib as th


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
def _convert_to_time_object(time_obj=str, Neware_machine=False):

    if Neware_machine:
        return dt.datetime.strptime(time_obj, '%m/%d/%Y %H:%M:%S')
    else:
        return dt.datetime.strptime(time_obj, '%Y-%m-%d %H:%M:%S')


def _validate_strptime_format( date_text ):
    try:
        if date_text != _convert_to_time_object( date_text, False ).strfttime('%m/%d/%Y %H:%M:%S'):
            raise ValueError
        return True
    except ValueError:
        return False


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


def concat_all_data(tempC = bool, search_key = str):
    '''
    :param cycle: keyword number to search and sort out
    :param tempC: True to read the temperature files, False otherwise
    :return: a dataframe contains all avg capture in a custom format
            an array of all data sets
    '''
    big_set = pd.DataFrame()

    if tempC:
        ''' Read the temperature files
        '''
        tC_1, tC_2 = [], []
        list_file = display_list_of_file( search_key )

        for filename in list_file:

            with open(path + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            for i, num in enumerate(y_str):
                if len(num.split()) > 2:
                    tC_1.append(num.split()[1])
                    tC_2.append(num.split()[2])

        return tC_2, tC_1


    else:
        '''Read data from capture files
        '''
        list_file = display_list_of_file( search_key )

        for captureID, filename in enumerate( list_file ):

            with open(path + filename) as my_file:
                y_str = my_file.read()
                y_str = y_str.splitlines()
            my_file.close()

            data = [float(num) for num in y_str]                                # convert string to float

            # concat all data set into a singl dataframe
            single_set = pd.DataFrame({captureID: data})
            big_set = pd.concat([big_set, single_set], axis=1, ignore_index=True)
            del data

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
    id_num      = table.columns.get_loc("id_num")
    cap_mAh     = table.columns.get_loc("cap(Ah)")
    energy_mWh  = table.columns.get_loc("en(Wh)")

    #add 21.00 for real capacity
    # for i in range(0, int(ind[1])):
    #     table.iat[i, cap_mAh] = 38 + table.iat[i, cap_mAh]


    for i in range(len(ind) -1 ):

        # Addition of cap for CV and CC cycle (step 1 and 2)
        if (table.iat[int(ind[i]), id_num] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), id_num]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, cap_mAh]                           # store the capacity
            diff = int(ind[i + 1]) - int(ind[i])                                # find the length of the stage

            for j in range(diff):
                table.iat[int(ind[i]) + j, cap_mAh] += tot
        # step 3 and 2
        elif (table.iat[int(ind[i]), id_num] == 'CC_Chg' and
              table.iat[int(ind[i - 1]), id_num] == 'CV_Chg'):

            tot = table.iat[int(ind[i]) - 1, cap_mAh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, cap_mAh] += tot
                table.iat[int(ind[i]) + j, cap_mAh] += tot


        # Keep the same capacity of CV_charge for rest cycle
        elif (table.iat[int(ind[i]), id_num] == 'Rest' and
              table.iat[int(ind[i - 1]), id_num] == 'CC_Chg' and
              table.iat[int(ind[i + 1]), id_num] == 'CC_DChg'):

            tot = table.iat[int(ind[i]) - 1, cap_mAh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, cap_mAh] += tot

        elif (table.iat[int(ind[i]), id_num] == 'Rest' and
              table.iat[int(ind[i - 1]), id_num] == 'CCCV_Chg'):

            tot     = table.iat[int(ind[i]) - 1, cap_mAh]
            tot_mwh = table.iat[int(ind[i]) - 1, energy_mWh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, cap_mAh] += tot
                table.iat[int(ind[i]) + j, energy_mWh] += tot_mwh


        # Subtraction the capacity for dischage cycle
        elif (table.iat[int(ind[i + 1]), id_num] == 'Rest' and
              table.iat[int(ind[i]), id_num] == 'CC_DChg'):

            tot     = table.iat[int(ind[i + 1]) - 1, cap_mAh]
            tot_mwh = table.iat[int(ind[i + 1]) - 1, energy_mWh]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, cap_mAh] = tot - \
                                                     table.iat[int(ind[i]) + j, cap_mAh]
                table.iat[int(ind[i]) + j, energy_mWh] = tot_mwh - \
                                                     table.iat[int(ind[i]) + j, energy_mWh]

        # else:
        #     tot = table.iat[len(table.index) - 1, cap_mAh]
        #     diff = int(len(table.index) - int(ind[i + 1]))
        #     for j in range(diff):
        #         table.iat[int(ind[i + 1]) + j, cap_mAh] = tot - table.iat[
        #             int(ind[i + 1]) + j, cap_mAh]

    return table


def _read_time(table):
    start_time = table['Date/Time'][_start_row]
    return start_time


# calculate the time difference in seconds. Return int
def calculate_time(begin, end, neware_machine=True):
    end_dt      = _convert_to_time_object(time_obj=end, Neware_machine=False)

    if neware_machine:
        start_dt = _convert_to_time_object(begin, True)
    else:
        start_dt = _convert_to_time_object(begin, True)


    sec = 0
    diff = (end_dt - start_dt)
    if ( diff.days == 0 ):
        sec += diff.seconds
    else:
        sec += diff.days*24*60*60 + diff.seconds

    m, s = divmod(sec, 60)

    return sec
    # if unit == 'sec':
    #     return sec
    # elif unit == 'min':
    #     return m


# grasp the capacity corresponding to the filename
# return line and value
def find_capacity(begin, end, table):
    line = _start_row
    diff = calculate_time(begin, end, neware_machine=__NEWARE__)


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
    print ('end_temp_1: ' + str(end_temp))

    diff = calculate_time(end_temp, end, neware_machine=__NEWARE__)
    line += int(diff / __PERIOD__)

    print ('end_temp_correct: ' + str(end_temp))
    print ("correct diff: %s \n" % str(diff))

    return line, table['cap(Ah)'][line], table['en(Wh)'][line],\
        table['current'][line], table['volt'][line], table['SoH'][line],\
        table['SoC'][line]



def _get_timestamp_from_filename( filename ):

    i = filename.split('-')

    if i[1] == 'temp':
        endtime = i[2] + '-' + i[3] + '-' + i[4] + ' ' \
                  + i[5] + ':' + i[6] + ':' + i[7]
        print ('endtime raw: ' + endtime)

    else:
        endtime = i[3] + '-' + i[4] + '-' + i[5] + ' ' \
                  + i[6] + ':' + i[7] + ':' + i[8]
        print ('endtime filtered: ' + endtime)

    return endtime


# return a sorted table with capacity, filename, index
def sort_by_name(filelist, starttime, table):
    cap     = []
    power   = []
    filename= []
    index   = []
    volt    = []
    current = []
    charging= []
    SoH     = []
    SoC     = []


    for i, element in enumerate( filelist ):

        endtime = _get_timestamp_from_filename( element )
        row, c, p, curr, voltage, soh, soc  = find_capacity(starttime, endtime, table)

        index.append(row)
        cap.append(c)
        power.append(p)
        volt.append(voltage)
        current.append(curr)
        filename.append(element)
        SoH.append(soh)
        SoC.append(soc)

        if curr < 0:
            charging.append( -1 )
        else:
            charging.append( 1 )

    print ("start sorting")
    column = ['index', 'charging', 'volt', 'current', 'cap(Ah)',
            'power(Wh)', 'FileName', 'SoH', 'SoC']

    table_sorted = pd.DataFrame({'index'    : index, 'charging' : charging,
                                 'volt'     : volt, 'current'  : current,
                                 'cap(Ah)'  : cap, 'power(Wh)':power,
                                 'FileName' : filename, 'SoH' : SoH, 'SoC' : SoC},
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
                    'cap(Ah)', 'Date/Time']
    tb.sort_values('id')
    # del tb['extra']

    return tb


def clean_test_data(Neware_report = True, fix = False):
    ''' select data in 5s interval.
    Fix=True if the general report captured data every 0.1s '''

    with open(path + name + '.txt', 'r') as my_file:
        if Neware_report:
            lines = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                                error_bad_lines=False, engine='python')
        else:    
            lines = pd.read_csv(my_file, header=3, sep=r'\t',
                                error_bad_lines=False, engine='python')
        my_file.close()

    print (lines.head())
    cycler_data = lines.iloc[:, 0:10]
    # cycler_data = lines.iloc[::50, 0:10]
    print (cycler_data.shape)
    header_list = ['id_num', 'time', 'volt', 'current',
                   'del2', 'cap(Ah)', 'cap(microAh)', 'en(Wh)',
                   'en(microWh)', 'Date/Time']
    cycler_data.columns = header_list
    del cycler_data['del2'], \
        cycler_data['en(microWh)'], cycler_data['cap(microAh)']


    # added extra 'id' columns to shift the first rows
    header_list = ['id', 'id_num', 'time', 'volt','current',
                   'cap(Ah)', 'en(Wh)','Date/Time']
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

    # ''' select data in 5s interval.
    # Fix=True if the general report captured data every 0.1s '''
    # table = clean_test_data(Neware_report = True, fix = False)
    #
    #
    # with open(cycler_path) as outfile:
    #     table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()
    #
    # table = merge_column(table)                                                 # Merge capactity of CC and CV stages
    # table.to_csv(cycler_path_merged)

    '''
        Determining rows to check the value based on the time differnce
    '''
    with open(cycler_path_merged) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()


    starttime = _read_time(table)                                               # when the test kicked-off
    print ('start-time: ' + str(starttime))

    filelist = display_list_of_file(keyword)                                    # store the list of filename
    battery_id_list = [battery_id for _ in range(len( filelist ))]              # fill up the whole list with battery_id
    trans_list      = [transducer_id for _ in range(len( filelist ))]

    # grasp the datetime from the filename
    datetime_list = []
    for single_name in filelist:
        st = _get_timestamp_from_filename( single_name )
        datetime_list.append( st )

    table_sorted = sort_by_name(filelist, starttime, table)                     # grasp the data instance and sort
    print (table_sorted.head().to_string())

    table_sorted['battery_id']      = battery_id_list                           # add battery id list into the report dateframe
    # table_sorted['collection_date'] = datetime_list                             # add collection date list into report dateframe
    table_sorted['transducer_id']   = trans_list



    '''
        For generating AVERAGE + tempC report
    '''
    # concat temperature
    tempTable = pd.DataFrame()
    tC_1, tC_2 = concat_all_data(tempC = True, search_key = 'cycle')
    tempTable['Temperature_bottom'] = tC_1                                      # construct a dataframe format for tempC
    tempTable['Temperature_top']    = tC_2                                      # construct a dataframe format for tempC
    
    table_sorted = pd.concat([table_sorted, tempTable['Temperature_bottom'],
                              tempTable['Temperature_top']], axis=1)            # add new column (diff index) into exisiing Dataframe
    
    del tempTable
    table_sorted.to_csv(final_log_path)



    return

#==============================================================================#
#                                                                              #
#                       constant variable                                      #
#                                                                              #
#==============================================================================#


keyword         = 'cycle'
battery_id      = input('Input Battery ID: \n')
# SoH             = input('Input SoH value: \n')
SoH = 98.34
date = '190523'
# date            = input('Testing date: \n')
transducer_id   = '039015'#'067143' #'09807'
name            = battery_id + '_H' + str(SoH) + '_' + str(date)

# name            = '18650_190320'
# actual_capacity = raw_input('Input Real capacity')

# path            ='/media/kacao/Ultra-Fit/titan-echo-boards/Echo-A/TC04-H74_181113/tempC/'
path            = '/media/kacao/Ultra-Fit/titan-echo-boards/18650/second_test/primary/18650_190605_merged.csv'
# path = th.ui.getdir('Pick your directory') + '/'                                # prompts user to select folder
cycler_path     = path + name + '.csv'
cycler_path_merged = path + name + '_merged_full.csv'
final_log_path  = path + name + '_sorted.csv'

__NEWARE__  = False
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove
ind = []                                                                        #list of stage index



if __name__ == '__main__':
    main()
