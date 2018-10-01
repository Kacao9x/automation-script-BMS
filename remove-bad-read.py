import subprocess

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

def main():
    with open(address + 'bad.txt', 'rb') as readout:
        for cnt, line in enumerate( readout ):
            print (str(cnt))
            Call( address + 'line' )
    readout.close()
    return


#==============================================================================#
# address = th.ui.getdir('Pick your directory')  + '/'                            # prompts user to select folder
address = '/media/jean/Data/titan-echo-board/180924-TC02-H75/data/primary/'
bad_data = []

if __name__ == '__main__':
    main()