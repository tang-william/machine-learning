

from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *

from sqlalchemy.sql import text

# Hive
engine = create_engine('hive://192.168.10.12:10010/ltv')

sql = text("select * from ltv.rac_grant_credit limit 10")

sql_rst = engine.execute(sql).fetchall()

print sql_rst


