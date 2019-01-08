import os, subprocess, sys, datetime, time
#==============================================================================#

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
#==============================================================================#
print(os.path.isdir("data/secondary"))
print(os.path.exists("data/third/"))
ts = time.time()
ts_print = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
print (ts_print)
# print ( len(os.listdir('data/third')) == 0 )
try:
    if os.path.exists("data/third"):

        os.rename('data/third', 'data/third-' + ts_print)
        print ('rename')

    os.makedirs(os.getcwd() + '/data/third/')
    print ('create folder')

except OSError:  # Do nothing on error
    sys.exit("Problem with creating data folder")

