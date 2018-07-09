import subprocess, sys, os
import csv
import datetime as dt


keyword     = 'cycle'
path        = 'data/Filtered/NIS3_18-07-03.txt'
log_name    = 'data/Filtered/testlog.csv'
__PERIOD__  = 5                                                                 #second
__DIFF__    = 0                                                                 #the result of time difference btw start and stop
_start_row  = 6                                                                 #number of header to be remove
__CAP__     = 0


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
            line = readout.readline().rstrip()
    except:
        sys.exit("error to reading the file")
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

def _create_logfile_name(name=''):
    header = ('CycleID','StepID', 'Record ID','Time(H:M:S:ms)', 'Vol(mV)',
              'Cur(mA)','Temperature(?)', 'Cap(mAh)', 'CmpCap(mAh/g)',
              'Energy(mWh)','CmpEng(mWh/g)','Realtime')

    try:
        with open(name, 'ab') as outcsv:
            writer = csv.writer(outcsv, dialect='excel',
                                lineterminator='\r\n')
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

