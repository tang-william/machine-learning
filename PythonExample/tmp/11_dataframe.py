# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

df = pd.DataFrame({"one":np.random.randn(4), "two":np.linspace(1,4,4)})
# print df
# data = np.array(df["one"]).tolist()
# print data


dfmi = pd.DataFrame([list('abcd'),list('efgh'),list('ijkl'),  list('mnop')], columns=pd.MultiIndex.from_product([['one','two'],  ['first','second']]))

# print dfmi['one']['second']
# dfmi['d'] = dfmi['one']['second'] + dfmi['two']['second']

df.replace(1,0.0001)
print df


t = df["one"]
t = t.values.tolist()

print t
print type(t)

print dfmi


tmp_df = df[df.two==2][["one","two"]]
tmp_df.columns = ["sd", "sadf"]
print tmp_df


data = [{'hour': '00', 'snu': 131, 'au': 5763, 'logday': '2018-01-17', 'nu': 131, 'sau': 5763},
        {'hour': '01', 'snu': 187, 'au': 3279, 'logday': '2018-01-17', 'nu': 56, 'sau': 9042}]

col = [{'name': u'\u65e5\u671f', 'id': 'logday'}, {'name': u'\u65f6\u6bb5', 'id': 'hour'}, {'name': u'DAU-\u5168\u90e8-qdxvivo', 'id': 'au'}, {'name': u'\u65b0\u589e\u6fc0\u6d3b-\u5168\u90e8-qdxvivo', 'id': 'nu'}, {'name': u'\u7d2f\u8ba1DAU-\u5168\u90e8-qdxvivo', 'id': 'sau'}, {'name': u'\u7d2f\u8ba1\u65b0\u589e\u6fc0\u6d3b-\u5168\u90e8-qdxvivo', 'id': 'snu'}]

df = pd.DataFrame(data)
print  df.columns

col1 = dict()
list = []
for dic in col:
    col1[dic["id"]] = dic["name"]
    list.append(dic["name"])
print col1
df.rename(columns=col1, inplace = True)

#print df

#
#df.to_csv("t.csv", index=False, encoding="utf_8_sig", columns=list)


data_2 = [{'名称':'注册','昨日': '00', '今日': 131, '相差比例': 5763},
        {'名称':'一元提现','昨日': '01', '今日': 187, '相差比例': 3279}]

df_2 = pd.DataFrame(data_2)
df_2.index.name= 'foo'
print df_2

pd.merge()