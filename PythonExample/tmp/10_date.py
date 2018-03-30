
import datetime


today = datetime.date.today()
begin = (today - datetime.timedelta(days=45)).strftime("%Y%m%d")
end = (today - datetime.timedelta(days=15)).strftime("%Y%m%d")


print begin
print end

lt_dict = dict()

lt_dict['a'] = 'b'
lt_dict['b'] = 'c'

print lt_dict
print lt_dict.items()

import numpy as np

print np.log(0.00001)