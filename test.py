#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
TITAN Command Line Interface
See Github repo for documentation
@author: kacao
'''
# python titan_cmd.py --start-fresh -a 15 -b 2400000 -c 0.75 -v 85 --input 1
# --impulse-type 2 --half-pw 100 --adc-config 0 --num-seq 1 --repeat 60 --minute 20
import argparse, sys

# from lib.echoes_spi import *
from lib.echoes_signalprocessing import *
from lib.echoes_protocol import *


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
    parser.add_argument('-a', '-A', '--delayus', default='1', type=int,
                        dest='delay_us', help='set the time delay',
                        choices=range(1, 5000000), metavar="[1,500000]")

    parser.add_argument('-b', '-B', '--rate', default='2400000', type=int,
                        dest='rate', help='set sampling rate',
                        choices=range(10000, 2500001), metavar="[10000-2500000]")

    parser.add_argument('-c', '-C', '--gain', default='0.0', type=str,
                        dest='gain', help='set the VGA gain', metavar="[0.0, 1.0]")

    parser.add_argument('-v', '-V', '--voltage', default='10', type=int,
                        dest='voltage', help='set transducer voltage',
                        choices=range(10, 90, 5), metavar="[0,85, 5]")

    parser.add_argument('--input', default=1, type=int, choices=[1, 2],
                        dest='input', metavar='[1 or 2]',
                        help='select input channel to collect data ' +
                             '1.adc-primary  2.adc-secondary')

    parser.add_argument('--impulse-type', default=1, type=int, choices=[1, 2],
                        dest='type', metavar='[1 or 2]',
                        help='select type of impulse\n' + '1.unipolar  2.bipolar')

    parser.add_argument('--period', type=int, default=1, help='periods',
                        dest='period', choices=[1, 2, 3], metavar='[1,2,3]')

    parser.add_argument('--half-pw', type=int, default=100,
                        choices=range(100, 1000, 50),
                        dest='half', help='input half period width' +
                                          '0.step' + '[100ns, 1000ns, 50]',
                        metavar='select 0 or value in range [100-1000]')

    parser.add_argument('--adc-config', type=int, default=0, choices=range(0, 7),
                        dest='adcConfig', help='Input ADC config', metavar='[0,6]')

    parser.add_argument('--num-seq', type=int, default='1', choices=[1, 2, 4, 8, 16],
                        dest='numSeq', help='how many sequence to average together',
                        metavar='[1,2,4,8,16]')

    # ============================ Add-on feature ==============================#
    parser.add_argument('--repeat', default=1, type=int, choices=range(1, 1001),
                        dest='repeat', metavar='[1,100]',
                        help='the number of repetition')

    parser.add_argument('--minute', default=20, type=int, choices=range(1, 60),
                        dest='minute', metavar='[1,59]', help='minutes to sleep')

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
        print "Start a new test"
    if args.resume:
        print "Resume the test"


# ==============================================================================#
# ================= create a test log file and set the name ====================#
def __get_filename():
    return "logs/" + "file-" + str(time.strftime("%Y%m%d_%H%M%S")) + ".txt"


def __write_test_logs(name=''):
    try:
        with open(name, 'ab') as writeout:
            writeout.writelines('the delay us is: ' + str(__DELAY__) + '\n')
            writeout.writelines('the VGA gain is: ' + __GAIN__ + '\n')
            writeout.writelines('the sampling rate is: ' + str(__SAMPLING__) + '\n')
            writeout.writelines('The volt transducer is' + str(__VOLTAGE__) + '\n')
            writeout.writelines('The input channel to collect data' + str(__INPUT__) + '\n')
            writeout.writelines('The impulse type' + str(__TYPE__) + '\n')
            writeout.writelines('The impulse half period?' + str(__HALF__) + '\n')
            writeout.writelines('Set conver sequence' + str(__numSEQ__) + '\n')
            writeout.writelines('Set ADC config' + str(__ADCconfig__) + '\n')
            writeout.writelines('number of Repeat' + str(__REPEAT__) + '\n')
            writeout.writelines('%s minutes to delay' % str(__MINUTE__) + '\n')

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
        print "unipolar: "
        return echoes_1.setImpulseType(Impulse_Type.half)
    elif __TYPE__ == 2:
        print "bipolar: "
        return echoes_1.setImpulseType(Impulse_Type.full)
    else:
        return False


def _half_pw_pulse_init():
    if __HALF__ == 0:
        print "step 65535ns: "
        return echoes_1.setImpulseHalfPeriodWidth(65535)
    elif (__HALF__ > 99) and (__HALF__ < 1001):
        print str(__HALF__) + 'ns'
        return echoes_1.setImpulseHalfPeriodWidth(__HALF__)

    else:
        return False


def _period_impulse_init():
    return echoes_1.setImpulseCycles(__PERIOD__)


def _input_capture_init():
    if __INPUT__ == 1:
        print "primary: "
        return echoes_1.setCaptureADC(Capture_Adc.adc_primary)
    elif __INPUT__ == 2:
        print "secondary: "
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
        print "12bit_7_2msps"
        result = echoes_1.setAdcConfig(ADC_Config.fs_12bit_7_2msps)
        if result:
            echoes_dsp.setFs(7200000.0)
            print("  Success!")
    else:
        print "Failed"


def _VGA_gain_init():
    print __GAIN__
    return echoes_1.setVgaGain(__GAIN__)


def system_config():
    # 1. set voltage limit for transducer
    print "(1) Voltage setup: %s " % str(_voltage_init())
    time.sleep(5)

    # 2. Shape of the impulse type unipolar or bipolar
    print "\n(2) Set input type: "
    print _input_type_init()
    time.sleep(5)

    # 3. Half period width of pulse
    # Need to fix
    print "\n(3) Half period width of pulse: "
    print _half_pw_pulse_init()
    time.sleep(5)

    # 4. number of period impulse
    print "\n(4) Number of period impulse: " + str(__PERIOD__)
    print str(_period_impulse_init())
    time.sleep(5)

    # 5. select input capture channel:primary or secondary
    print "\n(5) select input capture: "
    print str(_input_capture_init())
    time.sleep(5)

    # 6. select ADC sampling config:
    print "\n(6) select ADC sampling bits: "
    _ADC_sampling_init()
    time.sleep(5)

    # 7. Set how many sequences to average together
    print "\n(7) sequence to average: "
    print str(_sequence_init())
    time.sleep(5)

    # 8. Set VGA gain
    print "\n(8) set VGA gain: "
    print str(_VGA_gain_init())
    time.sleep(5)

    # 9
    # if echo.setImpulseDelay(__DELAY__):
    #     print "Successfully delay_us setup"
    # else:
    #     print "Failed delay_us"


# ==============================================================================#
# ======================== MAIN FUNCTION =======================================#
def _save_capture_data( num, key, y):
    # Write file
    ts = time.time()
    st = 'cycle' + str(num) + '-' + key + '-' \
         + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    fn = "data/" + st + "-echoes-b.dat"

    filehandle = open(fn, "w")
    for samp in y:
        filehandle.write(str(samp) + "\n")
    filehandle.close()
    return

def capture_raw_data(output=[]):
    y = output[0:totalpages * 2048];
    print("Total samples: " + str(len(y)))

    return y


def capture_filtered_data(output=[]):
    # fsOriginal = echoes_dsp.getFs()

    y = output[0:totalpages * 2048];

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


def is_dummy_data ( x ):
    last = 0.8 #threshold value
    count = 0
    for i in range (0, len(x)):
        if last > x[i]:
            count += 1

    return (count > 10)
# ==============================================================================#
# ======================== MAIN ACTIVITY =======================================#
def main():
    __NAME__ = __get_filename()
    print __NAME__
    __write_test_logs(__NAME__)

    # ======= UNIT TEST =======#
    # execute the activity here over SPI prococol
    system_config()
    for i in range(__REPEAT__):

        print '\n\nCycle: ' + str(i)
        #Emulate do-while loop
        #Keep firing until it collects a clean signal
        while True:
            echoes_1.initiateCapture(send_impulse=True)
            totalpages = 1
            output = echoes_1.readAdcData(pagesToRead=totalpages)
            if not is_dummy_data( output ):
                break

        if output:
            print '.... Capture raw data...'
            # totalpages = 1
            y =  capture_raw_data(output)
            _save_capture_data(i, 'raw', y )
            time.sleep(1 * 10)

            print '.... Capture filtered data...'
            z = capture_filtered_data(output)
            _save_capture_data(i, 'filtered', z)
            time.sleep(__MINUTE__ * 60)

        print 'End cycle \n \n'

    # ======= END UNIT TEST =======#


# ==============================================================================#


ParseHelpers()

__GAIN__ = args.gain
__SAMPLING__ = args.rate
__DELAY__ = args.delay_us
__VOLTAGE__ = args.voltage
__INPUT__ = args.input
__TYPE__ = args.type
__PERIOD__ = args.period
__HALF__ = args.half
__ADCconfig__ = args.adcConfig
__numSEQ__ = args.numSeq

__REPEAT__ = args.repeat
__MINUTE__ = args.minute

totalpages = 1

echoes_1 = echoes()
echoes_dsp = echoes_signals(2400000.0)

if args.fresh:
    print "Start a new test"
    main()
else:
    print "resume test"

# if args.test:
#     pass
# else:
#     parser.print_help()