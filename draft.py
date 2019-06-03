
# Program to show the use of continue statement inside loops


from enum import Enum
import json as j
import numpy as np
import os
import json
from datetime import datetime, timedelta
from time import time
import pytz


class LED_Color(Enum):
    __order__ = 'red green blue yellow purple'
    red = 0
    green = 1
    blue = 2
    yellow = 3
    purple = 4


def test_Enum34(color):
    p = LED_Color.red
    print('The string representation of enum member is: ', p)
    print('The value representation: ', repr(p))

    for item in LED_Color:
        print (item.value)


    if color is LED_Color.red.value:
        print ("RRR")
    elif color is LED_Color.green.value:
        print("GGGG")
    elif color is LED_Color.blue.value:
        print("BBBB")


def test_boolean_operator():
    result = False
    result |= True
    print (result)


def test_branching_function():
    for val in "string":
        if val == "i":
            continue
        print(val)

    i = 1
    cycle = 5
    while i < cycle + 1:
        i += 1
        if i == 3:
            continue
        print (i)
        

    print("The end")

    st = 'cycle294-temp-2019-01-29-20-05-31echoes-c.dat'

    i = st.split('echoes')
    print (i)

def test_console_input():
    name = input("What's ur name? \n")
    age = input("What's your age? \n")
    print("So, you are already " + age + " years old, " + name + "!")


def calculate_mean_value():
    adc_captures_float = [[4,4,4,4,0,0,0,0], [4,4,4,4,0,0,0,0], [4,4,4,4,0,0,0,0]]
    backgrd = [2,2,2,2]

    for adc_capture in adc_captures_float:
        noise_removal = True
        if noise_removal:
            print("Removing noise background")
            adc_capture = [a_i - b_i for a_i, b_i in zip(adc_capture, backgrd)]

    adc_captures_readout = np.mean( adc_captures_float, axis = 0)
    print (adc_captures_readout)
    # adc_captures_readout = [a_i - b_i for a_i, b_i in zip(adc_captures_readout, backgrd)]
    adc_captures_readout = np.subtract( adc_captures_readout, backgrd )
    print (adc_captures_readout)


def edit_element_numpy():
    arr = [1, 2, 3, 4]
    temp_1 = 21
    temp_2 = 20
    xxx = np.array([temp_1, temp_2])
    print (xxx[1])
    # arr = [[1,2], [3,4]]
    arr_np = np.array(arr)
    for id, ele in enumerate(arr):
        ele += 2
        # arr[id] = ele
    # arr = [ele +2 for ele in arr]
    print (arr)
    
    for ele in np.nditer(arr_np, op_flags=['readwrite']):
        ele += 2
    print (arr_np)


def JSON_to_file():
    FILE = 'data/average.json'
    try:
        with open(FILE, 'r') as f:
            jsonData = j.load(f)
            all_captures = jsonData["avg_captures"]
        f.close()
    except IOError:
        all_captures = []

    print(all_captures)
    # jsonData = {}
    # jsonData['avg_captures'] = []
    # signal = [1, 3, 5, 7, 9]
    signal = np.array([[0,1,2],[3,4,5],[6,7,8]]).tolist()
    with open(FILE, 'wb') as file:
        jsonData["avg_captures"].append( signal )
        file.write(j.dumps(jsonData))

    file.close()
    


def use_timeout_with_signal():
    import signal
    '''
    This solution only works Unix system
    '''
    def handler(signum, frame):
       print ("Forever is over!")
       raise Exception("end of time")


    def loop_forever():
        while 1:
            print ('sec')
            time.sleep(1)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)
    try:
        loop_forever()
    except Exception as e:
        print (e)

    return


def use_timeout_with_process():
    from multiprocessing import Process

    def do_action(mess=str, mess2=str):
        while 1:
            print (mess)
            print (mess2)
            time.sleep(1)

    action_process = Process(target=do_action, args=('repeat','what'))

    # Start the process and block for 5s
    action_process.start()
    action_process.join(timeout=2)

    # Terminate the process
    action_process.terminate()
    print('Kill the action')

    return

def convert_timest_to_sec(timest=""):
    pt = datetime.strptime(timest, '%H:%M:%S.%f')
    sec = pt.second + pt.minute * 60 + pt.hour * 3600

    # x = time.strptime(timest.split('.')[0], '%H:%M:%S')
    # sec = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min,
    #                    seconds=x.tm_sec).total_seconds()

    #Method 2
    # time = "01:34:11"
    # sum(x * int(t) for x, t in zip([3600, 60, 1], time.split(":")))

    print (sec)
    return sec


