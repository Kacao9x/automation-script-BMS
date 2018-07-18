import os
import glob
import pandas as pd
import numpy as np


# Merge the capacity between stage 1,2 and 4
# only works with the cycler data logs
def merge_column(table):
    # table: Dataframe with a custom header

    NAN_finder = table['id'].notna()                                            # result is in a boolean list
    ind = []
    print table

    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)

    for i in range(len(ind)):
        if (table.iat[int(ind[i]), 1] == 'CV_Chg' and
            table.iat[int(ind[i - 1]), 1]) == 'CC_Chg':

            tot = table.iat[int(ind[i]) - 1, 4]                                 # store the capacity
            diff = int(ind[i + 1]) - int(ind[i])

            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

        elif i == len(ind) - 1:

            tot = table.iat[int(len(NAN_finder) - 1), 4]
            diff = int(len(NAN_finder)) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

        elif (table.iat[int(ind[i]), 1] == 'Rest' and
              table.iat[int(ind[i - 1]), 1] == 'CV_Chg'):

            tot = table.iat[int(ind[i]) - 1, 4]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

        elif (table.iat[int(ind[i + 1]), 1] == 'Rest' and
              table.iat[int(ind[i]), 1] == 'CC_DChg'):

            tot = table.iat[int(ind[i + 1]) - 1, 4]
            diff = int(ind[i + 1]) - int(ind[i])
            for j in range(diff):
                table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

    table.to_csv(cycler_path)
    return

keyword         = 'cycle'
path            = 'data/Filtered/'
cycler_path     = path + 'Cycler_Data_Apple_180717.csv'
final_log_path  = path + 'test_log_sorted.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1                                                                 #number of header to be remove

value = 0.0022


path = r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data/"
cycler_data = pd.DataFrame()

for filename in glob.glob(os.path.join(path, "*.txt")):
    my_file = open(filename)
    lines = pd.read_csv(my_file, header=3, sep=r'\s\s+', error_bad_lines=False, engine='python')
# print(lines.head().to_string())
cycler_data = lines.iloc[::10, 0:10]

# cycler_data.to_csv(r"data/Nis-ModH80-1.csv")

header_list = ['id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
cycler_data.columns = header_list


header_list = ['id','id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
cycler_data = cycler_data.reindex(columns = header_list)
# print(cycler_data.to_string())

# transpose the dataframe for shifting rows
cycler_data_t = cycler_data.T

cycler_data_t[0] = cycler_data_t.iloc[:,0].shift(-1).tolist()

cycler_data = cycler_data_t.T
del cycler_data['del'], cycler_data['del2']
# cycler_data.to_csv(r"data/Nis-temp.csv")

row_zeros = cycler_data['cap(mAh)'] == 0.0220
print row_zeros

#find the index of stage 4
for i in range(len(cycler_data.index) - 1):
    if cycler_data.iat[i, 4] == 0 and cycler_data.iat[i+1, 4] > 0:
        print 'rows: %s' % str(i+1)
        row_stage_4 = i+1

for i in range(row_stage_4, len(cycler_data.index)):
    cycler_data.iat[ i, 4 ] = - cycler_data.iat[ i, 4 ] + \
                              cycler_data.iat[ len(cycler_data.index)-1, 4 ]


# print(cycler_data.to_string())
cycler_data.to_csv(r"data/Nis-temp.csv")