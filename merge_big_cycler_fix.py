import pandas as pd
import numpy as np
import thLib as th

ind = []
keyword         = 'cycle'
name            = '180914_Me02-H100'
# path            = '/media/jean/Data/titan-echo-board/Me02-H100_180911/'
path = th.ui.getdir('Pick your directory') + '/'                                # prompts user to select folder
cycler_path     = path + name + '.csv'
cycler_path_new = path + name + '_new.csv'
final_log_path  = path + name + '_sorted.csv'
__PERIOD__  = 5                                                                 #time difference btw each log
_start_row  = 1

# This function help grasp the data instance of 5 second interval
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
    np.sort(ind)


    tb = pd.DataFrame()

    for i in range(len(ind) -1):
        # table_stage = table.iloc[ int(ind[i]), :: ].copy()                 #grasp the stage id
        table_stage = table.loc[[int(ind[i])]]  # grasp the stage id
        print (table_stage.head())
        tb = pd.concat([tb, table_stage], axis=0)
        table_data = table.iloc[ int(ind[i]) + 1 : int(ind[i + 1]) : 50 ].copy()  #grasp the data instance
        print (table_data.head().to_string())

        # tb = tb.append(table_stage, table_data, ignore_index=True)
        # tb = pd.concat([table_stage, table_data], axis=0)
        tb = pd.concat([tb, table_data], axis=0)

    tb.columns = ['extra','id','id_num', 'time', 'volt', 'current',
                    'cap(mAh)', 'Date/Time']
    tb.sort_values('id')
    del tb['extra']

    return tb


def main ():
    with open(path + name + '.txt', 'r') as my_file:
        lines = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                            error_bad_lines=False, engine='python')
        my_file.close()

    cycler_data = lines.iloc[:, 0:10]
    # cycler_data = lines.iloc[::50, 0:10]
    print (cycler_data.shape)


    header_list = ['id_num', 'time', 'volt', 'current',
                    'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                    'en(microWh)', 'Date/Time']
    cycler_data.columns = header_list
    del cycler_data['del2'], cycler_data['en(mWh)'], \
        cycler_data['en(microWh)'], cycler_data['cap(microAh)']

    #added extra 'id' columns to shift the first rows
    header_list = ['id','id_num', 'time', 'volt', 'current',
                   'cap(mAh)', 'Date/Time']
    cycler_data = cycler_data.reindex(columns = header_list)
    print (cycler_data.head())
    cycler_data.to_csv(cycler_path)

    '''
    search for rows that need to shift
    '''

    ind = []
    #for good cycler data with 5s interval
    ind = (cycler_data.index[ cycler_data['time'].str.contains('Chg') ].tolist()) \
          + (cycler_data.index[ cycler_data['time'].str.contains('Rest') ].tolist())

    print (ind)

    # transpose the dataframe for shifting rows
    cycler_data_t = cycler_data.T

    for i in ind:
        cycler_data_t[i] = cycler_data_t.iloc[:,i].shift(-1).tolist()

    cycler_data = cycler_data_t.T
    cycler_data.to_csv(cycler_path)
    print (cycler_data.head())

    #------------------------------------------------------------------------------#
    # with open(cycler_path) as outfile:
    #     cycler_data = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    # outfile.close()
    # print(cycler_data.head().to_string())


    # cycler_data = merge_column(cycler_data)
    # cycler_data.to_csv(final_log_path)

    return

if __name__ == '__main__':
    main()