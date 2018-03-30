import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

import pandas as pd


def func1(x, a, b):
    return a * (x**b)

#df=pd.read_csv('/home/coohua/tyh/ltv/data/lifetime.csv')



str1 = "0.842563780962,0.282283102065,0.209868583656,0.185931736663,0.172610301933,0.162950056219,0.156021281457,0.149957755257,0.143644833883,0.138012235398,0.134283183751,0.130637263828,0.127797212665,0.124987699686,0.122554824316,0.119842015588,0.117247966467,0.11445372258,0.11266045252,0.110860396198,0.109263927772,0.107689514701,0.10576730564,0.104006270331,0.102406408773,0.100984686626,0.0998632566262,0.0987808476403,0.0976441485485,0.0958525750546,0.0943002173398"
str2 = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31"
list1 = [float(i) for i in str1.split(',')]
list2 = [int(i) for i in str2.split(',')]

ydata = np.array(list1)
xdata = np.array(list2)




# plt.plot(xdata, ydata, 'b-', label='data')
# plt.show()

popt, pcov = curve_fit(func1, xdata, ydata)
x_new=np.linspace(1, 1000, 1000)
y_new=func1(x_new, popt[0], popt[1])


rate=np.linspace(1, 1, 1000)
for index,v in enumerate(rate):
    if index>300:
        rate[index]=rate[index-1] * 0.9965

data = np.sum(y_new*rate)
print data


# xdata=np.array([1,2,3,4,5,6,7,14])
# x_new=np.linspace(1, 1000, 1000)

# for index, row in df.iterrows():
#     ydata=row[['rate1','rate2','rate3','rate4','rate5','rate6','rate7','rate14']].values.astype(float)
#     popt, pcov = curve_fit(func1, xdata, ydata)
#     y_new=func1(x_new, popt[0], popt[1])
#     df['lifetime'].values[index]=np.sum(y_new*rate)
#     print row['channel'], np.sum(y_new*rate)
#
# print df

#df.to_csv('/home/coohua/tyh/ltv/data/lt.csv', header=False, index=False)
