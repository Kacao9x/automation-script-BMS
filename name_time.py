import time


def __get_filename():
    name =  "file" + str(time.strftime("%Y%m%d_%H%M%S")) + ".txt"
    return name
    #time.clock() is an object, not string

__get_filename()

def __write_test_logs(name= '', delay=int, gain=str, sample_rate=int):
    try:
        with open(name, 'ab') as writeout:
            writeout.writelines('the delay us is: ' + str(delay))
            writeout.writelines('the VGA gain is: ' + gain)
            writeout.writelines('the sampling rate is: ' + str(sample_rate))

    finally:
        writeout.close()
    return

__NAME__ = __get_filename()
print __NAME__
__write_test_logs(__NAME__, 10, '0.5', 22000)
