#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
TITAN Command Line Interface
See Github repo for documentation
@author: kacao
'''
# python titan_cmd.py --start-fresh -a 15 -rate 2400000 -g 0.75 -v 85 --input 1
# --impulse 2 --half-pw 600 --adc-config 0 --num-seq 1 --repeat 60 --minute 20
import numpy as np
import argparse, sys
from lib.echoes_protocol import *
from lib.echoes_spi import *
from lib.echoes_temp_sensor import *
from lib.echoes_signalprocessing import *
from lib.echoes_database import *


# Command line arguments
def ParseHelpers():
    global parser, args

    parser = argparse.ArgumentParser(description='CMD line '
                                                 + 'argument for auto test'
                                                 + ' Must provide')
    # ======================= Start CMD ====================================#
    parser.add_argument('--start-fresh', dest='fresh', action='store_true',
                        help='Start a new test, clears all saved files')
    parser.add_argument('--resume-test', dest='resume', action='store_true',
                        help='Resume testing from position in status.txt')

    # ======================= Setting parameters ===========================#
    parser.add_argument('-a', '--delayus', default='1', type=int,
                        dest='delay_us', help='set the time delay',
                        choices=range(1, 5000000), metavar="[1,500000]")

    parser.add_argument('-b', '--rate', default='2400000', type=int,
                        dest='rate', help='set sampling rate',
                        choices=range(10000, 2500001),
                        metavar="[10000-2500000]")

    parser.add_argument('-g', '--gain', default='0.0', type=str,
                        dest='gain', help='set the VGA gain',
                        metavar="[0.0, 1.0]")

    parser.add_argument('-v', '--voltage', default='10', type=int,
                        dest='voltage', help='set transducer voltage',
                        choices=range(10, 90, 5), metavar="[0,85, 5]")

    parser.add_argument('--input', default=1, type=int, choices=[1, 2],
                        dest='input', metavar='[1 or 2]',
                        help='select input channel to collect data ' +
                             '1.adc-primary  2.adc-secondary')

    parser.add_argument('--impulse', default=1, nargs='*',
                        choices=[-2, -1, 1, 2],
                        dest='type', metavar='[1 or 2]', type=int,
                        help='select type of impulse\n' +
                             '1.unipolar  2.bipolar  -1.unipolar-neg  -2.bipolar-neg')

    parser.add_argument('--period', type=int, default=1, help='periods',
                        dest='period', choices=[1, 2, 3], metavar='[1,2,3]')

    parser.add_argument('--half-pw', type=int, default=100,
                        choices=range(100, 1300, 50),
                        dest='half', help='input half period width' +
                                          '0.step' + '[100ns, 1250ns, 50]',
                        metavar='select 0 or value in range [100-1250]')

    parser.add_argument('--adc-config', type=int, default=0,
                        choices=range(0, 5),
                        dest='adcConfig', help='Input ADC config',
                        metavar='[0,4]')

    parser.add_argument('--num-seq', type=int, default='1',
                        choices=[1, 2, 4, 8, 16],
                        dest='numSeq',
                        help='how many sequence to average together',
                        metavar='[1,2,4,8,16]')

    # ============================ Add-on feature ==============================#
    parser.add_argument('--repeat', default=1, type=int, choices=range(1, 1001),
                        dest='repeat', metavar='[1,100]',
                        help='the number of repetition')

    parser.add_argument('--minute', default=20, type=int, choices=range(1, 60),
                        dest='minute', metavar='[1,59]',
                        help='minutes to sleep')

    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Enable debug mode')

    parser.add_argument('-l', '--logs', dest='logs', action='store_true',
                        help='Print logging messages')

    args = parser.parse_args()

    # try:
    #     args = parser.parse_args()
    # except SystemExit as err:
    #     if err.code == 2:
    #         parser.print_help()

    if args.fresh:
        print ("Start a new test")
    if args.resume:
        print ("Resume the test")


# ==============================================================================#
# ================= create a test log file and set the name ====================#
def _get_filename():
    return "logs/" + "file-" + str(time.strftime("%Y%m%d_%H%M%S")) + ".txt"


def _write_test_logs(name='', offset=float):
    try:
        with open(name, 'ab') as writeout:
            writeout.writelines('the delay us is: ' + str(__DELAY__) + '\n')
            writeout.writelines('the VGA gain is: ' + __GAIN__ + '\n')
            writeout.writelines(
                'the sampling rate is: ' + str(__SAMPLING__) + '\n')
            writeout.writelines(
                'The volt transducer is ' + str(__VOLTAGE__) + '\n')
            writeout.writelines(
                'The input channel to collect data ' + str(__INPUT__) + '\n')
            writeout.writelines('The impulse type ' + str(__TYPE__) + '\n')
            writeout.writelines(
                'The impulse half period?  ' + str(__HALF__) + '\n')
            writeout.writelines('Set conver sequence ' + str(__numSEQ__) + '\n')
            writeout.writelines('Set ADC config ' + str(__ADCconfig__) + '\n')
            writeout.writelines('number of Repeat ' + str(__REPEAT__) + '\n')
            writeout.writelines('%s minutes to delay ' % str(__MINUTE__) + '\n')
            writeout.writelines('DC offset %s: ' % str(offset) + '\n')
            writeout.writelines('\n')

    except:
        sys.exit("error to writing to job file")
    finally:
        writeout.close()
    return


# ==============================================================================#
# ======================== System Config =======================================#
def _voltage_init():
    print str(__VOLTAGE__)
    if __VOLTAGE__ == 85:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_85v)
    elif __VOLTAGE__ == 80:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_80v)
    elif __VOLTAGE__ == 75:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_75v)
    elif __VOLTAGE__ == 70:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_70v)
    elif __VOLTAGE__ == 65:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_65v)
    elif __VOLTAGE__ == 60:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_60v)
    elif __VOLTAGE__ == 55:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_55v)
    elif __VOLTAGE__ == 50:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_50v)
    elif __VOLTAGE__ == 45:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_45v)
    elif __VOLTAGE__ == 40:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_40v)
    elif __VOLTAGE__ == 35:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_35v)
    elif __VOLTAGE__ == 30:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_30v)
    elif __VOLTAGE__ == 25:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_25v)
    elif __VOLTAGE__ == 20:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_20v)
    elif __VOLTAGE__ == 15:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_15v)
    elif __VOLTAGE__ == 10:
        return echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_10v)
    else:
        return False


def _input_type_init():
    if __TYPE__ == 1:
        print ("unipolar: ")
        return echoes_1.setImpulseType(Impulse_Type.half)
    elif __TYPE__ == 2:
        print ("bipolar: ")
        return echoes_1.setImpulseType(Impulse_Type.full)
    elif __TYPE__ == -1:
        print ("unipolar-negative: ")
        return echoes_1.setImpulseType(Impulse_Type.half_negative)
    elif __TYPE__ == -2:
        print ("bipolar-negative: ")
        return echoes_1.setImpulseType(Impulse_Type.full_negative)
    return False


def _half_pw_pulse_init():
    if __HALF__ == 0:
        print ("step 65535ns: ")
        return echoes_1.setImpulseHalfPeriodWidth(65535)
    elif (__HALF__ > 99) and (__HALF__ < 1400):
        print str(__HALF__) + 'ns'
        return echoes_1.setImpulseHalfPeriodWidth(__HALF__)

    else:
        return False


def _period_impulse_init():
    return echoes_1.setImpulseCycles(__PERIOD__)


def _input_capture_init():
    if __INPUT__ == 1:
        print ("primary: ")
        return echoes_1.setCaptureADC(Capture_Adc.adc_primary)
    elif __INPUT__ == 2:
        print ("secondary: ")
        return echoes_1.setCaptureADC(Capture_Adc.adc_secondary)
    else:
        return False


def _sequence_init():
    print str(__numSEQ__)
    if __numSEQ__ == 1:
        return echoes_1.setConvertsPerSequence(Sequence_Count.sequence_1)
    elif __numSEQ__ == 2:
        return echoes_1.setConvertsPerSequence(Sequence_Count.sequence_2)
    elif __numSEQ__ == 4:
        return echoes_1.setConvertsPerSequence(Sequence_Count.sequence_4)
    elif __numSEQ__ == 8:
        return echoes_1.setConvertsPerSequence(Sequence_Count.sequence_8)
    elif __numSEQ__ == 16:
        return echoes_1.setConvertsPerSequence(Sequence_Count.sequence_16)
    else:
        return False


def _ADC_sampling_init():
    if __ADCconfig__ == 0:
        print ("12bit_7_2msps")
        result = echoes_1.setAdcConfig(ADC_Config.fs_12bit_7_2msps)
        if result:
            echoes_dsp.setFs(7200000.0)
            print("  Success!")
        else:
            print ('error updating sampling rate')
    elif __ADCconfig__ == 1:
        print ("10bit_8_31msps")
        result = echoes_1.setAdcConfig(ADC_Config.fs_10bit_8_31msps)
        if result:
            echoes_dsp.setFs(8310000.0)
            print("  Success!")
        else:
            print ('error updating sampling rate')
    elif __ADCconfig__ == 2:
        print ("8bit_9_82msps")
        result = echoes_1.setAdcConfig(ADC_Config.fs_08bit_9_82msps)
        if result:
            echoes_dsp.setFs(9820000.0)
            print("  Success!")
        else:
            print ('error updating sampling rate')
    elif __ADCconfig__ == 3:
        print ("6bit_12_00msps")
        result = echoes_1.setAdcConfig(ADC_Config.fs_06bit_12_00msps)
        if result:
            echoes_dsp.setFs(12000000.0)
            print("  Success!")
        else:
            print ('error updating sampling rate')
    else:
        print ("Failed setting samping rate")


def _VGA_gain_init():
    print __GAIN__
    return echoes_1.setVgaGain(__GAIN__)


def system_config():
    # 1. set voltage limit for transducer
    print ("(1) Voltage setup: %s " % str(_voltage_init()))
    time.sleep(5)

    # 2. Shape of the impulse type unipolar or bipolar
    print ("\n(2) Set input type: ")
    print _input_type_init()
    time.sleep(5)

    # 3. Half period width of pulse
    # Need to fix
    # print ("\n(3) Half period width of pulse: ")
    # print _half_pw_pulse_init()
    # time.sleep(5)

    # 4. number of period impulse
    print ("\n(4) Number of period impulse: " + str(__PERIOD__))
    print (str(_period_impulse_init()))
    time.sleep(5)

    # 5. select input capture channel:primary or secondary
    print ("\n(5) select input capture: ")
    print (str(_input_capture_init()))
    time.sleep(5)

    # 6. select ADC sampling config:
    print ("\n(6) select ADC sampling bits: ")
    # _ADC_sampling_init()
    echoes_dsp.setFs(7200000.0)
    print("  Success!")
    time.sleep(5)

    # 7. Set how many sequences to average together
    print ("\n(7) sequence to average: ")
    print (str(_sequence_init()))
    time.sleep(5)

    # 8. Set VGA gain
    print ("\n(8) set VGA gain: ")
    print (str(_VGA_gain_init()))
    time.sleep(5)

    # 9
    # if echo.setImpulseDelay(__DELAY__):
    #     print "Successfully delay_us setup"
    # else:
    #     print "Failed delay_us"


# ==============================================================================#
# ======================== MAIN FUNCTION =======================================#
def _save_capture_data(cycleID, key, data, temper):
    # Write file
    ts = time.time()
    st = 'cycle' + str(cycleID + 1) + '-' + key + '-' \
         + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

    if temper:
        fn = "tempC/" + st + "-echoes-e.dat"

        tempC_1 = temp_sense_primary.get_average_temperature_celcius(16)
        tempC_2 = temp_sense_primary.get_average_temperature_celcius(16)
        filehandle = open(fn, "w")
        filehandle.write('Temperature_1_and_2: %s  %s oC' % (str(tempC_1),
                                                             str(tempC_2)))
        filehandle.close()
    else:
        fn = "data/" + st + "-echoes-e.dat"
        filehandle = open(fn, "w")
        for samp in data:
            filehandle.write(str(samp) + "\n")
        filehandle.close()
    return


# def _save_capture_to_Mongodb( cycleID=int, key=str, data=[], temper=bool,
#                               record = {} ):
#     ts = time.time()
#     st = 'cycle' + str(cycleID + 1) + '-' + key + '-' \
#          + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
#
#     packet = {}
#     packet['test_results'] = {}
#     packet['test_setting'] = {}
#     packet['test_apparatus'] = {}
#
#     record = echoes_1.getSessionData()
#     packet['test_results']['data'] = data
#     packet['test_results']['cycle_number'] = cycleID + 1
#     packet['test_results']['avg_number'] = key.split('-')[1]
#     packet['test_results']['timestamp'] = st
#
#
#     packet['test_setting']['impulseVoltage']= record['impulseVoltage']
#     packet['test_setting']['impulseType']  = record['impulseType']
#     packet['test_setting']['vgaGain']      = record['vgaGain']
#
#     packet['test_apparatus']['session'] = 'Me02-H100'
#
#
#     if temper:
#         # tempC_1 = temp_sense_primary.get_average_temperature_celcius(16)
#         # tempC_2 = temp_sense_secondary.get_average_temperature_celcius(16)
#         packet['test_results']['temperature_1'] = \
#             temp_sense_primary.get_average_temperature_celcius(16)
#         packet['test_results']['temperature_2'] = \
#             temp_sense_secondary.get_average_temperature_celcius(16)
#
#     echoes_db.insert_capture(packet)
#     return


def filter_raw_data(output=[]):
    y = output[0: totalpages * 2048]
    print("Total samples: " + str(len(y)))
    if True:
        print("enable Bandpass in raw data")
        bandpass_upper = float(3500000)
        bandpass_lower = float(300000)
        y = echoes_dsp.applyBandpass(y, bandpass_lower, bandpass_upper, 51)
    return y


def capture_filtered_data(output=[]):
    # fsOriginal = echoes_dsp.getFs()

    y = output[0: totalpages * 2048]
    print("Total samples: " + str(len(y)))

    if True:
        print("Removing DC offset")
        y = echoes_dsp.removeDcOffset(y)

    if True:
        print("Upsampling")
        y = echoes_dsp.upsample(y, 4)

    if False:
        print("Normalizing")
        y = echoes_dsp.normalize(y)

    # fs = echoes_dsp.getFs()
    return y


def capture_and_average_output(num, key, pagesToRead, offset):
    outputs = []

    adc_captures = echoes_1.capture_and_read(send_impulse=True)
    adc_captures_float = echoes.convert_adc_raw_to_float(adc_captures)
    adc_captures_float = echoes.remove_bad_reads(adc_captures_float)

    y_avg = np.array(adc_captures_float).mean(0)
    for i, output in enumerate(adc_captures_float):
        # y = filter_raw_data( output )                                           #enable bandpass
        _save_capture_data(num, key + '-' + str(i + 1), output,
                           False)  # don't save temperature
        # _save_capture_to_Mongodb( num, key + '-' + str( i + 1 ), output, False )

    return y_avg


def count_good_value(x):
    boundary = 0.015
    count = 0
    for i in range(0, len(x)):
        if boundary < abs(x[i]):
            count += 1

    return count


def find_data_std(x):
    x_arr = np.array(x)
    x_arr = np.absolute(x_arr)
    return np.std(x_arr[50:-1], ddof=1)


# ==============================================================================#
# ======================== MAIN ACTIVITY =======================================#
def main():
    __NAME__ = _get_filename()

    # ======= SET UP TEST PARAMETERs =======#
    system_config()
    echoes_1.measure_dc_offset()
    offSet = echoes_1.dcOffset
    echoes_1.set_total_adc_captures(total_capture)
    _write_test_logs(__NAME__, offSet)

    for i in range(__REPEAT__):
        print ('\nCycle: ' + str(i + 1))

        goodRead = False
        y_avg = capture_and_average_output(i, 'raw', totalpages,
                                           offSet)  # don't save temperature
        y_avg = filter_raw_data(y_avg)

        # detect a bad read
        count = count_good_value(y_avg)
        std_value = find_data_std(y_avg)
        goodRead = (count > 15 and std_value > 0.0020)
        # _save_capture_data(i, 'avg', y_avg, False)

        # Keep firing until it collects a clean signal
        while not goodRead:
            print ('bad data: count %s  std_value: %s' %
                   (str(count), str(std_value)))

            echoes_1.resetMicro()
            time.sleep(10)
            system_config()
            echoes_1.measureDcOffset()
            offSet = echoes_1.dcOffset
            _write_test_logs(__NAME__, offSet)

            y_avg = capture_and_average_output(i, 'raw', 1,
                                               offSet)  # don't save temperature
            count = count_good_value(y_avg)
            std_value = find_data_std(y_avg)

            # detect a bad read
            goodRead = (count > 15 and std_value > 0.0020)

        print ('good: count %s  std_value: %s' % (str(count), str(std_value)))
        _save_capture_data(i, 'avg', y_avg, False)

        _save_capture_data(i, 'temp', 0, True)  # save temperature
        time.sleep(__MINUTE__ * 60)

        print ('End cycle \n \n')
    # echoes_db.close()
    echoes_1.close()

    # ======= END UNIT TEST =======#


# ==============================================================================#

ParseHelpers()

__GAIN__ = args.gain
__SAMPLING__ = args.rate
__DELAY__ = args.delay_us
__VOLTAGE__ = args.voltage
__INPUT__ = args.input
__TYPE__ = args.type[0]
__PERIOD__ = args.period
__HALF__ = args.half
__ADCconfig__ = args.adcConfig
__numSEQ__ = args.numSeq

__REPEAT__ = args.repeat
__MINUTE__ = args.minute

total_capture = 64
totalpages = 1

print("Initializing EchOES")
echoes_1 = echoes()
echoes_1.resetMicro()
echoes_1.startNewSession()

# print("Initializing database")
# echoes_db       = database()
# echoes_db.mongo_db = 'echoes-captures'

print("Initializing signal processing")
echoes_dsp = echoes_signals(2400000.0)

print("Initializing temp sensor")
temp_sense_primary = echoes_temp_sense(PRIMARY_TEMP_SENSE_ADDR)
temp_sense_secondary = echoes_temp_sense(SECONDARY_TEMP_SENSE_ADDR)

if args.fresh:
    print ("Start a new test")
    main()
else:
    print ("resume test")

# if args.test:
#     pass
# else:
#     parser.print_help()
