import time
import datetime
import calendar

def getBetweenMonth(begin_date, end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y%m%d")
    end_date = datetime.datetime.strptime(end_date, "%Y%m%d")

    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y%m")
        date_list.append(date_str)
        begin_date = add_months(begin_date, 1)
    date_list.append(end_date.strftime("%Y%m"))
    return date_list


def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

for i in getBetweenMonth('20161005', '20170403'):
    print i

#
# import json
# import urllib2
#
# a='1,2,3,4,8'
#
# url = "http://172.16.10.235:5000/lt/data?fit_func=power&retention_day=" + a + "&retention_rate=0.6,0.4,0.3,0.3,0.1"
#
# print url
#
# req = urllib2.Request(url)
# res_data = urllib2.urlopen(req)
# res = res_data.read()
# text = json.loads(res)
# print text['lt']



