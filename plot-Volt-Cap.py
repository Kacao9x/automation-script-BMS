import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import datetime as dt
import thLib as th

keyword         = 'cycle'
name            = '180911_Me02-H100'
# path            = 'Me02-H100_180814/'
path = th.ui.getdir('Pick your directory') + '/'                                # prompts user to select folder
# path            = '/media/jean/Data/titan-echo-board/Me02-H100_180911/'
cycler_path     = path + name + '.csv'
cycler_path_new = path + name + '_new.csv'
final_log_path  = path + name + '_sorted.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove
ind = []

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
def merge_column(table):
    global ind
    id_num = table.columns.get_loc("id_num")
    capmAh = table.columns.get_loc("cap(mAh)")
    vol    = table.columns.get_loc("volt")

    # for i in range(len(ind) -1 ):

        # Addition of cap for CV and CC cycle (step 1 and 2)
        # if (table.iat[int(ind[i]), id_num] == 'Rest' and
        #       table.iat[int(ind[i - 1]), id_num] == 'CCCV_Chg'):
        #
        #     tot = table.iat[int(ind[i]) - 1, capmAh]
        #     print('i: %s tot: %s' % (str(tot), str(i)))
        #     diff = int(ind[i + 1]) - int(ind[i])
        #     for j in range(diff):
        #         table.iat[int(ind[i]) + j, capmAh] = float(
        #             table.iat[int(ind[i]) + j, capmAh]/tot)

        # Subtraction the capacity for dischage cycle
        # if (table.iat[int(ind[i + 1]), id_num] == 'Rest' and
        #       table.iat[int(ind[i]), id_num] == 'CC_DChg'):
        #
        #     tot = table.iat[int(ind[i]) - 1, capmAh]
        #     tot = 55.1067
        #     print ('i: %s tot: %s' % (str(tot), str(i)) )
        #     diff = int(ind[i + 1]) - int(ind[i])
        #     for j in range(diff):
        #         table.iat[int(ind[i]) + j, capmAh] = float(
        #             table.iat[int(ind[i]) + j, capmAh] / tot)

    tot = 55.193
    diff = 3259 - 0
    for j in range(diff):
        table.iat[ j, capmAh] = float(table.iat[j,capmAh] / tot)

    tot = 55.1067
    # print('i: %s tot: %s' % (str(tot), str(i)))
    diff = 5968 - 3321
    for j in range(diff):
        table.iat[3321 + j, capmAh] = float(table.iat[3321 + j,
                                                   capmAh] / tot)
    return table



def main():
    with open(cycler_path_new) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()


    # NAN_finder = table['id'].notna()  # a boolean list of ID column
    # global ind
    # for i in range(len(NAN_finder)):
    #     if NAN_finder[i] == True:
    #         ind = np.append(ind, i)
    # print (ind)
    #
    # table = merge_column(table)  # Merge capactity of CC and CV stages
    # table.to_csv(cycler_path_new)

    vol1,vol2,amp1,amp2 = [],[],[],[]
    amp1 = [num / 55.193 for num in amp1]
    amp2 = [num / 55.1067 for num in amp2]

    for i in range (1, 3259):
        #plot CCCV
        vol1.append(table['volt'][i])
        amp1.append(table['cap(mAh)'][i])
    plt.figure(1)
    plt.scatter(amp1, vol1)
    plt.title('Capacity vs Voltage in Charge cycle')
    plt.xlabel('Cap %')
    plt.ylabel('Volt (V)')
    plt.axvspan(0.095, 0.105, color='red', alpha=0.5)
    plt.interactive(True)
    plt.show()


    for j in range (3322, 5968):
        #plot Discharge
        # plot CCCV
        vol2.append(table['volt'][j])
        amp2.append(table['cap(mAh)'][j])
    plt.figure(2)
    plt.scatter(amp2, vol2)
    plt.title('Capacity vs Voltage in Discharge cycle')
    plt.xlabel('Cap %')
    plt.ylabel('Volt (V)')
    plt.axvspan(0.895, 0.905, color='red', alpha=0.5)
    plt.interactive(False)
    plt.show()


    # find the CC-CV charge/discharge ID_num
    # ind_charge, ind_discharge = [], []
    # for num in ind:
    #     if table['id'][num] % 4 == 1:
    #         ind_charge = np.append(ind_charge, num)
    #     elif table['id'][num] % 4 == 3:
    #         ind_discharge = np.append(ind_discharge, num)
    #     else:
    #         pass
    # print (ind_discharge)
    # print (ind_charge)

    # ind = [0, 3321, 6031, 9415, 3259, 5968, 9353, 12060]
    ind_charge = [0, 6031 ]
    ind_discharge = [3321, 9415]



    return





if __name__ == '__main__':
    main()
