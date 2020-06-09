# -*- coding: utf-8 -*-

import pandas as pd

#Filtered out June data because month is not over, grouped by Month, Year, and isOnline, summed numAttendees over
#each month
df = pd.read_csv("example.csv")

df['startDate'] = pd.to_datetime(df['startAt'], unit='s')
df['endDate'] = pd.to_datetime(df['endAt'], unit='s')

by_month = df.loc[pd.to_datetime(ggdf['startAt'], unit='s') <= pd.to_datetime(1590953558, unit='s')]\
.set_index('startDate').groupby([pd.Grouper(freq="M"),'isOnline'])['numAttendees'].sum().reset_index()

print(by_month.head())
