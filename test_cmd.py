from lib.echoes_cmd_test import *
from lib.echoes_protocol import *
from lib.echoes_signalprocessing import *

import argparse, socket, subprocess


def main():
    global  test_config
    auto_test_1 = echoes_test(echoes_1, echoes_dsp)

    auto_test_1.is_new_Test(args.fresh)
    auto_test_1.system_config(test_config)

    for cycleID in range(auto_test_1.startCycle, __REPEAT__):
        pass
    return


# Creates an argument parser and parses the given arguments
def ParseHelpers():
    global parser, args

    test_options = ['merc', 'tuna']
    parser = argparse.ArgumentParser(description='CMD tool for auto testing')

    # ======================= Start CMD ====================================#
    parser.add_argument('--start-fresh', dest='fresh', action='store_true',
                        help='Start a new test, clears all saved files')
    parser.add_argument('--resume-test', dest='resume', action='store_true',
                        help='Resume testing from position in status.txt')

    # ======================= Setting parameters ===========================#
    parser.add_argument('-t', '--test', action='store', dest='test',
                        help='Choose the test: %s' ', '.join(test_options))

    parser.add_argument('-d', '--delayus', default=25, type=int,
                        dest='delay_us', help='set the time delay',
                        choices=range(1, 101), metavar="[1,100]")

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

    parser.add_argument('--impulse', default=1, nargs='*',
                        choices=[-2, -1, 1, 2], dest='type', metavar='[1 or 2]',
                        type=int, help='select type of impulse\n' +
                                       '1.unipolar  2.bipolar -1.unipolar-neg '
                                       '-2.bipolar-neg')

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

    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Enable debug mode')

    args = parser.parse_args()


#==============================================================================#
#                               GLOBAL VARIABLES                               #
#==============================================================================#

ParseHelpers()
bucket = {}

__TEST__ = args.test

bucket['test_setting']  = {
            'impulse_volt'  : args.voltage,
            'vga_gain'      : args.gain,
            'delay_ms'      : args.delay_us,
            'sampling_rate' : args.rate,
            'impulse_type'  : 'neg-bipolar' if args.type[0] == -2 else 'pos-bipolar',
            'input_channel' : 'primary' if args.input == 1 else 'secondary' if args.input == 2 else 'none'
        }

bucket['echoes_id']     = str(socket.gethostname())



__REPEAT__      = args.repeat
__MINUTE__      = args.minute


isNewRun = args.fresh
total_capture   = 64
battery_id      = 'TC02-H75'
examiner        = 'Khoi'
project         = 'TUNA002-Phase1-Build_ML_Model'
cabinet         = 'tuna-can'

print("Initializing EchOES 1 and 2")
echoes_1 = echoes()  # set Impulse=True for 2nd transducer
echoes_1.reset_micro()
echoes_1.start_new_session()

# print("Initializing database")
# echoes_db = database(database='echoes-captures')
# echoes_db.mongo_db = cabinet

print("Initializing signal processing")
echoes_dsp = echoes_signals(test_config['__SAMPLING__'])

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
