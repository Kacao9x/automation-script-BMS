import pandas as pd
import numpy as np
import datetime, sys
from pprint import pprint

import unittest





class preprocessing(object):

    period      = 5 #time differnce between each capture
    start_row   = 1 #number of header to remove
    ind         = []

    _debug_level = None
    _class       = None
    _debug       = None

    def __init__(self, filename=None, neware = True, time_sync_fix = False,
                 debug = False):
        '''

        :param filename: Path to the data set
        :param neware: True if sorting the Neware data report
        :param time_sync_fix: True if the report captured data very 0.1s
        :param start_row: number of header to remove
        :param period: time difference between each capture
        :param debug:
        '''
        self._debug = debug
        self._class = self.__class__.__name__

        self._neware_   = neware
        self._time_fix  = time_sync_fix


        if not filename:
            self.dprint('No data set specified', error = True)
            exit()
        else:
            self._filename = filename
        self.dprint('Initializing data cleaning algo')


    def close(self):
        return True


    def clean_test_data(self):
        with open(self._filename + '.txt', 'r') as my_file:
            if self._neware_:
                lines = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                                    error_bad_lines=False, engine='python')
            else:
                lines = pd.read_csv(my_file, header=3, sep=r'\t',
                                    error_bad_lines=False, engine='python')
            my_file.close()


        cycler_data = lines.iloc[:, 0:10]
        print (cycler_data.shape)
        header_list = ['id_num', 'time', 'volt', 'current', 'del2', 'cap(Ah)',
                       'cap(microAh)', 'en(Wh)','en(microWh)', 'Date/Time']
        cycler_data.columns = header_list
        del cycler_data['del2'], cycler_data['en(microWh)'], \
            cycler_data['cap(microAh)']

        # added extra 'id' columns to shift the first rows
        header_list = ['id', 'id_num', 'time', 'volt', 'current',
                       'cap(Ah)', 'en(Wh)', 'Date/Time']
        cycler_data = cycler_data.reindex(columns=header_list)

        '''
                Magic stuff to search for rows that need to shift
        '''
        self._ind = []
        # for good cycler data with 5s interval
        ind = (cycler_data.index[
                   cycler_data['time'].str.contains('Chg')].tolist()) \
              + (cycler_data.index[
                     cycler_data['time'].str.contains('Rest')].tolist())

        print (ind)

        # transpose the dataframe for shifting rows
        cycler_data_t = cycler_data.T

        for i in ind:
            cycler_data_t[i] = cycler_data_t.iloc[:, i].shift(-1).tolist()

        cycler_data = cycler_data_t.T

        ''' filter data of 5 sec interval '''
        if self._time_fix:
            cycler_data = self._filter_data_by_timeInterval(cycler_data,
                                                            self.period)

        cycler_data.to_csv(self._filename + '.csv')     #cycler path

        return cycler_data


    def merge_column(self, table):

        print (table.shape)

        NAN_finder = table['id'].notna()                                        # a boolean list of ID columns
        # global ind

        ind = []
        for i in range(len(NAN_finder)):
            if NAN_finder[i] == True:
                ind = np.append(ind, i)

        print (ind)
        id_num      = table.columns.get_loc("id_num")
        cap_Ah      = table.columns.get_loc("cap(Ah)")
        energy_Wh   = table.columns.get_loc("en(Wh)")

        # add 21.00 for real capacity
        # for i in range(0, int(ind[1])):
        #     table.iat[i, cap_mAh] = 38 + table.iat[i, cap_mAh]

        for i in range(len(ind) - 1):

            # Adding capacity - CC charge --> CV charge
            if (table.iat[int(ind[i]), id_num] == 'CV_Chg' and
                table.iat[int(ind[i - 1]), id_num]) == 'CC_Chg':

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]                    # store the capacity
                diff    = int(ind[i + 1]) - int(ind[i])                         # find the length of the stage

                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah] += tot_cap

            # Adding capacity - CV charge --> CC charge
            elif (table.iat[int(ind[i]), id_num] == 'CC_Chg' and
                  table.iat[int(ind[i - 1]), id_num] == 'CV_Chg'):

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]
                diff    = int(ind[i + 1]) - int(ind[i])
                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah] += tot_cap


            # Keep the same capacity of CV_charge for rest cycle
            elif ((table.iat[int(ind[i]), id_num] == 'Rest' and
                  table.iat[int(ind[i - 1]), id_num] == 'CC_Chg' and
                  table.iat[int(ind[i + 1]), id_num] == 'CC_DChg')) or \
                ((table.iat[int(ind[i]), id_num] == 'Rest' and
                  table.iat[int(ind[i - 1]), id_num] == 'CV_Chg' and
                  table.iat[int(ind[i + 1]), id_num] == 'CC_DChg')):

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]
                diff    = int(ind[i + 1]) - int(ind[i])
                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah] += tot_cap


            # Keep the last capacity/power of CCCV_charge for rest cycle
            elif (table.iat[int(ind[i]), id_num] == 'Rest' and
                  table.iat[int(ind[i - 1]), id_num] == 'CCCV_Chg'):

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]
                tot_wh  = table.iat[int(ind[i]) - 1, energy_Wh]
                diff    = int(ind[i + 1]) - int(ind[i])
                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah]      += tot_cap
                    table.iat[int(ind[i]) + j, energy_Wh]   += tot_wh


            # Subtraction the capacity for dischage cycle
            elif (table.iat[int(ind[i + 1]), id_num] == 'Rest' and
                  table.iat[int(ind[i]), id_num] == 'CC_DChg'):

                tot_cap = table.iat[int(ind[i + 1]) - 1, cap_Ah]
                tot_wh  = table.iat[int(ind[i + 1]) - 1, energy_Wh]
                diff    = int(ind[i + 1]) - int(ind[i])
                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah] = tot_cap -\
                                                         table.iat[int(ind[i]) + j, cap_Ah]
                    table.iat[int(ind[i]) + j, energy_Wh] = tot_wh - \
                                                        float(table.iat[int(ind[i]) + j, energy_Wh])


        return table


    def calculate_SoH(self, table, rated_cap=None):
        SoH_value = 100

        ind = table[table['id'].notna()].index.tolist()                        # a list of ID rows
        print (ind)

        # id_num      = table.columns.get_loc("id_num")
        # cap_Ah      = table.columns.get_loc("cap(Ah)")
        # energy_Wh   = table.columns.get_loc("en(Wh)")

        # actual_cap_Ah_arr = []
        # for i in range(len(ind)):
        #     if table.iat[ind[i], id_num] == 'Rest' and \
        #         table.iat[ind[i-1], id_num] == 'CV_Chg':
        #
        #         actual_cap_Ah_arr.append(table.iat[ind[i-1], cap_Ah])
        #
        #
        # print(actual_cap_Ah_arr)
        # max_cap_Ah = max(actual_cap_Ah_arr)
        # print ('max capacity: ' + str(max_cap_Ah))

        max_cap_Ah = table['cap(Ah)'].max()
        print ('max capacity: ' + str(max_cap_Ah))

        if rated_cap is None:
            pass
        else:
            SoH_value *= max_cap_Ah/rated_cap


        return SoH_value


    def calculate_SoC(self, table, actual_capacity=None):

        table['SoC'] = 100*table['cap(Ah)']/actual_capacity
        table['SoH'] = 100*actual_capacity/18650
        return table



    def _filter_data_by_timeInterval(self, table, sec):
        '''
        Merge the table with a time step of 0.1s
        :param sec: time step (second)
        :return: new table with time step of 5 sec
        '''

        NAN_finder = table['id'].notna()  # result is in a boolean list

        global ind
        for i in range(len(NAN_finder)):
            if NAN_finder[i] == True:
                ind = np.append(ind, i)
        print (ind)
        np.sort(ind)

        tb = pd.DataFrame()

        for i in range(len(ind) - 1):
            table_stage = table.loc[[int(ind[i])]]  # grasp the stage id
            print (table_stage.head())

            tb = pd.concat([tb, table_stage], axis=0)
            table_data = table.iloc[int(ind[i]) + 1: int(
                ind[i + 1]): sec * 10].copy()  # grasp the data instance
            print (table_data.head().to_string())

            tb = pd.concat([tb, table_data], axis=0)

        tb.columns = ['id', 'id_num', 'time', 'volt', 'current',
                      'cap(Ah)', 'Date/Time']
        tb.sort_values('id')
        # del tb['extra']

        return tb




    def get_timestamp_from_filename(self, filename):

        i = filename.split('-')

        if i[1] == 'temp':
            endtime = i[2] + '-' + i[3] + '-' + i[4] + ' ' \
                      + i[5] + ':' + i[6] + ':' + i[7]
            print ('endtime raw: ' + endtime)

        else:
            endtime = i[3] + '-' + i[4] + '-' + i[5] + ' ' \
                      + i[6] + ':' + i[7] + ':' + i[8]
            print ('endtime filtered: ' + endtime)

        return endtime


    def read_time(self, table):
        start_time = table['Date/Time'][self.start_row]
        return start_time


    # Prints messages with function and class
    def dprint(self, txt, timestamp=False, error=False, level=1):

        if level <= self._debug_level:
            if self._debug or error:
                function_name = sys._getframe(1).f_code.co_name
                if timestamp:
                    print("  " + str(
                        datetime.datetime.now()) + " " + self._class + ":" + function_name + "(): " + txt)
                else:
                    print(
                                "  " + self._class + ":" + function_name + "(): " + txt)








