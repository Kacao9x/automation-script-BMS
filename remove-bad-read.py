import subprocess
import numpy as np
import pandas as pd
import os


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

# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls '+ address +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name


def main():

    for i in range(1, 301):

        ## Call('rm ' + address + 'cycle' + str(i) + '-raw_trans-64-*')

        ##Call( 'mv ' + address + 'cycle' + str(i) +'-raw_trans-*' + ' ' + address + 'bad/')
        if primary_channel:
            Call('rm ' + address + 'cycle' + str(i) + '-raw_echo-1-*')
        else:
            Call('rm ' + address + 'cycle' + str(i) + '-raw_trans-1-*')
    
    with open(address + 'bad-flat.txt', 'rb') as readout:
        for cnt, line in enumerate( readout ):
            # print (str(cnt))
            # print (line)
            line = line.rstrip()
            cmd = 'rm ' + address + line #+ ' ' + address + 'primary/'
            # print (cmd)
            Call( cmd )
    readout.close()


    # list_file = display_list_of_file('cycle')
    # print (list_file)

    # for idx, aFile in enumerate(list_file):
    #     ele  = aFile.split('echoes')
    #     Call('mv ' + address + aFile + ' ' + address + ele[0] + ele[1])

    # for idx, item in enumerate(list_file):
    #     if idx % 2 == 1:
    #         print (item)
    #         Call('mv ' + address + item + ' ' + address + 'remove/')

    return


#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

input_channel = 'secondary'
primary_channel = (input_channel == 'primary')
print (str(primary_channel))

address = '/media/kacao/Ultra-Fit/titan-echo-boards/Echo-A/TC23-H722_190206/' + input_channel + '/'
# bad_data = []

# adc_captures_float = [[4,4,4,4,0,0,0,0], [4,4,4,4,0,0,0,0], [4,4,4,4,0,0,0,0]]
# backgrd = [2,2,2,2]

# for adc_capture in adc_captures_float:
#     noise_removal = True
#     if noise_removal:
#         print("Removing noise background")
#         adc_capture = [a_i - b_i for a_i, b_i in zip(adc_capture, backgrd)]

# adc_captures_readout = np.mean( adc_captures_float, axis = 0)
# print (adc_captures_readout)
# # adc_captures_readout = [a_i - b_i for a_i, b_i in zip(adc_captures_readout, backgrd)]
# adc_captures_readout = np.subtract( adc_captures_readout, backgrd )
# print (adc_captures_readout)

if __name__ == '__main__':
    main()