#coding:utf-8

from sklearn.datasets import load_iris
import numpy as np
import matplotlib.pyplot as plt
import itertools

data = load_iris()
x = data['data']
y = data['target']
col_names = data['feature_names']

#print data.keys()
print y

plt.close()
plt.figure(1)

subplot_start = 321
col_numbers = range(0, 4)
col_pairs = itertools.combinations(col_numbers, 2)

plt.subplots_adjust(wspace=0.5)

# scatter参数： c=颜色, marker=形状

for col_pair in col_pairs:
    plt.subplot(subplot_start)
    print col_pair
    plt.scatter(x[:,col_pair[0]], x[:,col_pair[1]], c=y, marker='D')
    plt.xlabel(col_names[col_pair[0]])
    plt.ylabel(col_names[col_pair[1]])
    subplot_start +=1

plt.show()