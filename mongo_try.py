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

def main():
    filelist = display_list_of_file( 'temp' )
    print (filelist)

    tC = []
    for i, name in enumerate( filelist ):
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
    record['capture_data'] = tC
    record['session'] = 'ambient tempC'
    echoes_db.insert_capture( record )

    print("time:" + str(datetime.datetime.now()))

    return



print("Initializing EchOES")

echoes_1 = echoes()
echoes_1.startNewSession()
echoes_1.setImpulseType(Impulse_Type.full)
echoes_1.setImpulseVoltage(Impulse_Voltage.impulse_40v)
echoes_1.setVgaGain(0.6)

print("Initializing database")
echoes_db = database()

address = 'tempC/'                           # prompts user to select folder

if __name__ == '__main__':
    main()

