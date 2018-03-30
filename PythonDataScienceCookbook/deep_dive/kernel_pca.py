#coding:utf-8

# PCA 假定数据所有变化的主要方向都是直线，它只适合线性分布的数据

from sklearn.datasets import make_circles
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.decomposition import KernelPCA

np.random.seed(0)
x, y = make_circles(n_samples=400, factor=0.2, noise=0.03)
print x, y

plt.close('all')
plt.figure(1)
plt.scatter(x[:,0], x[:,1], c=y)
plt.show()