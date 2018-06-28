import argparse
#from argparse import ArgumentParser: optimize the low-memory on Pi
#https://stackoverflow.com/questions/25295487/python-argparse-value-range-help-message-appearance

import sys, datetime

from echoes_protocol import echoes
from echoes_spi import *
from echoes_signalprocessing import *



def ParseHelpers(err=None):
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
                        choices=range(1,5000000), metavar="[1,500000]")

    parser.add_argument('-b', '-B', '--rate', default='2400000', type=int,
                        dest='rate', help='set sampling rate',
                        choices=range(10000, 2500001), metavar="[10000-2500000]")

    parser.add_argument('-c', '-C', '--gain', default='0.0', type=str,
                        dest='gain', help='set the VGA gain', metavar="[0.0, 1.0]")


    parser.add_argument('-v', '-V', '--voltage', default='10', type=int,
                        dest='voltage', help='set transducer voltage',
                        choices=range(10,90,5), metavar="[0,85, 5]")

    parser.add_argument('--input', default=1, type=int, choices=[1,2],
                        dest='input', metavar='1 or 2',
                        help='select input channel to collect data\n' +
                        '1.adc-primary  2.adc-secondary')

    parser.add_argument('--impulse-type', default=1, type=int, choices=[1,2],
                        dest='type', metavar='1 or 2',
                        help='select type of impulse\n' + '1.unipolar  2.bipolar')

    parser.add_argument('--period', type=int, default=1,help='periods',
                        dest='period',choices=[1,2,3], metavar='[1,2,3]')

    parser.add_argument('--half-pw', type=int,default='1', choices=range(1,7),
                        dest='half', help='input half period width' +
                                          '0.step'+'1.500ns',
                        metavar='select 0 to 6')


    parser.add_argument('--adc-config', type=int, default='0', choices=range(0,7),
                        dest='adcConfig', help='Input ADC config', metavar='[0,6]')

    parser.add_argument('--num-seq', type=int, default=1, choices=[1,2,4,8,16],
                        dest='numSeq', help='how many sequence to average together',
                        metavar='[1,2,4,8,16]')

    #============================ Add-on feature ==============================#

    parser.add_argument('--repeat', default=1, type=int, choices=range(1,61),
                        dest='repeat', metavar='[1,10]',
                        help='the number of repetition')

    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-l', '--logs', dest='logs', action='store_true',
                        help='Print logging messages')

    # args = parser.parse_args()

    try:
        args = parser.parse_args()
    except SystemExit as err:
        if err.code == 2:
            parser.print_help()

        sys.exit(0)

    if args.fresh:
        print "Start a new test"
    if args.resume:
        print "Resume the test"

#==============================================================================#
#================= create a test log file and set the name ====================#
def __get_filename__():
    return  "logs/" + "file-" + str(time.strftime("%Y%m%d_%H%M%S")) + ".txt"
    #time.clock() is an object, not string
    #https://www.dotnetperls.com/filename-date-python


def __write_test_logs__(name= ''):
    try:
        with open(name, 'ab') as writeout:
            writeout.writelines('the delay us is: ' + str(__DELAY__) + '\n')
            writeout.writelines('the VGA gain is: ' + __GAIN__ + '\n')
            writeout.writelines('the sampling rate is: ' + str(__SAMPLING__) + '\n')
            writeout.writelines('The volt transducer is'+ str(__VOLTAGE__) + '\n')
            writeout.writelines('The input channel to collect data'+ str(__INPUT__)+ '\n')
            writeout.writelines('The impulse type'+ str(__TYPE__)+ '\n')
            writeout.writelines('The impulse half period?'+ str(__HALF__) +'\n')
            writeout.writelines('Set conver sequence'+ str(__numSEQ__) + '\n')
            writeout.writelines('Set ADC config' + str(__adcCONFIG__) + '\n')
            writeout.writelines('number of Repeat' + str(__REPEAT__) + '\n')

    except:
        sys.exit("error to writing to job file")
    finally:
        writeout.close()
    return

#create test_logs file

#==============================================================================#
#======================== System Config =======================================#
def __system_config__(echo, echo_dsp):
    # 1. set voltage limit for transducer
    if echo.setImpulseVoltage(__VOLTAGE__):
        print "Successfully voltage setup"
    else:
        print "Failed voltage setup"

    # 2. Shape of the impulse
    if echo.setImpulseType(__TYPE__):
        print "Successfully set input type unipolar or bipolar"
    else:
        print "Failed input set input type"

    # 3. Half period width of pulse
    # Need to fix
    if __HALF__ == 1:
        print "half period width of pulse:500"
        print echo.setImpulseHalfPeriodWidth(500)
    else:
        #step
        print echo.setImpulseHalfPeriodWidth(65535)

    # switch

    # 4. number of period impulse
    if echo.setImpulseCycles(__PERIOD__):
        print "Successfully Impulse cycle setup"
    else:
        print "Failed Impulse cycle setup"


    # 5. select input capture channel:primary or secondary
    if echo.setCaptureADC(__INPUT__):
        print "Successfully input capture setup"
    else:
        print "Failed input input capture setup"

    # 6. select ADC sampling config:
    if __adcCONFIG__ == 0:
        result = echo.setAdcConfig(ADC_Config.fs_12bit_3_60msps)
        if result:
            echo_dsp.setFs(3600000.0)
            print("  Success!")
            print "Successfully ADC sampling config setup"
    else:
        print "Failed ADC sampling config setup"

    # 7. Set how many sequences to average together
    if echo.setConvertsPerSequence(__numSEQ__):
        print "Successfully set sequence to avg"
    else:
        print "Failed to set sequence to avg"


    # 8. Set sampling rate
    if echo.setVgaGain(__GAIN__):
        print "Successfully VGA gain setup"
    else:
        print "Failed VGA gain setup"

    # #9
    # if echo.setImpulseDelay(__DELAY__):
    #     print "Successfully delay_us setup"
    # else:
    #     print "Failed delay_us"

