import argparse
#from argparse import ArgumentParser: optimize the low-memory on Pi
#https://stackoverflow.com/questions/25295487/python-argparse-value-range-help-message-appearance

import sys, time
import unittest



def ParseHelpers():
    global parser, args

    parser = argparse.ArgumentParser(description='start CMD line '
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
                        # choices=range(1,1000))
    # A = args.delay_us
    parser.add_argument('-b', '-B', '--rate', default='22000',
                        type=int, dest='rate', help='set sampling rate',
                        choices=range(10000, 50001), metavar="[10000-50000]")
                        # choices=[22000, 44000, 66000])
    # B = args.rate
    parser.add_argument('-c', '-C', '--gain', default='0.0', type=str,
                        dest='gain', help='set the VGA gain')
                        #(choices='0.0', '0.1', ... '9.9', '10.0')
    # C = args.gain

    parser.add_argument('-v', '-V', '--voltage', default='10', type=int,
                        dest='voltage', help='set transducer voltage',
                        choices=range(0,85,5), metavar="[0,85, 5]")

    parser.add_argument('--num-of-cycle-impulse', type=int, default=0,
                        dest='num_of_cycle',
                        help='number of cycles per impulse')
    # impulse = args.num_of_cycle
    parser.add_argument('--num-of-capture', type=int, default=0,
                        dest='capture', help='number of echoes to capture')
    # snapshot = args.capture

    parser.add_argument('--threshold', required=False, type=int, choices=range(0, 101),
                        help='Threshold (0-100) denoting at what threat level to provide',
                        metavar="[0-100]", default=49)

    #repetition rate:#num of cycle, freq
    #after runnning 10 min, rename the test_log file with a timestampe

    #============================ Add-on feature ==============================#
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-l', '--logs', dest='logs', action='store_true',
                        help='Print logging messages')

    args = parser.parse_args()


    answer = float(args.gain)
    if args.resume:
        print "the gain is: ".format(args.gain, answer)
    if args.gain == 4:
        print "the sampling rate".format(args.rate, args.rate)
    else:
        print "the time delay is: " + str(args.delay_us)

#==============================================================================#
#======= create a test log file and set the name =====#
def __get_filename():
    return  "file" + str(time.strftime("%Y%m%d_%H%M%S")) + ".txt"
    #time.clock() is an object, not string


def __write_test_logs(name= '', delay=int, gain=str, sample_rate=int):
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


#==============================================================================#
#======================== MAIN ACTIVITY =======================================#
def main():
    __NAME__ = __get_filename()
    print __NAME__
    __write_test_logs(__NAME__, __DELAY__, __GAIN__, __SAMPLING__)

    #execute the activity here over SPI prococol




#==============================================================================#


ParseHelpers()

__GAIN__    = args.gain
__SAMPLING__= args.rate
__DELAY__   = args.delay_us
__VOLTAGE__ = args.voltage
number_of_capture = args.num_of_cycle
number_of_cycle_impulse = args.capture

if args.fresh:
    print "Start a new test"
    main()
else:
    # A = args.delay_us
    # B = args.rate
    # C = args.gain
    # impulse = args.num_of_cycle
    # snapshot = args.capture
    result = args.delay_us*4
    print (result)

#DSP algo: filter reset(precondition data) -FIR
#high pass filter for DC offset, cutoff at 50khz
#output to webapp for screen display

class Test(unittest.Testcase):

    def testIt(self):
        echoes_1 = echoes()

        # Set delay_us to capture the waveform
        if echoes_1.setImpulseDelay(__DELAY__):
            print "Successfully delay_us setup"

        # Set sampling rate
        if echoes_1.setVGAGain(__GAIN__):
            print "Successfully VGA gain setup"

        # set voltage limit for transducer
        if echoes_1.setVoltage(__VOLTAGE__):
            print "Successfully voltage setup"

        
        return
