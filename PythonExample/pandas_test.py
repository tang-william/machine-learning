
import pandas as pd
import numpy as np
from util_lt import LT
df = pd.read_csv('kol_reten.csv', header=None, names=["channel", "day", "reten"]).sort(["channel","day"])

lt_dict = dict()
for (channel), group in df.groupby(['channel']):
        list_x = map(int, list(group['day']))
        list_y = map(float, list(group['reten']))
        for index, value in enumerate(list_y):
            if value == 0:
                list_y[index] = 0.00001
        if len(list_x) == len(list_y):
            x = np.asarray(list_x)
            y = np.asarray(list_y)
        try:
            res = LT(x, y, fitfunc='power').calc_lt()
        except Exception, Error:
            print "%s lt cal fail." % channel
        else:
            lt_dict[channel] = res['lt']
lt_df = pd.DataFrame(lt_dict.items(), columns=['channel', 'lt'])
lt_df.to_csv("lt.csv", index=False, header=None)



