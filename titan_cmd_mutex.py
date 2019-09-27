import numpy as np
import argparse, socket
import json
from time import time, sleep, clock
from datetime import datetime
import sys

import threading
import logging
from ilock import *

''' Traditional mutex: mutiple access to the same resource between a group 
    of thread in the same processs'''
# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-10s) %(message)s',)
#
# def worker_with(lock):
#     with lock:
#         logging.debug('Lock acquired via with')
#
# def worker_not_with(lock):
#     lock.acquire()
#     try:
#         logging.debug('Lock acquired directly')
#     finally:
#         lock.release()
#
#     return
#
# if __name__ == '__main__':
#     lock = threading.Lock()
#     w   = threading.Thread(target=worker_with, args=(lock, ))
#     nw  = threading.Thread(target=worker_not_with, args=(lock, ))
#
#     w.start()
#     nw.start()

# #!/usr/bin/python3

# import sys, fcntl, time

# with open("test.lock", "w+") as lock:
# fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
# # begin critical
# sys.stdout.write("hello\n")
# time.sleep(3)
# sys.stdout.write("world\n")
# # end critical


'''
Explain: https://stackoverflow.com/questions/19752168/python-ensure-script-is-activated-only-once
'''
# import fcntl
# import traceback

# class ProcessLock:

#     def __init__(self, path_to_file, block):
#         self.file_path = path_to_file
#         try:
#             options = fcntl.LOCK_EX
#             if not block:
#                 options = options | fcntl.LOCK_NB

#             self.file = open(path_to_file, 'w+')
#             self.lock = fcntl.flock(file, options)
#         except:
#             print 'caught something: {}'.format(traceback.format_exc())
#             self.file = None
#             self.lock = None

#     def is_locked(self):
#         return self.lock is not None

#     def unlock(self):
#         self.lock = None
#         self.file = None

# def aquire_lock(lock_name):
#     path = '/tmp/{}.lock'.format(lock_name)
#     return ProcessLock(path, False)

# def aquire_lock_blocking(lock_name):
#     path = '/tmp/{}.lock'.format(lock_name)
#     return ProcessLock(path, True)
def print_delay(x=int):

    for i in range(5):
    	start_time 	= time()
    	end_time	= start_time + 10 - x
        print "HAPPY >> {} <<\r".format(i)
        sys.stdout.flush()

        with lock:
            print ('LOCKED... {}s-{} time'.format(x, i))
            with open('data/log.txt', 'ab') as write_out:
            	write_out.write('{}: loop {}\n'.format(__ID__, i))
            write_out.close()

            sleep(x)

        print ('RELEASED. sleep 2s')
        if time() < end_time:
        	sl = end_time - time()
        	print ('sleep time: {}'.format(round(sl,2)))
        	sleep(sl)



def ParseHelpers():
    global parser, args

    parser = argparse.ArgumentParser(description='CMD tool for auto testing')

    # ======================= Start CMD ====================================#
    parser.add_argument('--minute', default=5, type=float,
                        dest='minute', metavar='[1,59]',
                        help='minutes to sleep')
    parser.add_argument('-b', '--batt', action='store', type=str,
                        dest='batteryID', help='battery ID')

    args = parser.parse_args()

ParseHelpers()
lock = ILock('data/kacao.lock', reentrant=False)

__MINUTE__  = args.minute
__ID__		= args.batteryID

if __name__ == '__main__':
    print_delay(__MINUTE__)