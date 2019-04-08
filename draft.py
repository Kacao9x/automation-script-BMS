
# Program to show the use of continue statement inside loops


from enum import Enum
import json as j
import numpy as np
import time

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
       print "Forever is over!"
       raise Exception("end of time")


    def loop_forever():
        while 1:
            print ('sec')
            time.sleep(1)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)
    try:
        loop_forever()
    except Exception, exc:
        print exc

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


if __name__ == "__main__":
    # test_Enum34(1)
    id = 'cycle3-raw_echo-2-2018-08-23-17-24-43-echoes-e.dat'
    i = id.split('-')
    print (i[0].split('cycle')[1])

    result = False
    result |= True
    print (result)

    # JSON_to_file()

    # use_timeout_with_signal()
    use_timeout_with_process()



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
    print arr

    for ele in np.nditer(arr_np, op_flags=['readwrite']):
        ele += 2
    print arr_np