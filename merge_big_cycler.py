import os
import glob
import pandas as pd
import numpy as np

ind = []
# Merge the capacity between stage 1,2 and 4
# only works with the cycler data logs
def merge_column(table):
    # table: Dataframe with a custom header

    NAN_finder = table['id'].notna()                                            # result is in a boolean list

    global ind
    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)
    print (ind)

    print type(table.iat[1,4])
    print table.iat[2,4]

    for i in range(161139):
        table.iat[i, 4] = int(table.iat[i, 4]) + 21000

    # for i in range(len(ind)):
    #     if (table.iat[int(ind[i]), 1] == 'CV_Chg' and
    #         table.iat[int(ind[i - 1]), 1]) == 'CC_Chg':
    #
    #         tot = table.iat[int(ind[i]) - 1, 4]                                 # store the capacity
    #         diff = int(ind[i + 1]) - int(ind[i])
    #
    #         for j in range(diff):
    #             table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot
    #
    #     elif i == len(ind) - 1:
    #
    #         tot = table.iat[int(len(NAN_finder) - 1), 4]
    #         diff = int(len(NAN_finder)) - int(ind[i])
    #         for j in range(diff):
    #             table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]
    #
    #     elif (table.iat[int(ind[i]), 1] == 'Rest' and
    #           table.iat[int(ind[i - 1]), 1] == 'CV_Chg'):
    #
    #         tot = table.iat[int(ind[i]) - 1, 4]
    #         diff = int(ind[i + 1]) - int(ind[i])
    #         for j in range(diff):
    #             table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot
    #
    #     elif (table.iat[int(ind[i + 1]), 1] == 'Rest' and
    #           table.iat[int(ind[i]), 1] == 'CC_DChg'):
    #
    #         tot = table.iat[int(ind[i + 1]) - 1, 4]
    #         diff = int(ind[i + 1]) - int(ind[i])
    #         for j in range(diff):
    #             table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

    # table.to_csv(cycler_path)
    return table

keyword         = 'cycle'
path            = r'Me01-H100_180730/'
cycler_path     = path + 'Cycler_Data_Merc_180730.csv'
final_log_path  = path + 'test_log_sorted.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove


cycler_data = pd.DataFrame()
with open(path + 'Me01-H100_180730.txt', 'r') as my_file:
    lines = pd.read_csv(my_file, header=3, sep=r'\s\s+', error_bad_lines=False, engine='python')
    my_file.close()

# print(table.head().to_string())
# cycler_data = lines.iloc[::10, 0:10]
cycler_data = lines.iloc[:, 0:10]
print (cycler_data.shape)


header_list = ['id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
cycler_data.columns = header_list

#added extra 'id' columns to shift the first rows
header_list = ['id','id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
cycler_data = cycler_data.reindex(columns = header_list)
del cycler_data['del'], cycler_data['del2']


'''
search for rows that need to shift
'''

# print (cycler_data[ cycler_data['time'].str.contains('CC') ])
# print (cycler_data[ cycler_data['time'].str.contains('Rest') ])
index = [0, 164141, 368782, 609427, 161139, 365779,606425, 811031]
int = index.sort()

# transpose the dataframe for shifting rows
cycler_data_t = cycler_data.T

for i in index:
    cycler_data_t[i] = cycler_data_t.iloc[:,i].shift(-1).tolist()

cycler_data = cycler_data_t.T
print (cycler_data.head().to_string())

cycler_data = merge_column(cycler_data)
print (cycler_data.head().to_string())

# cycler_data.to_csv(r"data/Merc-temp.csv")

# row_zeros = cycler_data['cap(mAh)'] == 0.0220
# print row_zeros
#
# #find the index of stage 4
# for i in range(len(cycler_data.index) - 1):
#     if cycler_data.iat[i, 4] == 0 and cycler_data.iat[i+1, 4] > 0:
#         print 'rows: %s' % str(i+1)
#         row_stage_4 = i+1
#
# for i in range(row_stage_4, len(cycler_data.index)):
#     cycler_data.iat[ i, 4 ] = - cycler_data.iat[ i, 4 ] + \
#                               cycler_data.iat[ len(cycler_data.index)-1, 4 ]
#
#
# # print(cycler_data.to_string())
# cycler_data.to_csv(final_log_path)