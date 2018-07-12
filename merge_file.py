
import numpy as np
import os
import glob
import pandas as pd

path = r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data"
table = pd.DataFrame()

# def _make_DataFrame():
for filename in glob.glob(os.path.join(path, "*.txt")):
    my_file = open(filename)
    table = pd.read_csv(my_file, header=3, delimiter='\t', nrows=10)
    my_file.close()

temp = table.iloc[:, 1:12]
table = temp

#rename the dataframe
table.columns = ['id', 'id_num', 'time', 'del', 'current', 'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)', 'en(microWh)', 'Date/Time']
del table['del']
del table['del2']
print(table.to_string())

print table['id'].notna().tolist()

cycle_1 = 0
for i, row in enumerate( pd.notna(table['id']).tolist() ):
    if row == True:
        print i
        cycle_1 = table.iloc[i+2,4]                         #go back 1 row to grasp the cap value
                                                            #might go to the last element in row
        print 'cycle_1: ' + str(cycle_1)



def _addition_value(x):
    return x * 0.5

# def func(x, y):
#     if x

for index, element in enumerate(table['id'].notna().tolist()):
    if element == True:
        print 'element %s' % element
        print table['cap(mAh)'][index]
        print '\n'
        # table['cap(mAh)'][index] = table.apply(_addition_value(table['cap(mAh)'][index]), axis=1)
#replace the data to the original dataframe
# table['cap(mAh)'] = table.apply(lambda row: _addition_value(row['cap(mAh)']), axis=1)

        table['cap(mAh)'] = table.apply(lambda row: 0 if row['id_num'] != 'CC_Chg' else _addition_value(row['cap(mAh)']), axis=1)
        # table['cap(mAh)'] = table.apply(lambda row: func(row['id'],row['cap(mAh)']), axis=1)
        print table['cap(mAh)'][2]

print(table.to_string())