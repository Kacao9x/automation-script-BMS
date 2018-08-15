import pandas as pd
import numpy as np

ind = []

keyword         = 'cycle'
path            = 'Me02-H100_180814/'
cycler_path     = path + 'Cycler_Data_Merc_180814.csv'
cycler_path_new = path + 'Cycler_Data_Merc_180814_new.csv'
final_log_path  = path + 'raw_sorted_logs.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1


def merge_column(table):
    """
    merge the table with a time step of 0.1s
    :param table:
    :return:
    """
    # table: Dataframe with a custom header

    NAN_finder = table['id'].notna()                                            # result is in a boolean list

    global ind
    for i in range(len(NAN_finder)):
        if NAN_finder[i] == True:
            ind = np.append(ind, i)
    print (ind)

    # for i in range(2, int(ind[1])):
    #     table['cap(mAh)'][i] = 21 + table['cap(mAh)'][i]

    table_temp = table.copy()
    del table
    tb = pd.DataFrame()
    # table = table.iloc[1::50, ::]

    for i in range(len(ind) -1):
        table_stage = table_temp.iloc[ : int(ind[i]) ].copy()                            #grasp the stage id
        table_data = table_temp.iloc[ int(ind[i]) + 1 : int(ind[i + 1]) : 50 ].copy()  #grasp the data instance
        print table_data.head().to_string()

        # tb = tb.append(table_stage, table_data, ignore_index=True)
        tb = pd.concat([table_stage, table_data], axis=0)
    # for idx in ind:
    #     table_new = table_temp.iloc[ int(idx)]
    #     print '\n'
    #     table = table.append(table_new, ignore_index=True)
    #     # table = pd.concat([table , table_new], axis=0)

    tb.columns = ['extra','id','id_num', 'time', 'current',
                    'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
    # table['extra'].astype(int)
    tb.sort_values('extra')
    del tb['extra']
    print tb.head().to_string()

    #
    # pd.concat([pd.DataFrame([[0, 0, 0]], columns=df.columns), df]).reset_index(drop=True)
    #
    # pd.DataFrame([[0, 0, 0]], columns=df.columns).append(df, ignore_index=True)
    # print table_new.head().to_string()


    # tb.to_csv(final_log_path)
    return tb

                                                              #number of header to be remove



with open(path + 'Me02-H100_180814.txt', 'r') as my_file:
    lines = pd.read_csv(my_file, header=3, sep=r'\s\s+', error_bad_lines=False, engine='python')
    my_file.close()

# cycler_data = lines.iloc[::10, 0:10]
cycler_data = lines.iloc[:, 0:10]
print (cycler_data.shape)


header_list = ['id_num', 'time', 'del', 'current',
                     'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
cycler_data.columns = header_list
del cycler_data['del'], cycler_data['del2'], \
    cycler_data['en(mWh)'], cycler_data['en(microWh)']

#added extra 'id' columns to shift the first rows
header_list = ['id','id_num', 'time', 'current',
               'cap(mAh)', 'cap(microAh)', 'Date/Time']
cycler_data = cycler_data.reindex(columns = header_list)
cycler_data.to_csv(cycler_path)

'''
search for rows that need to shift
'''

ind = []
ind = (cycler_data.index[ cycler_data['time'].str.contains('Chg') ].tolist()) \
      + (cycler_data.index[ cycler_data['time'].str.contains('Rest') ].tolist())
ind.sort()
print ind

# cycler_data.drop(index=10480)
#
# # index = [0, 164141, 368782, 609427, 161139, 365779,606425, 811031]
# # int = index.sort()

# transpose the dataframe for shifting rows
cycler_data_t = cycler_data.T

for i in ind:
    cycler_data_t[i] = cycler_data_t.iloc[:,i].shift(-1).tolist()

cycler_data = cycler_data_t.T
cycler_data.to_csv(cycler_path)

#------------------------------------------------------------------------------#
with open(cycler_path) as outfile:
    cycler_data = pd.read_csv(outfile, sep=',', error_bad_lines=False)
outfile.close()
print(cycler_data.head().to_string())



# cycler_data = merge_column(cycler_data)
# cycler_data.to_csv(final_log_path)