
import subprocess, sys, os
import csv

keyword = 'cycle'
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


def readFile(name, row=int):
    words = []
    try:
        with open(name, 'rb') as readout:
            data = readout.readlines()
            for line in data:
                words.append(line.split())

    except:
        sys.exit("error to reading the test log")
    finally:
        readout.close()

    return words

def displayListOfFile(key):
    file_name = []
    list_cmd = ("ls data/ | grep '" + key + "' | awk '{print$1}'")

    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.lstrip('').rstrip('').split('-echoes')[0])
    
    return file_name


name = displayListOfFile(keyword)
for i in name:
    print i
# line = readFile('data/NIS3-Charge-02-13-2018.txt', 12)
line = readFile('data/NIS3-Charge-02-13-2018 (copy).txt', 1)
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

