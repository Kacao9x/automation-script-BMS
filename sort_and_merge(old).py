import numpy as np
import glob
import pandas as pd

import subprocess, sys, os
import csv
import datetime as dt

keyword     = 'cycle'
path        = 'data/Cycler_Data_NIS3_180703.csv'
log_name    = 'data/testlog.csv'
__PERIOD__  = 5                                                                 #second
__DIFF__    = 0                                                                 #the result of time difference btw start and stop
_start_row  = 3                                                                 #number of header to be remove
__CAP__     = 0                                                                 #capacity of batt
header      = ('id', 'id_num', 'time', 'del', 'current',
            'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
            'en(microWh)', 'Date/Time')

header_new  = ('index', 'cap(mAh)', 'FileName')


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


# return the number of row
def _row_count(filename):
    # return sum(1 for row in open(filename))
    sum = 0
    with open(filename) as readout:
        for _ in readout:
            sum +=1
    readout.close()
    return sum



#return ID of execution
def _find_step_ID(filepath, key):
    ID = []
    try:
        with open(filepath) as readout:
            for index in range (_row_count(filepath)):
                line = readout.readline().rstrip()
                if (line[1]  == key[0]) | (line [1] == key[1]):
                    ID.append(index)
    except:
        sys.exit("error to find matching keyword")
    finally:
        readout.close()

    return ID


# return a line in a string of character
# readline will read the next line from position of the console
def read_line_in_file(filename, line_number=int):
    # line_number: int  # Number of the required line, 0-based
    # global readout          #make sure this name is not used twice
    row_num = _row_count(filename)

    if line_number > row_num:
        sys.exit('index out of bound')
    else:
        try:
            readout = open(filename, 'r')
        except:
            sys.exit("error to reading the file")
        else:
            for _ in range(line_number):
                readout.readline()
            line = readout.readline().rstrip()
        finally:
            readout.close()

    return line

# write data to a certan line in the file
# return True if successful, false otherwise
def write_line_in_file(filename, line_number=int):
    try:
        with open(filename) as readout:
            for _ in range(line_number):
                readout.writelines()
    except:
        sys.exit("error to reading the file")
        return False
    finally:
        readout.close()

    return True


def _convert_to_time_object(str_obj):
    return dt.datetime.strptime(str_obj, '%Y-%m-%d %H:%M:%S')


def display_list_of_file(key):
    file_name = []
    list_cmd = ("ls data/Filtered | grep '" + key + "'") #| awk '{print$1}'")

    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip().split('-echoes')[0])
    
    return file_name


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


def _line_to_capture(second):
    return _start_row + int(second/__PERIOD__)


def _create_logfile_name(name='', head=[]):

    try:
        with open(name, 'ab') as outcsv:
            writer = csv.writer(outcsv, dialect='excel',
                                lineterminator='\r\n')
            writer.writerow(head)
    finally:
        outcsv.close()

    return


def save_to_file(name='',data=[]):
    try:
        with open(name, 'ab') as outcsv:  # append in binary mode
            writer = csv.writer(outcsv)
            writer.writerow(data)
    finally:
        outcsv.close()

    return


def find_corresponding_character(begin, end, name=str):
    __DIFF__ = calculate_time(begin, end)
    print "diff: %s" % str(__DIFF__)
    matched_line = _line_to_capture(__DIFF__)

    #check if the index is out of bound

    row = read_line_in_file(path, matched_line).split(',')
    print '\n'

    temp_row = []
    temp_row.append(row[0])
    temp_row.append(row[5])
    temp_row.append(name)

    print temp_row
    save_to_file(log_name, temp_row)

    return


# ==============================================================================#
'''
for .txt, sep = '\t
for .csv, sep = ','
'''

'''
1. list of files in directory and save in the array[]
2. Loop through the array --> read name --> read timestamp
3. open the Batt test log
4. Loop/Scan through all lines. Save into an array? (memory consumption)
5. *Trick* 
    read the 2nd line. Store the start time
    Loop through array1[]
    Calculate how many lines to reach the first timestamp in test logs filename
    Grasp the whole line
'''
def sort_data(filename):
    my_file = open(filename)
    table = pd.read_csv(my_file, header=0, delimiter=',')

    table = table.sort_values('index')

    table.to_csv(r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data/test_log_sorted.csv")

    return

def Titan_Ashish():
    path_1 = r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data"
    table = pd.DataFrame()

    for filename in glob.glob(os.path.join(path_1, "*.txt")):
        my_file = open(filename)
        table = pd.read_csv(my_file, header=3, delimiter='\t')

    temp = table.iloc[:, 1:12]
    table = temp
    table.columns = ['id', 'id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                     'en(microWh)', 'Date/Time']
    del table['del']
    del table['del2']

    NA_finder = table['id'].notna()
    ind = []

    # find the stage index
    for i in range(len(NA_finder)):
        if NA_finder[i] == True:
            ind = np.append(ind, i)


    for i in range(len(ind)):

        if (table.iat[int(ind[i]), 1] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), 1]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, 4]
            diff = int(ind[i + 1]) - int(ind[i])

            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

        elif i == len(ind) - 1:

            tot = table.iat[int(len(NA_finder) - 1), 4]
            diff = int(len(NA_finder)) - int(ind[i])
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

    table.to_csv(r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data/Cycler_Data_NIS3_180703.csv")

    return


def main():
    row_num = _row_count(path)
    print 'num of row: ' + str(row_num)

    Titan_Ashish()
    #1. Create test log file to save data
    _create_logfile_name(log_name, header_new)

    #2. Open a log .txt to grasp the start time
    line = read_line_in_file(path, 2)
    print '#2 ' + line

    starttime = line.split(',')[9]
    print '#2 ' + str(starttime)

    #3. List filename that match a given pattern.
    #4. Loop through the list, Edit the format
    name = display_list_of_file(keyword)
    for element in name:
        print '#3' + element
        i = element.split('-')
        print i

        if i[1] == '2018':
            # endtime = "2018-02-16 11:10:22"
            endtime = '2018' + '-' + i[2] + '-' + i[3] + ' ' \
                      + i[4] + ':' + i[5] + ':' + i[6]
            print endtime

            find_corresponding_character(starttime, endtime, element)


        else:
            # endtime = "2018-02-15 11:10:22"
            endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' \
                      + i[5] + ':' + i[6] + ':' + i[7]
            print "endtime %s" % str(endtime)

            find_corresponding_character(starttime, endtime, element)

    sort_data(log_name)
    # keyID = ['2', 'CV_Charge']
    # print str(_find_step_ID(path, keyID))


    return

if __name__ == '__main__':
    main()



# ==============================================================================#
"""
No usage for now
"""
# For instance this awk will print lines between 20 and 40
#
# awk '{if ((NR > 20) && (NR < 40)) print $0}' /etc/passwd

#the file == a readout of text file
def yield_lines(thefile, whatlines):
  return (x for i, x in enumerate(thefile) if i in whatlines)


