#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
TITAN Command Line Interface
See Github repo for documentation
@author: kacao
'''

# =============================================================================#
#                                                                              #
#                       HOW - TO - RUN - CMD LINE TOOL                         #
# tnr = transmission + reflection  |  tran = TRANSMISSION  |  ref = reflection #                  #
# =============================================================================#
# python titan_cmd.py --start-fresh --test tran --batt TC36 --repeat 750 --minute 5 
# -- examiner Khoi

import numpy as np
import argparse, socket
import json
from time import time
from datetime import datetime

from lib.echoes_protocol import *
from lib.echoes_spi import *
from lib.echoes_temp_sensor import *
from lib.echoes_signalprocessing import *
from lib.echoes_database import *


# =============================================================================#
#                                MAIN ACTIVITY                                 #
# =============================================================================#
def main():
    global __INPUT__
    create_data_folder()
    fresh_or_resume()
    system_config()
    save_system_logs()
    

    for cycleID in range(startCycle, __REPEAT__):
        try:
            with open("logs/status.txt", 'w') as sf:  # Overwrite previous file
                sf.write(str(cycleID) + "\n")
            sf.close()
        except:  # Do nothing on error
            sys.exit("Problem with writing status.txt")

        print ('\nCycle: ' + str(cycleID + 1))

        # ============== PRIMARY ECHO ===============#
        __INPUT__ = 1  # Set the ADC channel
        _input_capture_init()  # Reset Input channel
        capture_signal(cycleID)
        print ('Completed capturing PRIMARY signal \n')

        # ============= TRANSMISSION ECHO ============#
        if __TEST__ == 'tnr':

            __INPUT__ = 2
            _input_capture_init()
            time.sleep(5)

            capture_signal(cycleID)
            print ('Completed capturing TRANSMISSION signal \n')
            __INPUT__ = 1

        elif __TEST__ == 'tran':
            pass  # Do nothing on secondary

        # ============== Save Temperature ==============#
        # _save_capture_data(cycleID, 'temp', [], True, True, False)

        print ('End cycle \n \n')
        time.sleep(__MINUTE__ * 60)

    echoes_1.close()
    return


# =================  MAIN FUNCTION ENDS  ===============#

# =============================================================================#
#                               System Initializing                            #
# =============================================================================#

def create_data_folder():
    # ======= Create folder to save logs and data =======#
    ts = time.time()
    ts_print = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    try:
        if not os.path.exists(os.getcwd() + '/logs/'):
            os.makedirs(os.getcwd() + '/logs/')

        dirName = ['/data/primary', '/data/secondary', '/tempC']

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


def fresh_or_resume():
    global startCycle
    if isNewRun:
        print ("Start a fresh run")
        startCycle = 0
    else:
        print ("Resume test from file")
        try:
            with open('logs/status.txt') as sf:
                startCycle = int(sf.readline().rstrip()) + 1
            sf.close()
        except:  # Do nothing on error
            sys.exit("Problem with status.txt")
    return


def save_system_logs():
    name = "logs/" + "file-" + str(time.strftime("%Y%m%d_%H%M%S")) + ".json"

    logs = {}
    logs['echoes_setting'] = echoes_1.get_session_data()
    print (logs)
    logs['test_setting'] = {
        'total_capture'     : __REPEAT__,
        'sleep_time'        : __MINUTE__
    }
    try:
        with open(name, 'w') as writeout:
            writeout.write(json.dumps(logs))
    except:
        sys.exit("error to writing to job file")
    finally:
        writeout.close()
    return


# =============================================================================#
#                               System Config                                  #
# =============================================================================#
def _voltage_init():
    print str(__VOLTAGE__)
    if __VOLTAGE__ == 85:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_85v.value)
    elif __VOLTAGE__ == 80:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_80v.value)
    elif __VOLTAGE__ == 75:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_75v.value)
    elif __VOLTAGE__ == 70:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_70v.value)
    elif __VOLTAGE__ == 65:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_65v.value)
    elif __VOLTAGE__ == 60:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_60v.value)
    elif __VOLTAGE__ == 55:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_55v.value)
    elif __VOLTAGE__ == 50:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_50v.value)
    elif __VOLTAGE__ == 45:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_45v.value)
    elif __VOLTAGE__ == 40:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_40v.value)
    elif __VOLTAGE__ == 35:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_35v.value)
    elif __VOLTAGE__ == 30:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_30v.value)
    elif __VOLTAGE__ == 25:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_25v.value)
    elif __VOLTAGE__ == 20:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_20v.value)
    elif __VOLTAGE__ == 15:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_15v.value)
    elif __VOLTAGE__ == 10:
        return echoes_1.set_impulse_type(Impulse_Voltage.impulse_10v.value)
    else:
        return False


def _impulse_type_init():
    global impulse_type
    if __TYPE__ == 0:
        print ("unipolar: ")
        impulse_type = 'pos-unipolar'
        return echoes_1.set_impulse_type(Impulse_Type.half.value)
    elif __TYPE__ == 1:
        print ("bipolar: ")
        impulse_type = 'pos-bipolar'
        return echoes_1.set_impulse_type(Impulse_Type.full.value)
    elif __TYPE__ == 2:
        print ("unipolar-negative: ")
        impulse_type = 'neg-unipolar'
        return echoes_1.set_impulse_type(Impulse_Type.half_negative.value)
    elif __TYPE__ == 3:
        print ("bipolar-negative: ")
        impulse_type = 'neg-bipolar'
        return echoes_1.set_impulse_type(Impulse_Type.full_negative.value)

    return False


def _period_impulse_init():
    return echoes_1.set_impulse_cycles(__PERIOD__)


def _input_capture_init():
    global input_channel

    if __INPUT__ == 1:
        input_channel = 'primary'
        print (input_channel + ' ')
        return echoes_1.set_capture_adc(Capture_Adc.adc_primary.value)
    elif __INPUT__ == 2:
        input_channel = 'secondary'
        print (input_channel + ' ')
        return echoes_1.set_capture_adc(Capture_Adc.adc_secondary.value)
    else:
        return False


def _VGA_gain_init():
    print __GAIN__
    return echoes_1.set_vga_gain(__GAIN__)


def system_config():
    # 1. set voltage limit for transducer
    print ("(1) Voltage setup: %s " % str(_voltage_init()))
    time.sleep(1)

    # 2. Shape of the impulse type unipolar or bipolar
    print ("\n(2) Set impulse type: %s" % str(_impulse_type_init()))
    time.sleep(1)


    # 3. number of period impulse
    print ("\n(3) Number of period impulse: " + str(__PERIOD__))
    print (str(_period_impulse_init()))
    time.sleep(1)


    # 4. select input capture channel:primary or secondary
    print ("\n(4) select input capture: ")
    print (str(_input_capture_init()))
    time.sleep(1)


    # 5. Set VGA gain
    print ("\n(5) set VGA gain: ")
    print (str(_VGA_gain_init()))
    time.sleep(1)

    echoes_1.set_total_adc_captures(total_captures=64)

    return


# =============================================================================#
#                       Signal Acquisition Supporting Method                   #
# =============================================================================#

# def _save_capture_to_file(cycleID=int, data_arr=[], tempC=[]):
#     ''' Save signal data readout'''
#     for runID, output in enumerate(data_arr):

#         ts = time()

#         if (output and __INPUT__ == 1):
#             st = 'cycle' + str(cycleID + 1) + \
#                  '-raw_echo-' + str(runID + 1) + \
#                  '-' + datetime.fromtimestamp(ts).strftime(
#                 '%Y-%m-%d-%H-%M-%S')
#             fn = "data/primary/" + st + "-" + __HOST__ + ".dat"

#         elif (output and __INPUT__ == 2):
#             st = 'cycle' + str(cycleID + 1) + \
#                  '-raw_trans-' + str(runID + 1) + \
#                  '-' + datetime.fromtimestamp(ts).strftime(
#                 '%Y-%m-%d-%H-%M-%S')
#             fn = "data/secondary/" + st + "-" + __HOST__ + ".dat"

#         else:
#             return

#         with open(fn, "w") as filehandle:
#             for samp in output:
#                 filehandle.write(str(samp) + "\n")
#         filehandle.close()

#     ''' Saving temperature readout '''
#     if tempC:
#         fn = "tempC/" + 'cycle' + str(cycleID + 1) + "-" + \
#             'temp-'+ datetime.fromtimestamp(ts).strftime(
#                 '%Y-%m-%d-%H-%M-%S') + '-' + __HOST__ + ".dat"
        
#         with open(fn, "w") as filehandle:
#             filehandle.write('TempC_1_and_2: %s  %s oC' % (str(tempC[0]),
#                                                            str(tempC[1])))
#         filehandle.close()
#     return

def _save_capture_to_file(cycleID=int, data_arr=[], tempC=[]):
    global trans_primary, trans_secondary
    ts = time.time()
    time_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    
    if (__INPUT__ == 1):
        st = 'cycle' + str(cycleID + 1) + '_echo_'+ time_str
        fn = "data/primary/" + st + "_" + __HOST__ + ".json"
    elif (__INPUT__ == 2):
        st = 'cycle' + str(cycleID + 1) + '_trans_'+ time_str
        fn = "data/secondary/" + st + "_" + __HOST__ + ".json"
    else:
        return


    bucket = {}
    bucket['test_examiner'] = __EXAMINER__
    bucket['timestamp']     = time_str


    bucket['battery_id']    = __battID__
    bucket['transducer_id'] =   {
        'primary'       : trans_primary,
        'secondary'     : trans_secondary
    }
    bucket['echoes_id']     = __HOST__
    
    bucket['test_setting'] = echoes_1.get_session_data()

    bucket['temperature']  = {
        'top'   : tempC[0],
        'bottom': tempC[1]
    }

    bucket['capture_number']    = cycleID + 1
    bucket['raw_data']          = []

    for output in data_arr:
        bucket['raw_data'].append(output)
    
    try:
        with open(fn, 'w') as writeout:
            writeout.write(json.dumps(bucket))
    except:
        sys.exit("error to writing to job file")
    finally:
        writeout.close()
        
    return


def _save_capture_to_Mongodb(cycleID=int, data_arr=[], tempC=[]):
    print("Initializing database")
    echoes_db           = database(database='echoes-captures')
    cabinet             = __battID__
    echoes_db.mongo_db  = cabinet

    global trans_primary, trans_secondary

    bucket = {}
    bucket['test_examiner'] = __EXAMINER__
    bucket['project_name']  = 'Phase1-BuildML-model'
    bucket['timestamp']     = datetime.datetime.now()


    bucket['battery_id']    = __battID__
    bucket['transducer_id'] =   {
        'primary'       : trans_primary,
        'secondary'     : trans_secondary
    }
    bucket['echoes_id']     = __HOST__
    
    bucket['test_setting'] = echoes_1.get_session_data()

    bucket['temperature']  = {
        'top'   : tempC[0],
        'bottom': tempC[1]
    }

    
    bucket['capture_number']    = cycleID + 1
    bucket['raw_data']          = []
    # avg = np.mean(data_arr, axis=0)
    # bucket['average_data']      = avg.tolist()

    for output in data_arr:
        bucket['raw_data'].append(output)

    try:
        res = echoes_db.insert_capture(record=bucket, collection=cabinet)
        print (res)
    except:
        print ("Error save file to mongo")
    
    echoes_db.close()
    return
    

def capture_raw_output():
    adc_captures = echoes_1.capture_and_read(send_impulse=True)
    adc_captures_float = echoes_1.convert_adc_raw_to_float(adc_captures)
    # adc_captures_float = echoes_1.remove_bad_reads(adc_captures_float)        # doesnt work for secondary trans

    return adc_captures_float


def capture_and_average_output(adc_captures_float):
    def _count_good_value(x):
        boundary = 0.015
        count = 0
        for num in x:
            if abs(num) > boundary:
                count += 1
        return count


    def _find_data_std(x):
        x_arr = np.array(x)
        x_arr = np.absolute(x_arr)
        return np.std(x_arr[50:-1], ddof=1)
    

    y_avg = np.array(adc_captures_float).mean(0)

    ''' detect a bad read in echo signal'''
    count       = _count_good_value(y_avg)
    std_value   = _find_data_std(y_avg)
    goodRead    = (count > 15 and std_value > 0.0020)

    # Keep firing until it collects a clean signal (PRIMARY SIGNAL ONLY)
    while (not goodRead) and (__INPUT__ == 1):
        print ('bad: cnt %s std_value: %s' % (str(count), str(std_value)))

        echoes_1.reset_micro()
        time.sleep(10)
        system_config()

        adc_captures_float = capture_raw_output()
        y_avg = np.array(adc_captures_float).mean(0)

        count       = _count_good_value(y_avg)
        std_value   = _find_data_std(y_avg)

        # detect a bad read
        goodRead = (count > 15 and std_value > 0.0020)

    print ('good echo: count %s  std_value: %s'
           % (str(count), str(std_value)))

    return adc_captures_float



def capture_signal(cycleID=int):
    adc_captures_float = capture_raw_output()
    adc_captures_float = capture_and_average_output(adc_captures_float)

    # Reading temperature sensor
    tempC_bottom = temp_sense_secondary.get_average_temperature_celcius(16)
    tempC_top = temp_sense_secondary.get_average_temperature_celcius(16)
    tempC = [tempC_top, tempC_bottom]

    # Capture signal and saving
    # _save_capture_to_Mongodb(cycleID, adc_captures_float, tempC)
    _save_capture_to_file(cycleID, adc_captures_float, tempC)

    print ("Successfully capture raw data")
    return


# Creates an argument parser and parses the given arguments
def ParseHelpers():
    global parser, args

    test_options = ['tnr', 'tran', 'ref']       # select test TRanmission, reflection or both
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

    parser.add_argument('-r', '--rate', default=7200000, type=int,
                        dest='rate', help='set sampling rate',
                        choices=range(2200000, 7500000),
                        metavar="[2.2M-7.5M]")

    parser.add_argument('-g', '--gain', default='0.55', type=str,
                        dest='gain', help='set the VGA gain',
                        metavar="[0.0, 1.0]")

    parser.add_argument('-v', '--voltage', default=85, type=int,
                        dest='voltage', help='set transducer voltage',
                        choices=range(10, 90, 5), metavar="[0,85, 5]")

    parser.add_argument('--input', default=1, type=int, choices=[1, 2],
                        dest='input', metavar='[1 or 2]',
                        help='select input channel to collect data ' +
                             '1.adc-primary  2.adc-secondary')

    parser.add_argument('--impulse', default=3, nargs='*',
                        choices=[0,1,2,3], dest='type', metavar='[1 or 2]',
                        type=int, help='0.unipolar  1.bipolar 2.unipolar-neg '
                                       '3.bipolar-neg')

    parser.add_argument('--period', type=int, default=1, help='periods',
                        dest='period', choices=[1, 2, 3], metavar='[1,2,3]')


    # ============================ Add-on feature ==============================#
    parser.add_argument('--repeat', default=1, type=int, choices=range(1, 1001),
                        dest='repeat', metavar='[1,100]',
                        help='number of repetition')

    parser.add_argument('--minute', default=5, type=int, choices=range(1, 60),
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
__SAMPLING__= args.rate
__VOLTAGE__ = args.voltage
__INPUT__   = args.input
__TYPE__    = args.type
__PERIOD__  = args.period

__REPEAT__  = args.repeat
__MINUTE__  = args.minute
__HOST__    = str(socket.gethostname())

isNewRun = args.fresh

trans_primary   = 98103
trans_secondary = 98102


print("Initializing EchOES 1 and 2")
echoes_1 = echoes()  # set Impulse=True for 2nd transducer
echoes_1.reset_micro()
echoes_1.start_new_session()

# print("Initializing database")
# echoes_db = database(database='echoes-captures')
# cabinet         = 'tuna-can-testing'
# echoes_db.mongo_db = cabinet

print("Initializing signal processing")
echoes_dsp = echoes_signals(__SAMPLING__)

print("Initializing temp sensor")
temp_sense_primary      = echoes_temp_sense(PRIMARY_TEMP_SENSE_ADDR)
temp_sense_secondary    = echoes_temp_sense(SECONDARY_TEMP_SENSE_ADDR)



if __TEST__ is None:
    __TEST__ = ' '
    print ('Battery type not selected \n')
else:
    print ('Test selected: ' + args.test)

if args.fresh or args.resume:
    main()
else:
    print ("Test stopped! Please select start-fresh or resume-test")