#==============================================================================#
#======================== MAIN FUNCTION =======================================#
def __capture_raw_data__(echo, num=int):
    echo.initiateCapture(True)
    # echoes_1(echoes_1.setImpulseType())
    totalpages = 1
    output = echo.readAdcData(pagesToRead=totalpages)
    y = output[0:totalpages * 2048];
    if output:

        y = y[0:2048]

        print("Generating data of " + str(len(y)) +
              " datapoints to log file")
        # Write file
        ts = time.time()
        st = 'cycle' + str(num) + '-' \
             + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        fn = "data/" + st + "-echoes-b.dat"

        filehandle = open(fn, "w")
        for samp in y:
            filehandle.write(str(samp) + "\n")
        filehandle.close()

def __capture_filtered_data_(echo, echo_dsp, num=int):
    echo.initiateCapture(True)
    # echoes_1(echoes_1.setImpulseType())
    totalpages = 1
    output = echo.readAdcData(pagesToRead=totalpages)
    y = output[0:totalpages * 2048];
    if output:

        if output:

            fsOriginal = echo_dsp.getFs()

            y = output[0:totalpages * 2048];

            print("Total samples: " + str(len(y)))

            if True:
                print("Removing DC offset")
                y = echo_dsp.removeDcOffset(y)

            if True:
                print("Upsampling")
                y = echo_dsp.upsample(y, 4)

            if False:
                print("Normalizing")
                y = echo_dsp.normalize(y)

            # Write file
            ts = time.time()
            st = 'cycle' + str(num) + '-' + 'filtered'\
                 + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
            fn = "data/" + st + "-echoes-b.dat"

            filehandle = open(fn, "w")
            for samp in y:
                filehandle.write(str(samp) + "\n")
            filehandle.close()

#==============================================================================#
#======================== MAIN ACTIVITY =======================================#
def main():
    __NAME__ = __get_filename__()
    print __NAME__
    __write_test_logs__(__NAME__)

    #send out op-code CMD over SPI prococol
    echoes_1 = echoes()
    echoes_dsp = echoes_signals(2400000.0)


    for i in range(__REPEAT__):
        print '\n\nCycle: ' + str(i)
        __system_config__(echoes_1, echoes_dsp)
        # Fire and capture the echoes
        print '.... Capture raw data...'
        __capture_raw_data__(echoes_1, i)
        time.sleep(1 * 10)
        print '.... Capture filtered data...'
        __capture_filtered_data_(echoes_1, echoes_dsp, i)
        time.sleep(1 * 10)

        print 'End cycle \n \n'




ParseHelpers()

__GAIN__        = args.gain
__SAMPLING__    = args.rate
__DELAY__       = args.delay_us
__VOLTAGE__     = args.voltage
__INPUT__       = args.input
__TYPE__        = args.type
__PERIOD__      = args.period
__HALF__        = args.half
__adcCONFIG__   = args.adcConfig
__numSEQ__      = args.numSeq

__REPEAT__      = args.repeat

if args.fresh:
    print "Start a new test"
    main()
else:
    #resume test
    result = args.delay_us*4
    print (result)

#DSP algo: filter reset(precondition data) -FIR
#high pass filter for DC offset, cutoff at 50khz
#output to webapp for screen display

# class Test(unittest.Testcase):
#
#     def testIt(self):
#         echoes_1 = echoes()
#
#         # Set delay_us to capture the waveform
#         # return True if successful setup
#         if echoes_1.setImpulseDelay(__DELAY__):
#             print "Successfully delay_us setup"

#
#         # Set sampling rate
#         if echoes_1.setVgaGain(__GAIN__):
#             print "Successfully VGA gain setup"
#
#         # set voltage limit for transducer
#         if echoes_1.setImpulseVoltage(__VOLTAGE__):
#             print "Successfully voltage setup"
#
#         # send CMD to readout value to STM32
#         if echoes_1.readAdcData():
#             print "blahblah"
#
#         #
#         if echoes_1.initiateCapture():
#             print "initateCapture"
#
#
#         return

# try:
#     options = parser.parse_args()
# except:
#     parser.print_help()
#     sys.exit(0)