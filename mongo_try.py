from lib.echoes_protocol import *
from lib.echoes_database import *
import subprocess

#=============================================================================#

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
#=============================================================================#

# display the file with keyword in ascending using BASH
def display_list_of_file(key):
    list_name = []
    list_cmd = ('ls '+ address +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        list_name.append(line.rstrip())

    return list_name


def _get_timestamp_from_filename( filename ):

    i = filename.split('-')
    # cycle1 - raw - 0 - 2018 - 08 - 31 - 16 - 44 - 34 - echoes - d
    if i[1] == 'temp':
        endtime = '2018' + '-' + i[3] + '-' + i[4] + ' ' \
                  + i[5] + ':' + i[6] + ':' + i[7]
        print ('endtime raw: ' + endtime)

    else:
        endtime = '2018' + '-' + i[4] + '-' + i[5] + ' ' \
                  + i[6] + ':' + i[7] + ':' + i[8]
        print ('endtime filtered: ' + endtime)

    return endtime


def read_pickle():
    record = echoes_1.getSessionData()
    print ('impulseVoltage: ' + str(record['impulseVoltage']))
    print ('impulseType: ' + str(record['impulseType']))
    print ('vga Gain: ' + str(record['vgaGain']))
    # print ('impulseCycle: ' + str(record['impulseCycles']))
    # print ('capture ADC: ' + str(record['captureAdc']))
    # print ('adc Sync Delay: ' + str(record['adcSynchroDelay']))

    return


def main(packet=None):

    read_pickle()

    packet = {}
    cycle = 10
    avgNum = 60
    amp, tC = [], []
    for cycle_num in range(cycle):

        filelist = display_list_of_file('cycle' + str(cycle_num + 1) + '-')
        print (filelist)

        for avg_num, name in enumerate( filelist ):
            #read the amplitude value
            with open( address + name ) as readout:
                y_str = readout.read()
                y_str = y_str.splitlines()
                amp = []
                for j, num in enumerate(y_str):
                    if j < len(y_str) - 1:
                        amp.append(float(num))
                    else:
                        if len(num.split()) > 2:
                            temp = num.rstrip().split('Temperature:')[1]
                            temp = temp.split('oC')[0]
                            tC.append(float(temp))
                        else:
                            amp.append(float(num))
            readout.close()


            record = echoes_1.getSessionData()
            # record['capture_data'] = amp
            # record['session'] = 'Me02-H100'
            # record['cycle_number']  = cycle_num + 1
            # record['avg_number']    = avg_num
            # record['source_filename'] = name

            packet['test_setting']['impulseVoltage']= record['impulseVoltage']
            packet['test_setting']['impulseType']   = record['impulseType']
            packet['test_setting']['vgaGain']       = record['vgaGain']

            packet['test_result']['data']           = amp
            packet['test_result']['session']        = 'Me02-H100'
            packet['test_result']['cycle_number']   = cycle_num + 1
            packet['test_result']['avg_number']     = avg_num
            packet['test_result']['source_filename']= name

            echoes_db.insert_capture(packet)

    print("time:" + str(datetime.datetime.now()))

    echoes_db.close()

    return



print("Initializing EchOES")

echoes_1 = echoes()
echoes_1.startNewSession()
echoes_1.setImpulseType(Impulse_Type.half)
echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_70v)
echoes_1.setVgaGain(0.55)

print("Initializing database")
echoes_db = database()
echoes_db.mongo_db = 'echoes-captures'

address = 'data/'                           # prompts user to select folder

if __name__ == '__main__':
    main()

