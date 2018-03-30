import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model

# Load the diabetes dataset
diabetes = datasets.load_diabetes()


# Use only one feature
diabetes_X = diabetes.data[:, np.newaxis, 2]

# Split the data into training/testing sets
diabetes_X_train = diabetes_X[:-20]
diabetes_X_test = diabetes_X[-20:]

# Split the targets into training/testing sets
diabetes_y_train = diabetes.target[:-20]
diabetes_y_test = diabetes.target[-20:]


# print diabetes_y_train
# print diabetes_X_train

str1 = "0.842563780962,0.282283102065,0.209868583656,0.185931736663,0.172610301933,0.162950056219,0.156021281457,0.149957755257,0.143644833883,0.138012235398,0.134283183751,0.130637263828,0.127797212665,0.124987699686,0.122554824316,0.119842015588,0.117247966467,0.11445372258,0.11266045252,0.110860396198,0.109263927772,0.107689514701,0.10576730564,0.104006270331,0.102406408773,0.100984686626,0.0998632566262,0.0987808476403,0.0976441485485,0.0958525750546,0.0943002173398"
str2 = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31"
list1 = [float(i) for i in str1.split(',')]
list2 = [int(i) for i in str2.split(',')]
t = np.array([list2,list1]).transpose()
print t[1:-20]
print type(diabetes_X)
# print diabetes_X


cpc2 = 2050942 * 0.129378
cpa2 = 77104 * 0.735594
cpw2 = 1562585 * 0.09
arpu2 = (cpc2 + cpa2 + cpw2)

cpc1 = 3208181 * 0.1048
cpa1 = 292691 * 0.725512
cpw1 = 859733 * 0.146415
arpu1 = (cpc1 + cpa1 + cpw1)

arpu = (arpu2+arpu1)/3563831
print arpu


print arpu2/1736626

str = '20170616'
print  str[0:6]