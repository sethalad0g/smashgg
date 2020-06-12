# smashgg
scrape_tocsv.py is an example of how to scrape data from smashgg's graphql api. You will need to get an API token from https://smash.gg/ to use their API.

The API is in Alpha, so this script might not work in the future.

----What this script does-----

Calls SmashGG API to get data about all Tournaments between May 31, 2020 and December 1st, 2018. Grabbed the following fields for now:

name - Tournament Name

slug - Tournament slug, which is used to identify it in SmashGG and build urls

shortSlug - Tournament shortSlug, which is used to identify it in SmashGG and build short urls

numAttendees - Number of peope who signed up to attend tournament

startAt - Start Unix Timestamp

endAt - End Unix Timestamp

countryCode - Which currency

currency - Currency used, such as USD

hasOfflineEvents - Whether Tournament has offline events

hasOnlineEvents - Whether Tournament has online events

isOnline - Whether Tournament is online

gamenames - List of games played in tournament, in list of dictionaries for now

timezone - Timezone of tournament

rules - Rules of Tournament

venueName - Name of Venue

startDate - MM/DD/YYYY date converted from startAt by me

endDate - MM/DD/YYYY date converted from endAt by me

----Other Included Files----

attendeesbymonth.py - Shows how I transformed the data for preliminary analysis and plotted in Seaborn.
requirements.txt - List of required Python modules.
vizurl.txt - Tableau visualization of transformed data.

----Future Work----

Convert script to crawler that avoids encountered hard limit.
Expand query or add more queries to perform analysis on SmashGG data.
