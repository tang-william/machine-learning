#coding:utf-8

# heat maps 热图, 用颜色的

from sklearn.datasets import load_iris
from sklearn.preprocessing import scale
import numpy as np
import matplotlib.pylab as plt

#1 load data
data = load_iris()
x = data['data']
y = data['target']
col_names = data['feature_names']

# 2. scale the variables, with mean value
#print x
x = scale(x, with_std=False)
#print x
x_ = x[1:26,]
y_labels = range(1, 26)


print x_
print y_labels

# 3. plot the heat map
plt.figure(1)
fig, ax = plt.subplots()
ax.pcolor(x_, cmap=plt.cm.Greens, edgecolors='k')
ax.set_xticks(np.arange(0, x_.shape[1])+0.5)
ax.set_yticks(np.arange(0, x_.shape[0])+0.5)
ax.xaxis.tick_top()
ax.yaxis.tick_left()
ax.set_xticklabels(col_names, minor=False, fontsize=10)
ax.set_yticklabels(y_labels, minor=False, fontsize=10)
plt.show()