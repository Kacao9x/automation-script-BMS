import sys

import re
import subprocess

# device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
# df = subprocess.check_output("lsusb")
# # print (df.decode().split('\n'))
# devices = []
#
# for count, i in enumerate(df.decode().split('\n')):
#     if i:
#         info = device_re.match(i)
#         if info:
#             dinfo = info.groupdict()
#             dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
#             devices.append(dinfo)
#             print (count, dinfo)
# print (devices)
#
# '''
# 0 {'id': '090c:1000', 'tag': 'Silicon Motion, Inc. - Taiwan (formerly Feiya Technology Corp.) Flash Drive', 'device': '/dev/bus/usb/002/006'}
# 1 {'id': '0424:5742', 'tag': 'Standard Microsystems Corp. ', 'device': '/dev/bus/usb/002/002'}
# 2 {'id': '1d6b:0003', 'tag': 'Linux Foundation 3.0 root hub', 'device': '/dev/bus/usb/002/001'}
# 3 {'id': '0c45:670c', 'tag': 'Microdia ', 'device': '/dev/bus/usb/001/009'}
# 4 {'id': '04f3:2313', 'tag': 'Elan Microelectronics Corp. ', 'device': '/dev/bus/usb/001/007'}
# 5 {'id': '0cf3:e301', 'tag': 'Atheros Communications, Inc. ', 'device': '/dev/bus/usb/001/005'}
# 6 {'id': '2010:7638', 'tag': ' ', 'device': '/dev/bus/usb/001/045'}
# 7 {'id': '138a:0091', 'tag': 'Validity Sensors, Inc. ', 'device': '/dev/bus/usb/001/004'}
# 8 {'id': '0424:2742', 'tag': 'Standard Microsystems Corp. ', 'device': '/dev/bus/usb/001/002'}
# 9 {'id': '1d6b:0002', 'tag': 'Linux Foundation 2.0 root hub', 'device': '/dev/bus/usb/001/001'}
# '''

while (1):
    try:
        f = open('/dev/hidraw2')
        print (f.read(100))
    except (PermissionError):
        print ('No scanner found')
        sys.exit(0)
    except (KeyboardInterrupt, SystemError):
        print ('Interrupted')
        sys.exit(0)
