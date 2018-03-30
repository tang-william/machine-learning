#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import os,sys
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import COMMASPACE
from email.header import Header
import pandas as pd

def sendqqmail(username,password,mailfrom,mailto,subject,content):
    gserver = 'smtp.exmail.qq.com'
    gport = 465

    try:
        msg = MIMEMultipart()
        msg['from'] = mailfrom
        msg['to'] = COMMASPACE.join(mailto)
        msg['Reply-To'] = mailfrom
        msg['Subject'] = Header(subject,'utf-8')
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="utf-8"

        html = MIMEText(content, 'html', 'utf-8')
        msg.attach(html)

        smtp = smtplib.SMTP_SSL(gserver, gport)
        smtp.set_debuglevel(0)
        smtp.ehlo()
        smtp.login(username,password)
        smtp.sendmail(mailfrom, mailto, msg.as_string())
        smtp.close()
    except Exception,err:
        print "Send mail failed. Error: %s" % err

style = """
<style type="text/css">
  .dataframe
    {
    font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
    width:100%;
    border-collapse:collapse;
    }

    .dataframe td, .dataframe th
    {
    font-size:1em;
    border:1px solid #F5F5F5;
    padding:3px 7px 2px 7px;
    }

    .dataframe th
    {
    font-size:1.1em;
    text-align:left;
    padding-top:5px;
    padding-bottom:4px;
    background-color:#708090;
    color:#ffffff;
    }

    .dataframe tr.alt td
    {
    color:#000000;
    background-color:#DCDCDC;
    }
</style>
"""

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    to_df = pd.read_csv("receiver.csv", header=None)
    to = to_df.values.tolist()[0]
    subject=sys.argv[0]
    df = pd.read_csv("t.csv", header=None)
    df.columns = ["指标", "今日数据", "昨日数据", "相差比例"]
    df.to_html("t.html", index=False)
    file_object = open('t.html')
    try:
        content = file_object.read()
    finally:
        file_object.close()
    content = "%s %s" %(style, content)
    sendqqmail('monitor@coohua.com','PGMaiX7BC9nr','monitor@coohua.com', to, subject, content)

if __name__ == "__main__":
    main()


