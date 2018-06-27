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

    parser.add_argument('-b', '-B', '--rate', default='22000', type=int,
                        dest='rate', help='set sampling rate',
                        choices=range(10000, 2500001), metavar="[10000-2500000]")
                        # choices=[22000, 44000, 66000])

    parser.add_argument('-c', '-C', '--gain', default='0.0', type=str,
                        dest='gain', help='set the VGA gain', metavar="[0.0, 1.0]")
                        #(choices='0.0', '0.1', ... '9.9', '10.0')

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


    # parser.add_argument('--adc-config')

    #============================ Add-on feature ==============================#

    parser.add_argument('--repeat', default=1, type=int, choices=range(1,11),
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


    answer = float(args.gain)
    if args.resume:
        print "the gain is: ".format(args.gain, answer)
    if args.gain == 4:
        print "the sampling rate".format(args.rate, args.rate)
    else:
        print "the time delay is: " + str(args.delay_us)

#==============================================================================#
#================= create a test log file and set the name ====================#
def __get_filename__():
    return  "logs/" + "file-" + str(time.strftime("%Y%m%d_%H%M%S")) + ".txt"
    #time.clock() is an object, not string
    #https://www.dotnetperls.com/filename-date-python


def __write_test_logs__(name= '', delay=int, gain=str, sample_rate=int):
    try:
        with open(name, 'ab') as writeout:
            writeout.writelines('the delay us is: ' + str(delay) + '\n')
            writeout.writelines('the VGA gain is: ' + gain + '\n')
            writeout.writelines('the sampling rate is: ' + str(sample_rate) + '\n')


    except:
        sys.exit("error to writing to job file")
    finally:
        writeout.close()
    return

#create test_logs file

#==============================================================================#
#======================== System Config =======================================#
def __system_config__(echo):
    if echo.setImpulseDelay(__DELAY__):
        print "Successfully delay_us setup"
    else:
        print "Failed delay_us"

    # Set sampling rate
    if echo.setVgaGain(__GAIN__):
        print "Successfully VGA gain setup"
    else:
        print "Failed VGA gain setup"

    # set voltage limit for transducer
    if echo.setImpulseVoltage(__VOLTAGE__):
        print "Successfully voltage setup"
    else:
        print "Failed voltage setup"

    # select input capture channel
    if echo.setCaptureADC(__INPUT__):
        print "Successfully input capture setup"
    else:
        print "Failed input input capture setup"

    # select Impulse type
    if echo.setImpulseType(__TYPE__):
        print "Successfully set input type [1,2,4,8,16]"
    else:
        print "Failed input set input type"

    # set the time for 1 cycle
    if echo.setImpulseCycles(__PERIOD__):
        print "Successfully Impulse cycle setup"
    else:
        print "Failed Impulse cycle setup"



def __sample_output__(echo, num=int):
    echo.initiateCapture(True)
    # echoes_1(echoes_1.setImpulseType())
    totalpages = 1
    output = echo.readAdcData(pagesToRead=totalpages)
    y = output[0:totalpages * 2048];
    if output:

        # fs = __SAMPLING__
        # y = output[0:totalpages * 2048];

        # echoes_dsp = echoes_signals(fs)
        # print("Removing DC offset")
        # y = echoes_dsp.removeDcOffset(y)

        # if True:
        #     y = echoes_dsp.applyBandpass(y)
        #
        # if True:
        #     print("Upsampling")
        #     y = echoes_dsp.upsample(y, 8)
        #     fs = fs * 8
        #
        # if True:
        #     print("Normalizing")
        #     y = echoes_dsp.normalize(y)
        #
        # if False:
        #     y = [i * 3.0 for i in y]

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

#==============================================================================#
#======================== MAIN ACTIVITY =======================================#
def main():
    __NAME__ = __get_filename__()
    print __NAME__
    __write_test_logs__(__NAME__, __DELAY__, __GAIN__, __SAMPLING__)

    #send out op-code CMD over SPI prococol
    echoes_1 = echoes()

    for i in range(__REPEAT__):
        print '\n\nCycle: ' + str(i)
        __system_config__(echoes_1)
        # Fire and capture the echoes
        __sample_output__(echoes_1, i)
        time.sleep(2*60)

        print 'End cycle \n \n'




ParseHelpers()

__GAIN__        = args.gain
__SAMPLING__    = args.rate
__DELAY__       = args.delay_us
__VOLTAGE__     = args.voltage
__INPUT__       = args.input
__TYPE__        = args.type
__PERIOD__      = args.period

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