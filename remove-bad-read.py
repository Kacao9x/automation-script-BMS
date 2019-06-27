import subprocess
import numpy as np
import pandas as pd
import os
import json
from lib.echoes_signalprocessing import *
from lib.echoes_database import *
from bson import ObjectId
from lib.commandline import *
#==============================================================================#



def remove_data_on_mongo():
    echoes_db = database(database='echoes-captures')

    query = {
        '_id':ObjectId('5cf545b3f52b9cc6222e1b9f')
    }

    projection = {
        'temperature':1
    }
    match = {
        '$unset': {"raw_data.0" : 1}
    }

    res = echoes_db.find_one(query=query, projection=projection,
                        collection='nobatt')

    pprint (res)
    echoes_db.update(record=query, match=match,collection='nobatt')
    echoes_db.close()
    return


def rename_json_file(path):
    list_file = display_list_of_file_by_date(path)

    for captureID, filename in enumerate(list_file):

        with open(address + filename) as json_file:
            aCapture = json.load(json_file)
        json_file.close()


        with open(address + str(aCapture['capture_number']) + '.json', 'w') as writeout:
            writeout.write(json.dumps(aCapture))
        writeout.close()


    return


def main():
    path = '/media/kacao/Ultra-Fit/titan-echo-boards/18650/Todd_20190625/primary/'
    rename_json_file(path)
    # remove_data_on_mongo()
    # for i in range(1, 1800):

        # Call('rm ' + address + 'cycle' + str(i) + '-raw_trans-64-*')

        ##Call( 'mv ' + address + 'cycle' + str(i) +'-raw_trans-*' + ' ' + address + 'bad/')
        # if primary_channel:
        #     Call('rm ' + address + 'cycle' + str(i) + '-raw_echo-1-*')
        # else:
        #     Call('rm ' + address + 'cycle' + str(i) + '-raw_trans-1-*')
    
    # with open(address + 'bad-flat.txt', 'rb') as readout:
    #     for cnt, line in enumerate( readout ):
    #         # print (str(cnt))
    #         # print (line)
    #         line = line.rstrip()
    #         # cmd = 'rm ' + address + line #+ ' ' + address + 'primary/'
    #         cmd = 'mv ' + address + line + ' ' + address + 'bad/'
    #         Call( cmd )
    # readout.close()


    # list_file = display_list_of_file('cycle')
    # for idx, item in enumerate(list_file):
    #     if idx % 2 == 1:
    #         print (item)
    #         Call('mv ' + address + item + ' ' + address + 'bad/')

    # print (list_file)

    # for idx, aFile in enumerate(list_file):
    #     ele  = aFile.split('echoes')
    #     Call('mv ' + address + aFile + ' ' + address + ele[0] + ele[1])

    return


#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder

input_channel = 'primary'
primary_channel = (input_channel == 'primary')
print (str(primary_channel))

address = '/media/kacao/Ultra-Fit/titan-echo-boards/Mercedes_data/ME06/primary/'# + input_channel + '/'

if __name__ == '__main__':
    main()