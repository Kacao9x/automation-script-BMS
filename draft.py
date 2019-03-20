
# Program to show the use of continue statement inside loops


from enum import Enum
import json as j
import numpy as np

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
    


if __name__ == "__main__":
    # test_Enum34(1)
    id = 'cycle3-raw_echo-2-2018-08-23-17-24-43-echoes-e.dat'
    i = id.split('-')
    print (i[0].split('cycle')[1])

    result = False

    result |= True
    print (result)

    arr = [1, 2, 3, 4]
    for id, ele in enumerate(arr):
        ele += 2
        arr[id] = ele
    # arr = [ele +2 for ele in arr]
    print arr

    JSON_to_file()
    
