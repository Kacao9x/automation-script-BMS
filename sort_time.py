
import subprocess, sys, os
import csv

keyword = 'cycle'
__PERIOD__ = 5  #second

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

# ==============================================================================#

def getFileName():

    return


# return a tuple of string in every line (eat memory)
def readFile(name, row=int):
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
def readLineInFile(filename, line_number=int):
    # line_number: int  # Number of the required line, 0-based
    # line: str  # Content of the required line
    try:
        with open(filename) as file:
            for _ in range(line_number):
                file.readline()
            line = file.readline().lstrip().rstrip()
    except:
        sys.exit("error to reading the file")
    finally:
        file.close()

    return line



#the file == a readout of text file
def yieldlines(thefile, whatlines):
  return (x for i, x in enumerate(thefile) if i in whatlines)



def displayListOfFile(key):
    file_name = []
    list_cmd = ("ls data/ | grep '" + key + "' | awk '{print$1}'")

    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip().split('-echoes')[0])
    
    return file_name



def calculateTime():
    sec,remainder = 0,0
    if (sec2 - sec1) >= 0:
        sec += sec2 - sec1
    else:
        sec += sec2 + 60 - sec1
        remainder += 1

    if (min2 - min1 - remainder) >= 0:
        sec += (min2 - min1 -remainder)*60
        remainder = 0
    else:
        sec += (min2 + 60 - min1 - remainder)*60
        remainder = 1

    sec += (hour2 - hour1 - remainder)*60*60
    return sec

def __find_lines(second):
    return int(second/__PERIOD__)


def findTimeMatch():

    pass


# ==============================================================================#


name = displayListOfFile(keyword)
for element in name:
    i = element.split('-')
    print i
    if i[1] == '2018':
        hour2, min2,sec2 = (i[4], i[5], i[6])
        print "hour2 %s min2 %s sec2 %s" % (hour2, min2, sec2)
    else:
        hour2, min2, sec2 = (i[5], i[6], i[7])
        print "hour2 %s min2 %s sec2 %s" % (hour2, min2, sec2)


# line = readFile('data/NIS3-Charge-02-13-2018.txt', 12)
# line = readFile('data/NIS3-Charge-02-13-2018 (copy).txt', 1)
# print line[5]
# print line[6].split('\t')[9]

line = readLineInFile('data/NIS3-Charge-02-13-2018 (copy).txt', 5)
print line
starttime =  line.split(' ')[1]
print starttime
hour1, min1, sec1 = (starttime.split(':')[0], starttime.split(':')[1], starttime.split(':')[2])
print hour1 + ' ' + min1 + ' ' + sec1

# min1, sec1 = (line.split('\t')[1].split(':')[1], line.split('\t')[1].split(':')[2])
# print "a= %s" % str(min1)
# print "b= %s" % str(sec1)

print"\n"
print readLineInFile('data/NIS3-Charge-02-13-2018 (copy).txt', 6).split('\t')


hour1, min1, sec1 = int(hour1), int(min1), int(sec1)
hour2, min2, sec2 = int(hour2), int(min2), int(sec2)

timegap = calculateTime()
print 'Timegap: %s' % str(timegap)

linetofind = 6 + __find_lines(timegap)
print "Lines need to capture: %s" % str(linetofind)

line = readLineInFile('data/NIS3-Charge-02-13-2018.txt', linetofind)
print line



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

