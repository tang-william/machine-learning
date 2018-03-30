# -*- coding:utf-8 -*-

import numpy as np
# import matplotlib.pylab as pl
from scipy.optimize import curve_fit
from math import e

class LT(object):

    def __init__(self, x, y, fitfunc="power",linear=True):
        self.x = x
        self.y = y
        self.fitfunc = fitfunc
        self.linear=linear

    def retention_fit(self,x,a,b):
        if self.fitfunc == "ln":
            return a*np.log(x)+b
        else:
            return a * x ** b

    def linear_retention_fit(self,x,a,b):
        return a + x*b

    def calc_r2(self,x,y,*popt):
        residuals = y-self.retention_fit(x, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y-np.mean(y))**2)
        return 1-(ss_res/ss_tot)

    def gen_func(self, a, b):
        if self.fitfunc == "ln":
            return "y= " + str(a)+"ln(x)+ " + str(b)
        else:
            return "y= " + str(a) + "x**" + str(b)

    # 部署到服务器上时，不需要matplotlib
    # def view(self):
    #     lt,func,r2,i,popt=self.calc_lt()
    #     pl.plot(self.x, self.y, ".",color="green")
    #     pl.plot(self.x, self.retention_fit(self.x,*popt),"r", color="blue")
    #     pl.legend(("Real Data","Retention Curve"))
    #     pl.annotate(func+"\n"+"lt:"+str(lt)+"\n"+"r2:"+str(r2)+"\n"+"x0:"+str(i), xy=(len(self.x)/2,np.max(self.y)/2),
    #                 xytext=(len(self.x)/2, np.max(self.y)/2))
    #     pl.xlabel("Day")
    #     pl.ylabel("Drr")
    #     return pl.show

    def short_lt(self):
        popt, pcov = curve_fit(self.linear_retention_fit, np.log(self.x), np.log(self.y))
        a = e ** popt[0]
        b = popt[1]
        return float(a),float(b)

    def calc_lt(self):
        popt, pcov = curve_fit(self.retention_fit, self.x, self.y)
        a=popt[0]
        b=popt[1]
        i = 0
        lt = 0
        x0=0
        if self.fitfunc=="ln":
            while True:
                i = i + 1
                lt = lt + self.retention_fit(i, a, b)
                if self.retention_fit(i, a, b) < 0 :
                    x0=i
                    break
        elif self.fitfunc == "power" and self.linear == True:
            popt, pcov = curve_fit(self.linear_retention_fit, np.log(self.x), np.log(self.y))
            a = e ** popt[0]
            b = popt[1]
            popt = np.asarray([a, b])
            lt_list = []
            while True:
                i = i + 1
                lt = lt + self.retention_fit(i, a, b)
                if i == 366:
                    x0=i
                    lt_list.append(lt)
                    break
            lt_tmp = self.retention_fit(365, a, b)
            for x in range(366, 1001):
                lt_tmp = lt_tmp * 0.997
                lt_list.append(lt_tmp)
            lt = sum(lt_list)
        else:
            lt_list = []
            while True:
                i = i + 1
                lt = lt + self.retention_fit(i, a, b)
                if i == 366:
                    x0=i
                    lt_list.append(lt)
                    break
            lt_tmp = self.retention_fit(365, a, b)

            for x in range(366,1001):
                lt_tmp=lt_tmp * 0.997
                lt_list.append(lt_tmp)
            lt = sum(lt_list)

        r2 = self.calc_r2(self.x, self.y, *popt)
        func = self.gen_func(a, b)

        return {"lt":lt,"fit_func":func,"R2":r2,"BreakPoint":x0,"params":[popt[0],popt[1]]}




