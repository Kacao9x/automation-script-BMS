#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
TITAN Command Line Interface
See Github repo for documentation
@author: kacao
'''
'''
=============================================================================
                       HOW - TO - RUN - CMD LINE TOOL                       
tnr = transmission + reflection  |  tran = TRANSMISSION  |  ref = reflection
=============================================================================
python titan_cmd.py --start-fresh --test tran --channel 0 --batt TC36 --repeat 750 
--minute 5 --examiner Khoi
'''

import numpy as np
import argparse, socket
import json
import time
from pprint import pprint
from datetime import datetime
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
sys.path.insert(0,parentdir+"/lib")

from api.echoes_hardware_api import *
from api.lib.signal_processing.echoes_dsp import *
# from api.lib.database.aws_mongo import *


# =============================================================================#
#                                MAIN ACTIVITY                                 #
# =============================================================================#
def main():
    global __INPUT__
    global flag, capCount
    global status
    flag, capCount = 0, 0                                                       #used for detecting database connection issue
    
    create_data_folder()
    startCapture = fresh_or_resume()
    system_config()
    save_system_logs()


    for captureID in range(startCapture, __REPEAT__):

        print ('\nCycle: {}'.format(captureID + 1))

        # ============== PRIMARY ECHO ===============#
        if __TEST__ == 'tnr' or __TEST__ == 'ref':

            __INPUT__ = 1  # Set the ADC channel
            _capture_adc_init()  # Reset Input channel
            capture_signal_and_save_data(captureID + 1)
            print ('Completed capturing PRIMARY signal \n')

        # ============= TRANSMISSION ECHO ============#
        if __TEST__ == 'tnr' or __TEST__ == 'tran':

            __INPUT__ = 2
            _capture_adc_init()
            capture_signal_and_save_data(captureID + 1)
            print ('Completed capturing TRANSMISSION signal \n')
            __INPUT__ = 1

        # ============= TEST PERFORMANCE STATISTIC  ============#
        generate_test_statistic()

        print ('End cycle \n \n')
        time.sleep(__MINUTE__ * 60)

    echoes_hw.close()
    return


# =================  MAIN FUNCTION ENDS  ===============#

# =============================================================================#
#                               System Initializing                            #
# =============================================================================#

def create_data_folder():
    # ======= Create folder to save logs and data =======#
    ts_print = datetime.datetime.now().replace(microsecond=0).isoformat()
    #TO-DO: change the location save file
    try:
        if not os.path.exists(os.getcwd() + '/logs/'):
            os.makedirs(os.getcwd() + '/logs/')

        dirName = ['/data/primary', '/data/secondary', '/data/missed']

        for addr in dirName:
            print (addr)
            if not os.path.exists(os.getcwd() + addr):
                os.makedirs(os.getcwd() + addr)
            else:
                if not os.listdir(os.getcwd() + addr):
                    pass
                else:
                    print ('not empty data folder, creating new ones')
                    os.rename(os.getcwd() + addr, os.getcwd() + addr
                              + '_' + ts_print)
                    os.makedirs(os.getcwd() + addr)


    except OSError:
        sys.exit("Problem with creating data folder")

def generate_test_statistic():
    global status

    with open("logs/status.json", 'w') as writeout:  # Overwrite previous file
        writeout.write(json.dumps(status, indent=2, sort_keys=True))
    writeout.close()

    return


def fresh_or_resume():
    global status
    if isNewRun:
        print ("Start a fresh run")
        startCapture = 0
        status = {
            'current_capture'       : 0,
            'total_captures'        : 0,
            'failed_count'          : 0,
            'passed_count'          : 0,
            'noises_count'          : 0,
            'logging_report'		: [],
        }

    else:
        print ("Resume test from file")
        with open('logs/status.json') as json_file:
            status = json.load(json_file)
        json_file.close()
        startCapture = status['current_capture'] + 1

    return startCapture


def save_system_logs():

    st = str(time.strftime("%Y%m%d_%H%M%S"))
    name = os.path.join('logs/', '{}_{}.json'.format(__battID__, st))

    logs = {}
    logs['echoes_setting'] = echoes_hw.get_hardware_details()
    pprint (logs)
    logs['test_setting'] = {
        'total_capture'     : __REPEAT__,
        'sleep_time'        : __MINUTE__
    }

    with open(name, 'w') as writeout:
        writeout.write(json.dumps(logs, indent=2, sort_keys=True))
    writeout.close()

    return


# =============================================================================#
#                               System Config                                  #
# =============================================================================#
def system_config():
    #Primary or Secondary
    _capture_adc_init()
    time.sleep(0.5)

    # Master or Slave
    _input_channel()
    time.sleep(0.5)

    # Shape of voltage rails
    _impulse_type_init()
    time.sleep(0.5)

    # select input capture
    print (str(_capture_adc_init()))
    time.sleep(0.5)


    # Set VGA gain
    _VGA_gain_init()
    time.sleep(0.5)

    echoes_hw.set_total_adc_captures(total_captures=__TOTAL_SAMPLE__)
    return


def _capture_adc_init():
    """"
    Select primary (top)/secondary(bottom) channel to acquire the signal
    """
    print ('Set primary/secondary channel')
    if __INPUT__ == 1:
        return echoes_hw.set_capture_adc(ADC_PRIMARY)
    elif __INPUT__ == 2:
        return echoes_hw.set_capture_adc(ADC_SECONDARY)
    else:
        return False


def _input_channel():
    """
    Select master/slave channel to acquire data
    """
    print ('set capture channel: {}'.format(__CHANNEL__))
    return echoes_hw.set_capture_channel( __CHANNEL__ )


def _impulse_type_init():
    """
    Shape of the voltage rails
    """
    if __IMPULSE__ == 0:
        print ("unipolar: ")
        return echoes_hw.set_impulse_type(IMPULSE_HALF)
    elif __IMPULSE__ == 1:
        print ("bipolar: ")
        return echoes_hw.set_impulse_type(IMPULSE_FULL)
    elif __IMPULSE__ == 2:
        print ("unipolar-negative: ")
        return echoes_hw.set_impulse_type(IMPULSE_HALF_NEG)
    elif __IMPULSE__ == 3:
        print ("bipolar-negative: ")
        return echoes_hw.set_impulse_type(IMPULSE_FULL_NEG)

    return False


def _VGA_gain_init():
    print (__GAIN__)
    return echoes_hw.set_vga_gain(__GAIN__)


# =============================================================================#
#                       Signal Acquisition Supporting Method                   #
# =============================================================================#
def capture_raw_output():

    adc_captures        = echoes_hw.capture_and_read(send_impulse=True)
    adc_captures_float  = echoes_hw.convert_adc_raw_to_float(adc_captures)
    #TO-DO: implement remove_bad_sampling reads
    adc_captures_float,bad_idx = echoes_dsp.remove_bad_reads(adc_captures_float)

    adc_captures_filtered, adc_captures_avg = [], []
    if adc_captures_float:
        for idx, adc_capture in enumerate(adc_captures_float):
            adc_captures_filtered.append(echoes_dsp.apply_bandpass_filter(adc_capture, 300000.0, 1200000.0, filterlen=51))

        adc_captures_avg = np.mean(adc_captures_filtered, axis=0)
    else:
    	adc_captures_float = []
    	bad_idx = []

    return adc_captures_float, adc_captures_avg.tolist(), bad_idx



def _json_creator(captureID=int, adc_captures_float=[], adc_captures_avg=[], bad_idx=[]):
    global trans_primary, trans_secondary

    bucket = {
        'test_examiner'     : __EXAMINER__,
        'battery_id'        : __battID__,
        'transducer_id'     : [trans_primary, trans_secondary],
        'timestamp'         : datetime.datetime.now().replace(microsecond=0),
        'input_channel'     : __INPUT__,
        'test_setting'      : echoes_hw.get_hardware_details(),
        'capture_number'    : captureID,
        'raw_data'          : adc_captures_float,
        'average_data'      : adc_captures_avg,
        'removed_index'		: bad_idx,

    }

    return bucket


def save_data_to_file(captureID=int, bucket={}):
    global flag

    #bucket['timestamp'] = datetime.now().replace(microsecond=0).isoformat()
    bucket['timestamp'] = bucket['timestamp'].isoformat()
    print ('2nd timestamp: {}'.format(bucket['timestamp']))

    # if (__INPUT__ == 1 and flag != 1):
    #     st = 'cycle{}_echo_{}'.format(captureID, bucket['timestamp'])
    #     fn = 'data/primary/{}_{}.json'.format(st, __HOST__)
    # elif (__INPUT__ == 2 and flag !=1):
    #     st = 'cycle{}_trans_{}'.format(captureID, bucket['timestamp'])
    #     fn = 'data/secondary/{}_{}.json'.format(st, __HOST__)
    # else:
    #     st = 'cycle{}_{}'.format(captureID, bucket['timestamp'])
    #     fn = 'data/missed/{}_{}.json'.format(st, __HOST__)

    if (__INPUT__ == 1):
        st = 'cycle{}_echo_{}'.format(captureID, bucket['timestamp'])
        folder = 'primary' if flag != 1 else 'missed'
        
        fn = 'data/{}/{}_{}.json'.format(folder, st, __HOST__)
    elif (__INPUT__ == 2):
        st = 'cycle{}_trans_{}'.format(captureID, bucket['timestamp'])
        folder = 'secondary' if flag != 1 else 'missed'
        
        fn = 'data/{}/{}_{}.json'.format(folder, st, __HOST__)
    else:
        return

    
    with open(fn, 'w') as writeout:
        writeout.write(json.dumps(bucket, sort_keys=True))
    writeout.close()

    return


def save_data_to_mongo(bucket={}):
    global flag, echoes_db
    print("Initializing database")
    try:
        echoes_db = database(database='echoes-captures')
        print("database initialized")
    except:
        flag = 1
        print("database initialization failed")

    if echoes_db:     
        try:
            res = echoes_db.insert_capture(record=bucket, collection=__battID__)
            print(res)
        except:
            flag = 1
            print("Mongo - inserting capture failed")

        echoes_db.close()
    return

  
def save_dbconnect_error_log(captureID):
    st = str(time.strftime("%Y%m%d_%H%M%S"))
    filename = os.path.join('logs/','dbConnection_status.txt')
    
    with open(filename, 'a+') as f:
    	f.write("Database connection error occurred on: {}, with captureID= {}\n".format(st, captureID))
    f.close()
    return


def capture_signal_and_save_data(captureID=int):
    global flag, capCount, status
    
    # Generate BAM-BAM and capture the raw signal
    adc_captures_float, adc_captures_avg, bad_idx = capture_raw_output()

    
    bucket = _json_creator(captureID, adc_captures_float, adc_captures_avg, bad_idx)
    
    # new_logging_report = {captureID:bad_idx}
    status['logging_report'].append({captureID:bad_idx})
    status['current_capture'] = captureID
    
    if len(adc_captures_avg) == 0:
        status['failed_count'] = status['failed_count'] + 1
    elif len(adc_captures_float) < __TOTAL_SAMPLE__:
        status['noises_count'] = status['noises_count'] + 1
    else:
        status['passed_count'] = status['passed_count'] + 1

    # Save data to Mongo-aws
    # if flag == 0:
    #     save_data_to_mongo(bucket)
    # else:
    #     if capCount >= 5:
    #         save_data_to_mongo(bucket)
    #         capCount = 0
    #         flag     = 0
    #     else:
    #         save_dbconnect_error_log(captureID)
    #         capCount += 1
    #         print("captures saved locally, save to mongoDB failed\
    #             program automatically retry after {} cycles".format(5-capCount))
    
    # Save data on disk
    # del bucket['_id']
    save_data_to_file(captureID, bucket)        
    return


# Creates an argument parser and parses the given arguments
def ParseHelpers():
    global parser, args

    test_options = ['tnr', 'tran', 'ref']                                       # select test TRanmission, reflection or both
    parser = argparse.ArgumentParser(description='CMD tool for auto testing')

    # ======================= Start CMD ====================================#
    parser.add_argument('--start-fresh', dest='fresh', action='store_true',
                        help='Start a new test, clears all saved files')
    parser.add_argument('--resume-test', dest='resume', action='store_true',
                        help='Resume testing from position in status.txt')

    # ======================= Setting parameters ===========================#
    parser.add_argument('-t', '--test', action='store', dest='test',
                        help='Choose the test: %s' ', '.join(test_options))

    parser.add_argument('-b', '--batt', action='store', type=str,
                        dest='batteryID', help='battery ID')

    parser.add_argument('-e', '--examiner', action='store', type=str,
                        dest='examiner', help='Who run test?')

    parser.add_argument('-g', '--gain', default='0.55', type=str,
                        dest='gain', help='set the VGA gain',
                        metavar="[0.0, 1.0]")

    parser.add_argument('--input', default=1, type=int, choices=[1, 2],
                        dest='input', metavar='[1 or 2]',
                        help='select input channel to collect data ' +
                             '1.adc-primary  2.adc-secondary')

    parser.add_argument('--channel', default=0, type=int, choices=[0,1,2,3],
                        dest='channel', metavar='[0,1,2,3]',
                        help='select master-slave channel ' +
                             '0.A-master  1.B-master 2.C-slave 3.D-slave')

    parser.add_argument('--impulse', default=3, nargs='*',
                        choices=[0,1,2,3], dest='impulse', metavar='[1 or 2]',
                        type=int, help='0.unipolar  1.bipolar 2.unipolar-neg '
                                       '3.bipolar-neg')


    # ============================ Add-on feature ==============================#
    parser.add_argument('--repeat', default=1, type=int, choices=range(1, 250001),
                        dest='repeat', metavar='[1,250000]',
                        help='number of repetition')

    parser.add_argument('--minute', default=5, type=float,
                        dest='minute', metavar='[1,59]',
                        help='minutes to sleep')

    args = parser.parse_args()


# ==============================================================================#
#                               GLOBAL VARIABLES                               #
# ==============================================================================#

ParseHelpers()
__TEST__    = args.test
__battID__  = args.batteryID
__EXAMINER__= args.examiner
__GAIN__    = args.gain
__INPUT__   = args.input
__IMPULSE__ = args.impulse
__CHANNEL__ = args.channel

__REPEAT__  = args.repeat
__MINUTE__  = args.minute
__HOST__    = str(socket.gethostname())
__TOTAL_SAMPLE__ = 64

isNewRun = args.fresh

trans_primary   = None
trans_secondary = None
status = {}

print("Initializing EchOES 1 2")
echoes_hw = echoes_spi_api(debug=True)
echoes_hw.set_delay_between_captures(25)

echoes_uart = echoes_telemetry()
echoes_dsp  = echoes_dsp( 7200000.0 )



if __TEST__ is None:
    sys.exit('Please select Reflection or Tranmission test \n')
else:
    print ('Test selected: ' + args.test)

if args.fresh or args.resume:
    main()
else:
    print ("Test stopped! Please select start-fresh or resume-test")