def convert_to_time_utc(time_string):
    import pytz
    import dateutil.parser
    import datetime

    # time_string = u'11/14/2018 4:09:03 PM'
    desire = '2019-01-23T14:14:08.000+00:00'

    # format = "%m/%d/%Y %I:%M:%S %p"
    format = "%m/%d/%Y %H:%M:%S"
    strptime = datetime.strptime(time_string, format)
    print (strptime)
    return strptime.isoformat()


def datetime_format(time_string):
    format = "%m/%d/%Y %H:%M:%S"
    return time.strptime(time_string, format)


def grap_middle_value():
    def left(s, amount):
        return s[:amount]

    def right(s, amount):
        return s[-amount:]

    def mid(s, offset, amount):
        return s[offset:offset+amount]

    zc_array = [1,2,3,4, 9,10,11,12]
    zc_left = [x for x in zc_array if x<=5]
    print (zc_left)

    # zc_left = left(zc_array, 4)
    # zc_right = right (zc_array, 4)
    zc_left_max = right( zc_left, 2)
    print (zc_left)
    # print (zc_right)
    print (zc_left_max)

def test_exception():
    # timest = datetime_format(u'11/14/2018 16:09:03')
    time_arr = [u'11/14/2018 16:09:03', None,u'353415574.4', u'12/1/2018 16:09:03']
    for timest in time_arr:
        if timest is not None:
            try:
                timest = datetime_format(timest)
            except:
                print ('wrong format')
                continue

            print (timest)
            print (timest[1])

    return


def test_file_path():
    file_path = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(file_path + '/data/'):
        SESSION_CONFIG_PATH = file_path + '/data/session-config.pickle'
        print (SESSION_CONFIG_PATH)
    elif os.path.isdir('../data/'):
        SESSION_CONFIG_PATH = '../data/session-config.pickle'
        print (SESSION_CONFIG_PATH)
    else:
        print("Missing data/ directory")
        exit()

    return


def test_datetime_import():
    # from datetime import datetime
    # from time import time
    import socket

    CWD = os.getcwd()
    if True:
        st = datetime.fromtimestamp(time()).strftime('%Y%m%dT%H%M%S')
        sk = socket.gethostname()
        fn = os.path.join(CWD, "data", "{}_{}.dat".format(st, sk))

        print (fn)

def test_time_zone():


    timezones = ['America/New_York', 
                'America/Los_Angeles', 
                'Europe/Madrid', 
                'America/Puerto_Rico']

    ts = datetime.now().replace(microsecond=0)
    print ("Time ISOformat: {}".format(ts))
    # time_string = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    # print ("Time to save file: {}".format(time_string))

    bucket = {}
    bucket['timestamp'] = ts.isoformat()

    with open('data/timestamp_' + str(bucket['timestamp']) + '.json', 'w') as outfile:
        outfile.write(json.dumps(bucket))
    outfile.close()

    # Python3 only!
    # tzinfo = timezone.utc
    # ts.replace(tzinfo=tzinfo)
    # print (ts.replace(tzinfo=timezone.utc).isoformat())
    # print (ts.strftime('%Y-%m-%dT%H-%M-%S'+'Z'+str(tzinfo)))
    # print (ts.astimezone)
    # print (datetime.utcnow().replace(tzinfo=timezone.utc).isoformat())

    current_timezone = pytz.timezone("US/Eastern")
    print (datetime.now(current_timezone).replace(microsecond=0).isoformat())
    time_now = datetime.now(current_timezone).replace(microsecond=0)
    print (time_now.strftime('%Y%m%dT%H%M%S.%Z'))
    # print ()
    unaware = datetime(2011, 8, 15, 8, 15, 12, 0)
    aware = datetime(2011, 8, 15, 8, 15, 12, 0, pytz.UTC)
    now_aware = pytz.utc.localize(unaware)
    assert aware == now_aware



if __name__ == "__main__":
    # test_Enum34(1)


    id = 'cycle3-raw_echo-2-2018-08-23-17-24-43-echoes-e.dat'
    i = id.split('-')
    print (i[0].split('cycle')[1])



    test_exception()
    test_datetime_import()

    edit_element_numpy()
    grap_middle_value()
    convert_timest_to_sec('0:01:05.000')
    test_file_path()

    # JSON_to_file()

    # use_timeout_with_signal()
    # use_timeout_with_process()

    test_time_zone()
    