
# Program to show the use of continue statement inside loops


from enum import Enum
import json as j
import numpy as np
import os
import json
from datetime import datetime, timedelta, tzinfo
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

def test_wrong_datetime_exception():
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
    bucket['timestamp'] = datetime.now()#.replace(microsecond=0).isoformat()
    cycleID = 2
    st = 'cycle{}_echo_{}.json'.format(cycleID+1, bucket['timestamp'].isoformat())
    print ('st {}'.format(st))


    # with open('data/timestamp_' + str(bucket['timestamp']) + '.json', 'w') as outfile:
    #     outfile.write(json.dumps(bucket))
    # outfile.close()

    # Python3 only!
    # tzinfo = timezone.utc
    # ts.replace(tzinfo=tzinfo)
    # print (ts.replace(tzinfo=timezone.utc).isoformat())
    # print (ts.strftime('%Y-%m-%dT%H-%M-%S'+'Z'+str(tzinfo)))
    # print (ts.astimezone)
    # print (datetime.utcnow().replace(tzinfo=timezone.utc).isoformat())

    current_timezone = pytz.timezone("US/Eastern")
    print ('timezone: {}'.format(datetime.now(current_timezone).replace(microsecond=0).isoformat()))

    time_now = datetime.now(current_timezone)#.replace(microsecond=0)
    bucket['timestamp'] = time_now
    print ('time now: {}'.format(bucket['timestamp'].strftime('%Y%m%dT%H%M%S.%Z')))
    # print ()

    # unaware = datetime(2011, 8, 15, 8, 15, 12, 0)
    # aware = datetime(2011, 8, 15, 8, 15, 12, 0, pytz.timezone("US/Eastern"))
    # now_aware = pytz.utc.localize(unaware)
    # assert aware == now_aware


def avg_arr_of_arr():
    list_1 = [None, [1,3,4,7], None, [3,7,6,3], None, [4,5,6,3]]

    list_1 = [i for i in list_1 if i != None]
    # list_1 = filter(lambda x: x != None, list_1)
    avg = np.mean(list_1 ,axis=0)
    print(avg)


    I = [0, 2]
    list_1_np = np.array(list_1)
    # np.delete(a, 1, 0)
    list_2 = np.delete(list_1_np, I, axis = 0).tolist()
    print ('remove element from array: {}'.format(list_2))
    print (np.array(list_1))

    echoes_data = {'raw_data': [4,5,6,3],'capture_number':220}

    mess = 'detect failed' if 'temperature' in echoes_data else 'correct'
    print (mess)
    print ('\n')


def join_list():
    # res = echoes_db.update(record ={"$unset": {"raw_data.0": 1, "raw_data.2": 1}},
    #                  match  ={"_id": oneCapture['_id']},
    #                  collection='TC28constant3A')
    dup = [0,3,6,4]
    # record = {'raw_data.'.join(str(dup))}
    # print('record {}'.format(record))

    unset = ''
    for idx in dup:
        unset += "'raw_data.{}':1, ".format(idx)

    print (unset)
    print ('\n')
    return


def test_bypass_function():
    outside_count = 0
    error = 0
    time_arr = ['11/14/2018 18:09:03', u'11/14/2018 16:09:03', None, u'353415574.4', u'12/1/2018 16:09:03']

    for timest in time_arr:
        if timest is not None:
            try:
                convert = datetime_format(timest)
                print (convert)
            except:
                print ('wrong format')
                error += 1

            # print (convert)
            print ('timest: {}'.format(timest))
            outside_count += 1

    print('outside {}, error {}\n\n'.format(outside_count, error))

    return

def create_folder_w_timestamp():
    bucket = {}
    bucket['timestamp'] = datetime.now().replace(microsecond=0)
    st = 'xxx_{}.dat'.format(bucket['timestamp'].isoformat())

    with open("data/" + st, 'w') as writeout:
        writeout.write("testing")
    writeout.close()

    print("finish creating filename")
    return

def sort_folder_by_name():
    ''' sort by siginificant number'''
    import os

    myimages = []  # list of image filenames

    dirFiles = os.listdir('/media/kacao/Ultra-Fit/titan-echo-boards/Lenovo/transducer-testing-0723/primary/')  # list of directory files
    dirFiles.sort()  # good initial sort but doesnt sort numerically very well
    sorted(dirFiles)  # sort numerically in ascending order

    for files in dirFiles:  # filter out all non jpgs
        if '.json' in files:
            myimages.append(files)

    print len(myimages)
    print myimages

def sort_folder_by_name_advance():
    myimages = []  # list of image filenames
    dirFiles = os.listdir('/media/kacao/Ultra-Fit/titan-echo-boards/Lenovo/transducer-testing-0723/primary/')  # list of directory files
    dirFiles.sort(key=lambda f: int(filter( str.split('-')[1].isdigit(), f )))  # good initial sort but doesnt sort numerically very well
    sorted(dirFiles)  # sort numerically in ascending order

    for files in dirFiles:  # filter out all non jpgs
        if '.json' in files:
            myimages.append(files)

if __name__ == "__main__":
    # test_Enum34(1)
    # avg_arr_of_arr()
    # join_list()
    # test_bypass_function()
    # create_folder_w_timestamp()
    # sort_folder_by_name_advance()


    ind = [3,5,6,8]
    print ('list: {}'.format( ind[len(ind) -1] ))

    test_time_zone()

    time_readout = "2019-06-04-13-46-57"
    time_converted = datetime.strptime(time_readout, '%Y-%m-%d-%H-%M-%S').strftime('%Y-%m-%d %H:%M:%S')
    print (time_converted)




    test_wrong_datetime_exception()
    test_datetime_import()

    edit_element_numpy()
    grap_middle_value()
    convert_timest_to_sec('0:01:05.000')
    test_file_path()

    # JSON_to_file()

    # use_timeout_with_signal()
    # use_timeout_with_process()

    