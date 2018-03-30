#coding:utf-8


# 主成分分析 PCA 是一种无监督学习方法。它保留了数据中的绝大部分变化，也就是数据分布的方向被最大程度地保留下来.
# 特征值，特征向量

# PCA 算法
# 1. 将数据集标准化，均值0
# 2. 找出数据集的相关矩阵和单位标准偏差值
# 3. 将相关矩阵分解成它的特征向量和值
# 4. 基于降序的特征值选择 Top—N 特征向量
# 5. 投射输入的特征向量矩阵到一个新的子空间。

import numpy as np
from sklearn.datasets import load_iris
from sklearn.preprocessing import scale
import scipy
import matplotlib.pyplot as plt


data = load_iris()
x = data['data']
y = data['target']

x_s = scale(x, with_mean=True, with_std=True, axis=0)

#
x_c = np.corrcoef(x_s.T)

eig_val, r_eig_vec = scipy.linalg.eig(x_c)

print 'Eigen values \n %s'%(eig_val)
print '\n Eigen vectors \n %s'%(r_eig_vec)


w = r_eig_vec[:,0:2]
x_rd = x_s.dot(w)

plt.figure(1)
plt.scatter(x_rd[:,0], x_rd[:,1], c=y)
plt.xlabel('1')
plt.ylabel('2')

#plt.show()

print "Component, Eigen Value, % of Variance, Cummulative %"
cum_per = 0
per_var = 0

print eig_val

for i,e_val in enumerate(eig_val):
    per_var = round((e_val.real / len(eig_val)),3)
    cum_per+=per_var
    print ('%d, %0.2f, %0.2f, %0.2f')%(i+1, e_val.real, per_var*100,cum_per*100)

# 将相关矩阵分解为特征向量和特征值是一种通用的技术，可以应用到任意矩阵
# 目的是了解数据分布的主轴，通过主轴观察数据的最大变化
# PCA 可以用来进行探索数据，也可以用来给后续算法做准备，降维只保留最相关的特征给后续分类算法

# PCA 的一个缺点是运算代价昂贵.
# Numpy 里的 corrcoef 函数内置了数据标准化


