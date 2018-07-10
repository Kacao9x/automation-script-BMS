import numpy as np
import os
import glob
import pandas as pd

path = r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data"
table = pd.DataFrame()

for filename in glob.glob(os.path.join(path, "*.txt")):
    my_file = open(filename)
    table = pd.read_csv(my_file, header=3, delimiter='\t')

temp = table.iloc[:, 1:12]
table = temp
table.columns = ['id', 'id_num', 'time', 'del', 'current',
                 'del2', 'cap(mAh)', 'cap(microAh)', 'en(mWh)',
                 'en(microWh)', 'Date/Time']
del table['del']
del table['del2']

NA_finder = table['id'].notna()
ind = []

for i in range(len(NA_finder)):
    if NA_finder[i] == True:
        ind = np.append(ind, i)

for i in range(len(ind)):

    if (table.iat[int(ind[i]), 1] == 'CV_Chg' and
        table.iat[int(ind[i - 1]), 1]) == 'CC_Chg':

        tot = table.iat[int(ind[i]) - 1, 4]
        diff = int(ind[i+1]) - int(ind[i])

        for j in range(diff):
            table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

    elif i == len(ind)-1:

        tot = table.iat[int(len(NA_finder) - 1), 4]
        diff = int(len(NA_finder)) - int(ind[i])
        for j in range(diff):
            table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

    elif( table.iat[int(ind[i]), 1] == 'Rest' and
            table.iat[int(ind[i - 1]), 1] == 'CV_Chg'):

        tot = table.iat[int(ind[i]) - 1, 4]
        diff = int(ind[i+1]) - int(ind[i])
        for j in range(diff):
            table.iat[int(ind[i]) + j, 4] = table.iat[int(ind[i]) + j, 4] + tot

    elif( table.iat[int(ind[i + 1]), 1] == 'Rest' and
            table.iat[int(ind[i]), 1] == 'CC_DChg' ):

        tot = table.iat[int(ind[i + 1]) - 1, 4]
        diff = int(ind[i + 1]) - int(ind[i])
        for j in range(diff):
            table.iat[int(ind[i]) + j, 4] = tot - table.iat[int(ind[i]) + j, 4]

table.to_csv(r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/data/Cycler_Data_NIS3_180703.csv")