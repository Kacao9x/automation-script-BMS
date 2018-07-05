
import subprocess, sys, os
import csv
import datetime as dt

keyword     = 'cycle'
path        = 'data/NIS3-Charge-02-13-2018 (copy).txt'
log_name    = 'data/testlog.csv'
__PERIOD__  = 5         #second
__DIFF__    = 0         #the result of time difference btw start and stop

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

# For instance this awk will print lines between 20 and 40
#
# awk '{if ((NR > 20) && (NR < 40)) print $0}' /etc/passwd
# ==============================================================================#



# return a tuple of string in every line (eat memory)
def read_file(name, row=int):
    words = []
    try:
        with open(name, 'rb') as readout:
            data = readout.readlines()
            for line in data:
                words.append(line.lstrip().rstrip())

    except:
        sys.exit("error to reading the test log")
    finally:
        readout.close()

    return words


# return a line in a string of character
# readline will read the next line from position of the console
def read_line_in_file(filename, line_number=int):
    # line_number: int  # Number of the required line, 0-based
    # line: str  # Content of the required line
    # global readout          #make sure this name is not used twice
    try:
        with open(filename) as readout:
            for _ in range(line_number):
                readout.readline()
            line = readout.readline().lstrip().rstrip()
    except:
        sys.exit("error to reading the file")
    finally:
        readout.close()

    return line

def _convert_to_time_object(str_obj):
    return dt.datetime.strptime(str_obj, '%Y-%m-%d %H:%M:%S')

#the file == a readout of text file
def yield_lines(thefile, whatlines):
  return (x for i, x in enumerate(thefile) if i in whatlines)



def display_list_of_file(key):
    file_name = []
    list_cmd = ("ls data/ | grep '" + key + "'") #| awk '{print$1}'")

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
    return 6 + int(second/__PERIOD__)

def _create_logfile_name(name=''):
    header = ('Record ID','Time(H:M:S:ms)', 'Vol(mV)', 'Cur(mA)',
              'Temperature(?)', 'Cap(mAh)', 'CmpCap(mAh/g)', 'Energy(mWh)',
              'CmpEng(mWh/g)','Realtime')

    try:
        with open(name, 'ab') as outcsv:
            writer = csv.writer(outcsv, dialect='excel',
                                lineterminator='\r\n')
            writer.writerow('\n')
            writer.writerow(header)
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


def find_corresponding_character(begin, end):
    __DIFF__ = calculate_time(begin, end)
    print "diff: %s" % str(__DIFF__)
    matched_line = _line_to_capture(__DIFF__)

    row = read_line_in_file(path, matched_line).split('\t')
    print row
    save_to_file(log_name, row)

    return



# ==============================================================================#


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

def main():
    #1. Create test log file to save data
    _create_logfile_name(log_name)

    #2. Open a log .txt to grasp the start time
    line = read_line_in_file(path, 5)
    print '#2' + line

    starttime = line.split('\t')[9]
    print '#2' + starttime

    #3. List filename that match a given pattern.
    #4. Loop through the list, Edit the format
    name = display_list_of_file(keyword)
    for element in name:
        print '#3' + element
        i = element.split('-')
        print i

        if i[1] == '2018':
            # endtime = "2018-02-16 11:10:22"
            endtime = '2018' + '-' + i[2] + '-' + i[3] + ' ' + i[4] + ':' + i[5] + ':' + i[6]
            print endtime

            find_corresponding_character(starttime, endtime)

        else:
            # endtime = "2018-02-15 11:10:22"
            endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' + i[5] + ':' + i[6] + ':' + i[7]
            print "endtime %s" % str(endtime)

            find_corresponding_character(starttime, endtime)


    return

if __name__ == '__main__':
    main()