import pandas as pd
import numpy as np
import thLib as th
import sys

def main():
    path = '/media/jean/Data/titan-echo-board/txt-report/'
    name = '180914_Me02-H100.csv'
    name_edit = '180914_Me02-H100_volt.csv'

    with open(path + name) as outfile:
        table = pd.read_csv(outfile, sep=',', error_bad_lines=False)
    outfile.close()

    del table['id'], table['time'], table['cap(mAh)'], table['Date/Time']
    table.to_csv(path + name_edit)
    return

if __name__ == '__main__':
    sys.exit(main())