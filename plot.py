# import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import os

path = r"/media/kacao/479E26136B58509D/Titan_AES/Python-script/31Ah-Battery-1-30-2018/"

# file_name = os.path.join(path, "2018-06-27-11-35-44-echoes-b.dat")
file_name = '31Ah-Battery-1-30-2018/2018-06-27-11-35-44-echoes-b.dat'
y = []
with open(file_name, 'rb') as outfile:
   reader = outfile.read().splitlines()
   for num in reader:
       print(float(num))
       y.append(float(num))
outfile.close()

print(y)
print(len(y))

# my_file = open("31Ah-Battery-1-30-2018/2018-06-27-11-35-44-echoes-b.dat")
# y_str = my_file.read()
# y_str = y_str.splitlines()
# y = []
# for num in y_str:
#     print(type(float(num)))
#     y.append(float(num))
# print(type(y))
# print(len(y))

fs = 2400000
N = len(y)
dt = 1/fs
x = np.arange(0, dt*N, dt)
print(len(x))
plt.interactive(False)
plt.plot(x, y)
plt.show()
