#!/usr/bin/python3

from enum import Enum
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from lib.echoes_database import *
from dateutil.parser import parse

import unittest
import pprint

from lib.commandline import *


class cycler_preprocessing(object):

    __PERIOD__      = 5                                                         #number of seconds btw logs to be saved
    start_row   = 1                                                             #number of header to remove
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

        self._neware    = neware
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
        with open(str(self._filename) + '.txt', 'r', encoding='latin-1') as my_file:
            chunksize = 100000
            if self._neware:
                # lines = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                #                     error_bad_lines=False, engine='python')
                tfr = pd.read_csv(my_file, header=3, sep=r'\s\s+',
                                  error_bad_lines=False, engine='python',
                                  chunksize=chunksize, iterator=True)
                lines = pd.concat(tfr, ignore_index=True)
            else:
                lines = pd.read_csv(my_file, header=3, sep=r'\t',
                                    error_bad_lines=False, engine='python')
            my_file.close()


        cycler_data = lines.iloc[:, 0:10]
        print (cycler_data.shape)
        header_list = ['id_num', 'time', 'volt', 'current', 'del2', 'cap(mAh)',
                       'cap(microAh)', 'en(mWh)','en(microWh)', 'Date/Time']

        cycler_data.columns = header_list
        del cycler_data['del2'], cycler_data['en(microWh)'], \
            cycler_data['cap(microAh)']

        # added extra 'id' columns to shift the first rows
        header_list = ['id', 'id_num', 'time', 'volt', 'current',
                       'cap(mAh)', 'en(mWh)', 'Date/Time']
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
                                                            self.__PERIOD__)


        cycler_data.to_csv(str(self._filename) + '.csv')                             #cycler path

        return cycler_data


    def merge_column(self, table):

        print (table.shape)

        NAN_finder = table['id'].notna()                                        # a boolean list of ID columns
        
        ind = []
        for i in range(len(NAN_finder)):
            if NAN_finder[i] == True:
                ind = np.append(ind, i)
        

        print ('ind: {}'.format(ind))
        id_num      = table.columns.get_loc("id_num")
        cap_Ah      = table.columns.get_loc("cap(mAh)")
        energy_Wh   = table.columns.get_loc("en(mWh)")

        # add 21.00 for real capacity
        # for i in range(0, int(ind[1])):
        #     table.iat[i, cap_mAh] = 38 + table.iat[i, cap_mAh]
        table['cap(mAh)']    = table['cap(mAh)'].astype(float)
        table['en(mWh)']     = table['en(mWh)'].astype(float)


        for i in range(len(ind) - 1):

            # Adding capacity - CC charge --> CV charge
            if (table.iat[int(ind[i]), id_num] == 'CV_Chg' and
                table.iat[int(ind[i - 1]), id_num]) == 'CC_Chg':

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]                    # store the capacity
                tot_wh  = table.iat[int(ind[i]) - 1, energy_Wh]                 # store the energy

                diff    = int(ind[i + 1]) - int(ind[i])                         # find the length of the stage

                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah]      += tot_cap
                    table.iat[int(ind[i]) + j, energy_Wh]   += tot_wh

            # Adding capacity - CV charge --> CC charge
            elif (table.iat[int(ind[i]), id_num] == 'CC_Chg' and
                  table.iat[int(ind[i - 1]), id_num] == 'CV_Chg'):

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]
                tot_wh = table.iat[int(ind[i]) - 1, energy_Wh]

                diff    = int(ind[i + 1]) - int(ind[i])

                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah]      += tot_cap
                    table.iat[int(ind[i]) + j, energy_Wh]   += tot_wh


            # Keep the same capacity of CV_charge for rest cycle
            elif ((table.iat[int(ind[i]), id_num] == 'Rest' and
                  table.iat[int(ind[i - 1]), id_num] == 'CC_Chg' and
                  table.iat[int(ind[i + 1]), id_num] == 'CC_DChg')) or \
                ((table.iat[int(ind[i]), id_num] == 'Rest' and
                  table.iat[int(ind[i - 1]), id_num] == 'CV_Chg' and
                  table.iat[int(ind[i + 1]), id_num] == 'CC_DChg')):

                tot_cap = table.iat[int(ind[i]) - 1, cap_Ah]
                tot_wh  = table.iat[int(ind[i]) - 1, energy_Wh]

                diff    = int(ind[i + 1]) - int(ind[i])

                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah]      += tot_cap
                    table.iat[int(ind[i]) + j, energy_Wh]   += tot_wh


            # Keep the last capacity/power of CCCV_charge for rest cycle
            elif (table.iat[int(ind[i]), id_num] == 'Rest' and
                  table.iat[int(ind[i - 1]), id_num] == 'CCCV_Chg'):

                tot_cap = float(table.iat[int(ind[i]) - 1, cap_Ah])
                tot_wh  = float(table.iat[int(ind[i]) - 1, energy_Wh])
                diff    = int(ind[i + 1]) - int(ind[i])

                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah]      += tot_cap
                    table.iat[int(ind[i]) + j, energy_Wh]   +=  tot_wh

            # Subtraction the capacity for dischage cycle
            elif (table.iat[int(ind[i + 1]), id_num] == 'Rest' and
                  table.iat[int(ind[i]), id_num] == 'CC_DChg'):

                tot = table.iat[int(ind[i + 1]) - 1, cap_Ah]
                tot_mwh = table.iat[int(ind[i + 1]) - 1, energy_Wh]
                diff = int(ind[i + 1]) - int(ind[i])
                for j in range(diff):
                    table.iat[int(ind[i]) + j, cap_Ah] = tot - \
                                                          table.iat[int(ind[i]) + j, cap_Ah]
                    table.iat[int(ind[i]) + j, energy_Wh] = tot_mwh - \
                                                             table.iat[int(ind[i]) + j, energy_Wh]


            # Subtraction the capacity for dischage cycle
            # elif (table.iat[int(ind[i - 1]), id_num] == 'Rest' and
            #     table.iat[int(ind[i]), id_num] == 'CC_DChg' and
            #     table.iat[int(ind[i + 1]), id_num] == 'CCCV_Chg'):
            #
            #     tot_cap = table.iat[int(ind[i + 1]) - 1, cap_Ah]
            #     tot_wh  = table.iat[int(ind[i + 1]) - 1, energy_Wh]
            #     # tot_sec = table.iat[int(ind[i]) - 1, sec]                       # total sec from Rest
            #     diff    = int(ind[i + 1]) - int(ind[i])
            #
            #     for j in range(diff):
            #         table.iat[int(ind[i]) + j, cap_Ah] = tot_cap -\
            #                                              table.iat[int(ind[i]) + j, cap_Ah]
            #         table.iat[int(ind[i]) + j, energy_Wh] = tot_wh - \
            #                                             table.iat[int(ind[i]) + j, energy_Wh]
                    # table.iat[int(ind[i]) + j, sec] += tot_sec

            # for cycler ends up at Discharge cycle
            # Subtraction the capacity for dischage cycle
            if (i == len(ind) - 2 and
                table.iat[int(ind[i]), id_num] == 'Rest' and
                table.iat[int(ind[len(ind) - 1]), id_num] == 'CC_DChg'):

                tot_cap = table.iat[int(ind[i+1]) -2, cap_Ah]
                tot_wh  = table.iat[int(ind[i+1]) -2, energy_Wh]

                print ('length table {}\n\n'.format(table.index))
                diff = len(table.index) - int(ind[i+1])

                for j in range(diff):
                    table.iat[int(ind[i+1]) + j, cap_Ah] = tot_cap - \
                                                         table.iat[int(ind[i+1]) + j, cap_Ah]
                    table.iat[int(ind[i+1]) + j, energy_Wh] = tot_wh - \
                                                            table.iat[int(ind[i+1]) + j, energy_Wh]
        return table


    def calculate_SoH(self, table, rated_cap=None):
        SoH_value = 100

        ind = table[table['id'].notna()].index.tolist()                         # a list of ID rows
        print (ind)

        cap_ah_arr = []
        for i in ind:
            # if table['id_num'][i] == 'CCCV_Chg':
            #     cap_ah_arr.append( table['volt'][i])
            if table['id_num'][i] == 'Rest':
                cap_ah_arr.append( table['cap(mAh)'][i])
        max_cap_Ah = max(cap_ah_arr)
        print ('max capacity: {}'.format(max_cap_Ah))

        if rated_cap is None:
            pass
        else:
            SoH_value *= max_cap_Ah/rated_cap


        return round(SoH_value, 2)


    def calculate_SoC(self, table, actual_capacity=None, rated_cap=None):


        if rated_cap is None:
            table['SoH'] = 100*actual_capacity/1
        else:
            table['SoH']    = 100 * actual_capacity / rated_cap
            table['SoC']    = 100 * table['cap(mAh)'] / actual_capacity

        return table


    @staticmethod
    def _filter_data_by_timeInterval(table, sec):
        '''
        Merge the table with a time step of 0.1s
        :param sec: time step (second)
        :return: new table with time step of 5 sec
        '''

        NAN_finder = table['id'].notna()  # result is in a boolean list

        # global ind
        ind = []
        for i in range(len(NAN_finder)):
            if NAN_finder[i] == True:
                ind = np.append(ind, i)
        print (ind)
        np.sort(ind)

        tb = pd.DataFrame()

        for i in range(len(ind)):
            table_stage = table.loc[[int(ind[i])]]  							# grasp the stage id
            print (table_stage.head())

            tb = pd.concat([tb, table_stage], axis=0)
            if i < len(ind) -1:
                table_data = table.iloc[int(ind[i]) + 1: int(ind[i + 1]): sec ].copy()  # grasp the data instance
            else:
                table_data = table.iloc[int(ind[i]) + 1: len(table.index): sec ].copy()  # grasp the data instance
            print (table_data.head().to_string())

            tb = pd.concat([tb, table_data], axis=0)

        tb.columns = ['id', 'id_num', 'time', 'volt', 'current',
                      'cap(mAh)', 'en(mWh)', 'Date/Time']
        tb.sort_values('id')
        # del tb['extra']

        return tb


    @staticmethod
    def _isTimeValid(date_string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(date_string, fuzzy=fuzzy)
            return True

        except:
            print ("wrong date format")
            return False

    @staticmethod
    def _convert_timestr_to_dateObj(neware, time_string):
        if cycler_preprocessing._isTimeValid(time_string) and neware:
            return datetime.datetime.strptime(time_string, "%m/%d/%Y %H:%M:%S")

        elif cycler_preprocessing._isTimeValid(time_string) and (neware is False):
            return datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")

        else:
            return None



    def post_csv_data(self, table, battery_id, dtb, collection):

        print("Initializing database")
        echoes_db       = database(database=dtb)

        '''
        A specs of tested battery:
        - full capacity
        - note
        - module
        '''
        # log_master = {
        #     'batter_id'     : battery_id,
        #     'note'          : 'Aging mercedes cell',
        #     'rated_capacity': battery_cap.mercedes.value,
        #     'test_machine'  : 'echoes-two-101, Neware channel 1',
        #     'channel'       : None,
        #
        # }
        # result = echoes_db.insert(log_master, collection=collection)
        # self.dprint('log master: {}'.format(result))

        batch_size = 1000
        insert_list = []
        count = 0

        del table['Unnamed: 0']
        del table['time']#, table['del1'], table['del2']
        data_table = json.loads(table.to_json(orient='records'))

        for idx, aLog in enumerate(data_table):
            temp = self._convert_timestr_to_dateObj(self._neware,
                                                    aLog['Date/Time'])
            if temp:
                print (temp.isoformat())
                aLog['Date/Time'] = temp
            else:
                continue

                # try:
		            # aLog['Date/Time'] = datetime_format(self._neware, aLog['Date/Time'])
		            # print (aLog['Date/Time'])
                # except:
                #     print ('wrong format')
                #     continue

            aLog['battery_id'] = battery_id

            count += 1
            insert_list.append(aLog)

            if count >= batch_size or idx == len(table.index) - 1:
                result = echoes_db.insert_multiple(insert_list,
                                                  collection=collection)
                print (result)
                count = 0                                                       #reset counter
                insert_list = []                                                #zero out the list


        echoes_db.close()

        return


    # Prints messages with function and class
    def dprint(self, txt, timestamp=False, error=False, level=1):
        if self._debug_level != None:
            if level <= self._debug_level:
                if self._debug or error:
                    function_name = sys._getframe(1).f_code.co_name
                    if timestamp:
                        print ("  {} {}:{}'()': {}".format(datetime.now(),
                                                           self._class,
                                                           function_name, txt))
                        # print("  " + str(
                        #     datetime.now()) + " " + self._class +
                        #       ":" + function_name + "(): " + txt)
                    else:
                        print("  " + self._class + ":" + function_name + "(): " + txt)
        else:
            return "skip"
        return


class echoes_sorting(object):

    __PERIOD__      = 1                                                         #time differnce between each capture
    __start_row__   = 1                                                         #number of header to remove
    ind         = []                                                            #index of stage

    _debug_level = None
    _class       = None
    _debug       = None

    def __init__(self, path=None, neware = True, time_between_capture=1, debug = False):
        '''
        :param filename: Path to the data set
        :param neware: True if sorting the Neware data report
        :param start_row: number of header to remove
        :param period: time difference between each capture
        :param debug:
        '''
        self._debug = debug
        self._class = self.__class__.__name__

        self._neware   = neware
        self.__PERIOD__= time_between_capture

        if not path:
            self.dprint('No data set specified', error = True)
            exit()
        else:
            self._path = path
        self.dprint('Initializing data cleaning algo')


    def close(self):
        return True

    # Prints messages with function and class
    def dprint(self, txt, timestamp=False, error=False, level=1):
        if self._debug_level != None:
            if level <= self._debug_level:
                if self._debug or error:
                    function_name = sys._getframe(1).f_code.co_name
                    if timestamp:
                        print("  " + str(
                            datetime.now()) + " " + self._class +
                              ":" + function_name + "(): " + txt)
                    else:
                        print("  " + self._class + ":" + function_name + "(): " + txt)
        else:
            return "skip"
        return

    # calculate the time difference in seconds. Return int
    def calculate_time(self, begin, end):

        print ('end {}, begin {}'.format(end, begin))
        end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        if self._neware:
            begin = datetime.datetime.strptime(begin, '%m/%d/%Y %H:%M:%S')
        else:
            begin = datetime.datetime.strptime(begin, '%Y-%m-%d %H:%M:%S')

        diff = (end - begin)
        sec = diff.total_seconds()

        return sec


    def find_capacity(self, begin, end, table):
        line = self.__start_row__

        diff = self.calculate_time(begin, end)
        line += int( diff / self.__PERIOD__ )
        
        # identify the index to grasp the proper row of data instance
        cycler_end_temp = table['Date/Time'][line]

        while cycler_preprocessing._isTimeValid(cycler_end_temp) is False:
            line = line + 1
            cycler_end_temp = table['Date/Time'][line]


        print ('grasp a time Node: {}'.format(cycler_end_temp))

        diff = self.calculate_time(cycler_end_temp, end)
        line += int(diff / self.__PERIOD__)

        print ('cycler_end_temp_correct: {}'.format(table['Date/Time'][line]))
        print ("correct diff: {} \n".format(diff))

        return line, table['cap(mAh)'][line], table['en(mWh)'][line],\
            table['current'][line], table['volt'][line], \
            table['SoH'][line], table['SoC'][line]

    
    # return a sorted table with capacity, filename, index
    def sort_by_name(self, filelist, table):
        cap, power      = [], []
        index, filename = [], []
        volt,current    = [], []
        charging= []
        SoH     = []
        SoC     = []

        cycler_start_time = table['Date/Time'][self.__start_row__]              # Read the start time in Cycler

        for i, element in enumerate( filelist ):
            with open(str(element) ) as json_file: #self._path + element
                aCapture = json.load(json_file)
            json_file.close()

            print ('captureID: {}'.format(aCapture['capture_number']))

            convert_UTC_to_EDT = False
            if convert_UTC_to_EDT:
                echoes_UTC = datetime.datetime.strptime(aCapture['timestamp'],
                                               '%Y-%m-%dT%H:%M:%S')

                echoes_convert_EDT = echoes_UTC - timedelta(hours=4)            # convert UTC to EDT timezone
                echoes_endtime = echoes_convert_EDT.strftime('%Y-%m-%d %H:%M:%S')
                print (echoes_endtime)

            else:
                echoes_endtime = datetime.datetime.strptime(aCapture['timestamp'],
                                '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

                # echoes_endtime = datetime.strptime(aCapture['timestamp'],
                #                                    '%Y-%m-%dT%H:%M:%S-04:00').strftime(
                #     '%Y-%m-%d %H:%M:%S')
                print (echoes_endtime)



            row, c, p, curr, voltage, soh, soc  = self.find_capacity(cycler_start_time, echoes_endtime, table)
            # row, c, p, curr, voltage  = self.find_capacity(cycler_start_time, echoes_endtime, table)

            index.append(row)
            cap.append(c)
            power.append(p)
            volt.append(voltage)
            current.append(curr)
            filename.append(element.stem)
            SoH.append(soh)
            SoC.append(soc)

            if curr < 0:
                charging.append( -1 )
            else:
                charging.append( 1 )

        print ("start sorting")
        # column = ['index', 'charging', 'volt', 'current', 'cap(mAh)',
        #         'power(Wh)', 'FileName']
        # table_sorted = pd.DataFrame({'index'    : index, 'charging' :charging,
        #                             'volt'     : volt, 'current'  : current,
        #                             'cap(mAh)'  : cap, 'power(Wh)':power,
        #                             'FileName' : filename},
        #                             columns=column)


        column = ['index', 'charging', 'volt', 'current', 'cap(mAh)',
                'power(mWh)', 'FileName', 'SoH', 'SoC']

        table_sorted = pd.DataFrame({'index'    : index, 'charging' :charging,
                                    'volt'     : volt, 'current'  : current,
                                    'cap(mAh)'  : cap, 'power(mWh)':power,
                                    'FileName' : filename, 'SoH' : SoH, 'SoC' : SoC},
                                    columns=column)                             # columns=[] used to set order of columns

        del table_sorted['index']
        # # table_sorted = table_sorted.sort_values('index')
        print ("done sorting")
        return table_sorted
        


class battery_cap(Enum):
    'unit: mAh'
    mercedes    = 56000
    tunacan     = 66000
    toyotaCell  = 25800
    lenovo      = 3000
    enel        = 114000
    apple       = None
    hyundai     = None
    subaru      = None



class Test(unittest.TestCase):
    
    _cycler_txt_report = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Experiment/ET_CouplantCyclingState')
    echoes_cycler_path = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Experiment/ET-Couplant-Cylcing-State_secondary')

    battery_id      = 'TC'    #raw_input('battery_id \n')
    rated_cap       = battery_cap.tunacan.value
    time_btw_logs   = 10                                                         # time btw each capture log in cycler
    channel         = 'primary'
    _isNeware  		= True

    dtb             = 'mercedes'
    collection      = '{}-cycler'.format(battery_id)


    cycler_sort = cycler_preprocessing(
        filename    =_cycler_txt_report,
        neware      = _isNeware,
        time_sync_fix=False, debug=False)

    echoes_sort = echoes_sorting(
        path    = echoes_cycler_path,
        neware  = _isNeware,
        time_between_capture = time_btw_logs,
        debug=True)


    def test_clean_data(self, cycler_sort=cycler_sort):
        print (self.battery_id)
        clean_table = cycler_sort.clean_test_data()

        return clean_table


    def test_merge_column(self, cycler_sort=cycler_sort):

        Test.test_clean_data(self, cycler_sort)	#test_clean_data doesn't return table
        with open (str(self._cycler_txt_report) + '.csv') as my_file:
            clean_table = pd.read_csv(my_file, sep=',', error_bad_lines=False)
        print (clean_table.head().to_string())

        table = cycler_sort.merge_column(clean_table)                              	# Merge capactity of CC and CV stages
        # table.loc[:, 'cap(mAh)'] *= 1000
        # table.loc[:, 'en(mWh)'] *= 1000
        table.to_csv(str(self._cycler_txt_report) + '_merged.csv')
        return table


    def test_calculate_SOHSOC(self,cycler_sort=cycler_sort):
        table = Test.test_merge_column(self, cycler_sort=cycler_sort)

        SoH_value = cycler_sort.calculate_SoH(table, rated_cap=self.rated_cap)
        print('SOH: {0:.2f}'.format(SoH_value) )

        table = cycler_sort.calculate_SoC(table, SoH_value*self.rated_cap/100,
                                          self.rated_cap)

        print (table.head().to_string())
        table.to_csv(str(self._cycler_txt_report) + '_merged_full.csv')
        return


    def test_sort_Cycler_Echoes(self, cycler_sort=cycler_sort,
                                echoes_sort=echoes_sort):
        with open(str(self._cycler_txt_report) + '_merged_full.csv') as readTable:
            table = pd.read_csv(readTable, sep=',', error_bad_lines=False)
        readTable.close()

        print (table.head().to_string())

        # key = 'cycle'
        # filelist = display_list_of_file(self.echoes_cycler_path, key)
        key = '*.json'
        filelist = sort_folder_by_name_universal(self.echoes_cycler_path, key)
        print (filelist)

        _start_row = 1        
        sorted_table = echoes_sort.sort_by_name(filelist, table)
        # sorted_table.to_csv(str(self.echoes_cycler_path) +
        #                     '{}_{}_echoescyler_final.csv'.format(
        #                         self.battery_id, self.channel))

        sorted_table.to_excel(str(self.echoes_cycler_path) +
                            '_echoescyler_final.xlsx')
        return


    def test_post_data_to_mongo(self, cycler_sort=cycler_sort,
                                battery_id=battery_id):
        
        with open (str(self._cycler_txt_report) + '_merged_full.csv') as my_file:
            table = pd.read_csv(my_file, sep=',', error_bad_lines=False)

        my_file.close()
        del table['id'], table['id_num']
        print (table.head().to_string())

        cycler_sort.post_csv_data(table, battery_id, self.dtb, self.collection)

        return





if __name__ == 'main':
    unittest.main()