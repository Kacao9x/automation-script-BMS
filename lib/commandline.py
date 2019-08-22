import subprocess
import re, os, glob

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

# display the file with keyword in ascending using BASH
def display_list_of_file(path, key):
    file_name = []
    list_cmd = ('ls '+ path +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip())

    print ('len filelist {}'.format(len(file_name)))
    return file_name


# display the file with keyword in ascending using BASH
def display_list_of_file_by_date(path, key):
    file_name = []
    list_cmd = "ls {} -1tr | grep '{}'".format(path, key)
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip())

    print ('len filelist {}'.format(len(file_name)))
    return file_name


def sort_folder_by_name(path, key):
    ''' sort by siginificant number'''

    myimages = []  # list of image filenames

    dirFiles = os.listdir(path)  # list of directory files
    dirFiles.sort()  # good initial sort but doesnt sort numerically very well
    sorted(dirFiles)  # sort numerically in ascending order

    for files in dirFiles:  # filter out all non jpgs
        if key in files:
            myimages.append(files)

    print (len(myimages))
    return myimages


def sort_folder_by_name_universal(path, key):

    def tryint(s):
        try:
            return int(s)
        except:
            return s

    def alphanum_key(s):
        return [ tryint(c) for c in re.split('([0-9]+)', s) ]




    # dirFiles = (os.listdir(path))  # list of directory files
    dirFiles = [os.path.basename(x) for x in
                glob.glob(os.path.join(path, key))]
    print ('beforeSorted {}'.format(dirFiles))
    dirFiles.sort( key=alphanum_key )
    print ('dirFiles {}, len {}'.format(dirFiles, len(dirFiles)))
    return dirFiles