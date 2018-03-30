#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import os,sys
import pandas as pd
from mail_util import sendqqmail,style


def fun(x):
    x = x * 100
    return "%.2f%%" % x




def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    to_df = pd.read_csv("receiver.csv", header=None)
    to = to_df.values.tolist()[0]
    subject=sys.argv[1]
    df = pd.read_csv("hour.csv", header=None).fillna(0)
    df.columns = ["指标", "小时", "平均指标", "超过阈值比例"]
    df['平均指标'] = df['平均指标'].apply(lambda x: "%.2f" % x)
    df['超过阈值比例'] = df['超过阈值比例'].apply(lambda x: '%.2f%%' % (x * 100))
    df.to_html("t.html", index=False)
    file_object = open('t.html')
    try:
        content = file_object.read()
    finally:
        file_object.close()
    content = "%s %s %s" %(style, sys.argv[2], content)
    sendqqmail('monitor@coohua.com','PGMaiX7BC9nr','monitor@coohua.com',to,subject,content)

if __name__ == "__main__":
    main()