class Test(unittest.TestCase):
    cycler_sort = preprocessing(
        filename='/media/kacao/Ultra-Fit/titan-echo-boards/18650/tempC/18650_190320',
        neware=False,
        time_sync_fix=False, debug=False)


    def test_clean_data(self, cycler_sort=cycler_sort):

        cycler_sort.clean_test_data()
        return


    def test_merge_column(self, cycler_sort=cycler_sort):

        table = cycler_sort.clean_test_data()
        print (table.head().to_string())

        cycler_sort.merge_column(table)                                         # Merge capactity of CC and CV stages
        # table.to_csv('/media/kacao/Ultra-Fit/titan-echo-boards/18650/tempC/18650_190320_merged.csv')
        return table


    def test_calculate_SOHSOC(self,cycler_sort=cycler_sort):
        table = Test.test_merge_column(self, cycler_sort=cycler_sort)

        SoH_value = cycler_sort.calculate_SoH(table, rated_cap=18650)
        print('SOH: {0:.2f}'.format(SoH_value) )

        table = cycler_sort.calculate_SoC(table, SoH_value*18650/100)

        print (table.head().to_string())
        table.to_csv('/media/kacao/Ultra-Fit/titan-echo-boards/18650/tempC/18650_190320_merged_soc.csv')
        return



    def test_something(self):

        return




if __name__ == 'main':
    unittest.main()