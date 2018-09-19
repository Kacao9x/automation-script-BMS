from scipy.optimize import fsolve
import pylab
import numpy

# def findIntersection(fun1,fun2,x0):
#     return fsolve(lambda x : fun1(x) - fun2(x),x0)
#
# result = findIntersection(numpy.sin,numpy.cos,0.0)
# x = numpy.linspace(-2,2,50)
# pylab.plot(x,numpy.sin(x),x,numpy.cos(x),result,numpy.sin(result),'ro')
# pylab.show()

st = 'Temperature_1_and_2: 23.567  25.676 oC'
if len(st.split()) > 2:
    temp_1 = st.split()[1]
    temp_2 = st.split()[2]
    # temp_2 = st.rstrip().split('Temperature_1_and_2:')[2]
print (temp_1)
print (temp_2)