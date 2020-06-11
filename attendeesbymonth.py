# -*- coding: utf-8 -*-

import pandas as pd
pd.plotting.register_matplotlib_converters()
import matplotlib.pyplot as plt
import seaborn as sns
print("Setup Complete")


#Filtered out June data because month is not over, grouped by Month, Year, and isOnline, summed numAttendees over
#each month
df = pd.read_csv("example.csv")

df['startDate'] = pd.to_datetime(df['startAt'], unit='s')
df['endDate'] = pd.to_datetime(df['endAt'], unit='s')

by_month = df.loc[pd.to_datetime(df['startAt'], unit='s') <= pd.to_datetime(1590953558, unit='s')]\
.set_index('startDate').groupby([pd.Grouper(freq="M"),'isOnline'])['numAttendees'].sum().reset_index()

offendees = by_month.query('isOnline == 0')['numAttendees'].rename("offlineAttendees")
onendees = by_month.query('isOnline == 1')['numAttendees'].rename("onlineAttendees")

joined_df = by_month.join(offendees, how='left').join(onendees, how='left')

plot_df = joined_df.set_index('startDate').groupby([pd.Grouper(freq="M")])['numAttendees','offlineAttendees','onlineAttendees'].sum()


fig, ax = plt.subplots(figsize = (12,6)) 
fig = sns.lineplot(data = plot_df, ax=ax)
plt.xlabel("Tournament Start Date")
plt.ylabel("Sum of Attendees per Month")
plt.title("Attendees at SmashGG Tournaments Over Time")