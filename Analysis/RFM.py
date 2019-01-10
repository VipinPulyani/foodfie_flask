import pymysql
import config
import numpy as np
import pandas as pd
import datetime as dt
from Misc.foodfie_db.db import connectDB

SQL = 'Select * from foodfie.Order'
db_connect = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)

NOW = dt.datetime.now()
df1 = pd.read_sql(SQL, db_connect)
rfmTable = df1.groupby('CustomerId').agg({'TotalAmount': np.sum, 'OrderTime': lambda x: (NOW - x.max()).days, 'CustomerId':np.count_nonzero})
rfmTable.rename(columns={'OrderTime':'LastVisited',
                         'CustomerId': 'TotalVisit',
                        }, inplace = True)
#rfmTable.columns = ['LastVisited', 'Frequency','TotalAmount']
print(rfmTable.head())
quantiles = rfmTable.quantile(q=[0.25, 0.5, 0.75])
quantiles = quantiles.to_dict()

segmented_rfm = rfmTable

def RScore(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]:
        return 3
    else:
        return 4

def FMScore(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]:
        return 2
    else:
        return 1

segmented_rfm['r_quartile'] = segmented_rfm['LastVisited'].apply(RScore, args=('LastVisited',quantiles,))
segmented_rfm['f_quartile'] = segmented_rfm['TotalVisit'].apply(FMScore, args=('TotalVisit',quantiles,))
segmented_rfm['m_quartile'] = segmented_rfm['TotalAmount'].apply(FMScore, args=('TotalAmount',quantiles,))

print(segmented_rfm.head())

segmented_rfm['RFMScore'] = segmented_rfm.r_quartile.map(str) + segmented_rfm.f_quartile.map(str)  \
                            + segmented_rfm.m_quartile.map(str)

conn, curs = connectDB()
for index, item in segmented_rfm[segmented_rfm['RFMScore'] <= '444'].sort_values('TotalAmount', ascending=False).iterrows():
    SQL = """INSERT INTO foodfie_analysis.RFM(CustomerId, Frequency, Recently, Monetary, R, F, M, RFMScore)
             VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, '{7}')
            """.format(int(index), int(item['TotalVisit']), int(item['LastVisited']), int(item['TotalAmount']),
                       int(item['r_quartile']), int(item['f_quartile']), int(item['m_quartile']), str(item['RFMScore']))
    curs.execute(SQL)
    conn.commit()



# """Get set go to take "MOMOS BEYOND MOMOS" with Foodfie!!! The much awaited Momos food festival, MOMOIESTA 2018 has kickstarted around you. The week long fest promises to be delightful for the momos lovers.Come and pamper your tastebuds.
# Highlight of event:
# Pasta momos</br>Momos 65</br>Momos chaat</br>Oreo momos</br>Chocolate momos</br>Cheese and Corn</br>Burger momos</br>Kurkure momos</br> Gravy momos</br>Afghai momos to steamed momos</br>there will be all sorts of striking fusion momos.
#
# Venue: Foodfie Candor Infospace and Infotch
# Date: 9th April 2018 to 13th April 2018."""
