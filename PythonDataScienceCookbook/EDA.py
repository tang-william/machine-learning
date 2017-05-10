#coding:utf-8

import numpy as np
from matplotlib.pylab import frange
import matplotlib.pyplot as plt


fill_data = lambda x : int(x.strip() or 0)
data = np.genfromtxt('president.txt',dtype=(int,int),converters={1:fill_data}, delimiter=",")
x = data[:,0]
y = data[:,1]

print x
print y


plt.close('all')  #关闭所有图
plt.figure(1)
plt.title("All data")
plt.plot(x,y,'ro')
plt.xlabel('year')
plt.ylabel('No Presedential Request')
#plt.show()

#3.计算出数据的百分位数（第25、50、75位）以了解数据分布
perc_25 = np.percentile(y,25)
perc_50 = np.percentile(y,50)
perc_75 = np.percentile(y,75)
print
print "25th Percentile = %0.2f"%(perc_25)
print "50th Percentile = %0.2f"%(perc_50)
print "75th Percentile = %0.2f"%(perc_75)
print

# 在图中画出第25、50、75位的百分位水平线。
plt.axhline(perc_25,label='25th perc',c='r')
plt.axhline(perc_50,label='50th perc',c='g')
plt.axhline(perc_75,label='75th perc',c='m')
plt.legend(loc='best')
# plt.show()



y_masked = np.ma.masked_where(y==0,y)
# Remove point 54
y_masked = np.ma.masked_where(y_masked==54,y_masked)


plt.figure(2)
plt.title("Masked data")
plt.plot(x,y_masked,'ro')
plt.xlabel('year')
plt.ylabel('No Presedential Request')
plt.ylim(0,60)

# 在图中画出第25、50、75位的百分位的水平线
plt.axhline(perc_25,label='25th perc',c='r')
plt.axhline(perc_50,label='50th perc',c='g')
plt.axhline(perc_75,label='75th perc',c='m')
plt.legend(loc='best')
plt.show()