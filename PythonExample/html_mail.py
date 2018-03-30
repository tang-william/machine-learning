# -*- coding: utf-8 -*-
# 一个通过拼接html方式优化邮件内容显示的程序
import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE
from email.header import Header
import xlwt
import numpy as np

# mail_dict = dict(gserver="smtp.exmail.qq.com"
#                 ,gport=465
#                 ,user_name="monitor@coohua.com"
#                 ,password="PGMaiX7BC9nr"
#                 ,mail_from="monitor@coohua.com"
#                )
mail_dict = dict(gserver="smtp.exmail.qq.com"
                ,gport=465
                ,user_name="data@coohua.com"
                ,password="ygnjbwnrDcfuni8npvc9kakI_"
                ,mail_from="data@coohua.com"
               )

# 发邮件
def sendQQMail(subject,content,files,to):
    try:
        msg = MIMEMultipart()
        print msg
        msg['from'] = mail_dict["mail_from"]
        msg['to'] = COMMASPACE.join(to)
        msg['Reply-To'] = mail_dict["mail_from"]
        msg['Subject'] = Header(subject, 'utf-8')
        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "utf-8"
        for file in files:
            basename = os.path.basename(file)
            att = MIMEText(open(file, 'rb').read(), 'base64','gb2312')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename=%s' % basename.decode('utf-8').encode('gb2312')
            msg.attach(att)
        # msg.attach(MIMEText(content, 'plain', 'utf-8'))
        html=MIMEText(content, 'html','utf-8')
        msg.attach(html)
        smtp = smtplib.SMTP_SSL(mail_dict["gserver"], int(mail_dict["gport"]))
        smtp.set_debuglevel(0)
        smtp.ehlo()
        smtp.login(mail_dict["user_name"], mail_dict["password"])
        smtp.sendmail(mail_dict["mail_from"], to, msg.as_string())
        smtp.close()
    except Exception,err:
        print "Send mail failed. Error: %s" % err

# 读取csv文件，转换成list
def csv_to_list(file_name):
    result = []
    f = open(file_name)
    line = f.readline()
    while line:
        line = line.replace('\n','')
        line_cols =line.split(",")
        result_col=[]
        col_num=0
        for line_col in line_cols:
            if col_num == 2:
                result_col.append(line_col[:4])
            else:
                result_col.append(line_col)
            col_num = col_num +1
        result.append(result_col)
        line = f.readline()
    return result


def data_to_html(file_data):
    mail_msg = """
    <html><head>
    <style type="text/css">
    #customers
      {
      font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
      width:100%;
      border-collapse:collapse;
      }

    #customers td, #customers th
      {
      font-size:1em;
      border:1px solid #F5F5F5;
      padding:3px 7px 2px 7px;
      }

    #customers th
      {
      font-size:1.1em;
      text-align:left;
      padding-top:5px;
      padding-bottom:4px;
      background-color:#708090;
      color:#ffffff;
      }

    #customers tr.alt td
      {
      color:#000000;
      background-color:#DCDCDC;
      }
    </style>
    </head><body><p>附件是锁屏召回短信点击数据表:</p>
        """
    mail_msg = "%s%s" % (
                    mail_msg
                    , "<table id=\"customers\" border=\"1\"><tr><th>点击量</th><th>发送量</th><th>点击率</th><th>时间</th></tr>")
    num = 0
    for file_data_row in file_data:
        if num % 2 == 0:
            mail_msg = """%s<tr>""" % (mail_msg)
        else:
            mail_msg = """%s<tr class="alt">""" % (mail_msg)
        num = num + 1
        for file_data_row_col in file_data_row:
            mail_msg = "%s<td>%s</td>" % (mail_msg, file_data_row_col)
        mail_msg = "%s</tr>" % (mail_msg)

    mail_msg = """%s </table> </hr> <p>数据研发</p><p>dev_data@coohua.com</p> </body></html>""" % (mail_msg)
    return mail_msg


def writeExcel(file_name,data):
    path = file_name
    wb = xlwt.Workbook()
    for data_row in data:
        ws = wb.add_sheet(data_row["sheet_name"])
        for data_row_i in data_row["data"]:
            tmp_data = np.array(data_row_i["row"])
            if np.size(tmp_data.shape) == 1 :
                seat_x = data_row_i["seat"][0]
                seat_y = data_row_i["seat"][1]
                for row_x in tmp_data:
                    ws.write(seat_x, seat_y, row_x)
                    seat_y = seat_y + 1
            elif np.size(tmp_data.shape) == 2:
                seat_x = data_row_i["seat"][0]
                for row_x in tmp_data:
                    seat_y = data_row_i["seat"][1]
                    for row_y in row_x:
                        ws.write(seat_x, seat_y, row_y)
                        seat_y = seat_y + 1
                    seat_x = seat_x + 1
                pass
            else:
                pass
            pass
    wb.save(path)


def main():
    to = ['yangchao@coohua.com']
    subject = u"锁屏召回短信点击数据表"
    file_name = "/home/coohua/dev_data/locker_mr/job/f_dau_die_1day/message_recall_monitor.csv"
    file_data = csv_to_list(file_name)
    mail_msg = data_to_html(file_data)
    sheet_1_name = u"页面1"
    sheet_1_data1 = [u"点击量",u"发送量",u"点击率",u"时间"]
    sheet_1_data1_seat = [0, 0]
    sheet_1_data2_seat = [1, 0]
    sheet_1_data2 = file_data
    sheet_1_dict = dict(sheet_name=sheet_1_name, data=[dict(seat=sheet_1_data1_seat, row=sheet_1_data1)
        , dict(seat=sheet_1_data2_seat, row=sheet_1_data2)])
    writeExcel("/home/coohua/dev_data/locker_mr/job/f_dau_die_1day/message_recall_monitor.xls", [sheet_1_dict])
    sendQQMail(subject, mail_msg, ["/home/coohua/dev_data/locker_mr/job/f_dau_die_1day/message_recall_monitor.xls"], to)

if __name__ == "__main__":
    main()