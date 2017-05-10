#coding:utf-8

# 点阵图
# dot_plots 点阵图，适合小型、中型数据，大型数据适合直方图 histogram

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from collections import  OrderedDict
from matplotlib.pylab import frange

fill_data = lambda x : int(x.strip() or 0)
data = np.genfromtxt('president.txt', dtype=(int, int), converters={1:fill_data}, delimiter=",")
x = data[:, 0]
y = data[:, 1]

# 给定一组数据，Counter 返回 数据点及其频数
x_freq = Counter(y)
x_ = np.array(x_freq.keys())
y_ = np.array(x_freq.values())

print x_
print y_

x_group = OrderedDict()
group = 5
group_count = 1
keys = []
values = []

for i, xx in enumerate(x):
    keys.append(xx)
    values.append(y[i])
    if group_count == group:
        x_group[tuple(keys)] = values
        keys = []
        values = []
        group_count = 1
    group_count += 1
x_group[tuple(keys)] = values

print x_group

plt.subplot(311)
plt.title("Dot Plot by Frequency")
plt.plot(y_, x_, "ro")
plt.xlabel("Count")
plt.ylabel("PR")

# x 轴范围
plt.xlim(min(y_)-1, max(y_)+1)

plt.subplot(312)
plt.title("Simple dot plot")
plt.xlabel("PR")
plt.ylabel("Frequency")

for key, value in x_freq.items():
    print key
    print value
    x__ = np.repeat(key, value)
    y__ = frange(0.1, value/10.0, 0.1)
    try:
        plt.plot(x__, y__, 'go')
    except ValueError:
        print x__.shape, y__.shape
    # 设置x轴和y轴的最小和最大值
    plt.ylim(0.0, 0.4)
    plt.xlim(xmin=-1)


plt.xticks(x_freq.keys())












plt.show()
