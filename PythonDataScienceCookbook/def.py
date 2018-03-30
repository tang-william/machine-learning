import numpy as np
import pandas as pd


df = pd.DataFrame({'key1':['a', 'b', 'c', 'd', 'e'],
                   'data2':np.random.randn(5)})

df2 = pd.DataFrame({'key1':['a', 'b', 'c', 'd', 'e'],
                   'data1':np.random.randn(5)
                   })

print df
print df2


df3 = pd.merge(df, df2, how='inner', on=['key1'])
print df3

df3['c'] = df3['data2'] * df3['data1']

df4 = df3[['key1','c']]
df4['b'] = df3['data2'] * df3['c']

print "end"
print df4
print df4.dtypes


df = pd.DataFrame([['c']],
                   index=['error'])

df2 = pd.DataFrame({'key1':['a'],
                   'data1':np.random.randn(1)
                   })

print str(df2.shape)

# dic1 = dict()
# dic1['sdf'] = 4
# dic1['kkk'] = 3
# print type(dic1.items())
#
#
#
# import datetime
# import time
# import calendar
#
# def get_days_ago(end_date, days):
#     end_date =  datetime.datetime.strptime(end_date, "%Y%m%d")
#     d3 = end_date - datetime.timedelta(days=days)
#     print d3.strftime('%Y%m%d')
#
# get_days_ago('20170621', 5)

# r=  df['data1'].groupby(df['key1']).apply(list)

# df2 = pd.DataFrame(r)

#print df2


# for (k1), group in df.groupby(['key1']):
#     print k1
#     print list(group['data1']), list(group['data2'])
#     print ','.join( map(str,list(group['data1'])))

