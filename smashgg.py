# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
from datetime import datetime
import time

def gg_reqs(page, beforeDate, query, rnum):

    #Go to https://smashgg-developer-portal.netlify.app for documentation. They have a blog where\
    #you can post your projects
    url = 'https://api.smash.gg/gql/alpha'
    
    #Get token by making smashgg account
    token = #token goes here as string
    
    rlist = []

    #Each run of this loop makes 1 request, need to set gql variables here so you can iterate
    tracker = 0
    while tracker < rnum:#rnum is number of request you want to make per run
        variables = {
          "page": page, #page returned by query
          "beforeDate": beforeDate #Unix Timestamp
        }

        myobject = {
          "query": query,#graphql query as string
            "variables": variables
        }

        #Need your token to be in the Authorization header of your request
        rlist.append(requests.post(url, json = myobject, headers = {"Authorization": "Bearer {}".format(token)}))
        page += 1
        tracker += 1

    #returns page for tracking progress, and rlist is a list of responses
    return page, rlist

#Each response comes back in json, this is to convert it into a pandas dataframe
def tour_parser(rlist):

    #column names for the dataframe
    tour = {'name': [],
     'slug': [],
     'shortSlug': [],
     'numAttendees': [],
     'startAt': [],
     'endAt': [],
     'countryCode': [],
     'currency': [],
     'hasOfflineEvents': [],
     'hasOnlineEvents': [],
     'isOnline': [],
     'gamenames': [],
     'timezone': [],
     'rules': [],
     'venueName': []}

    #I just pulled each object directly; If query returns nothing objects come back as None
    for req in rlist:
        parsed = json.loads(req.text)
        #On error, response will have 'error' instead of 'data
        if 'data' in parsed and parsed['data'] is not None and parsed['data']['tournaments'] is not None\
        and parsed['data']['tournaments']['nodes'] is not None:
            for node in parsed['data']['tournaments']['nodes']:
                #I wanted to loop through each key, value, but I ran into errors
                #if you find a solution, let me know
                tour['name'].append(node['name'])
                tour['slug'].append(node['slug'])
                tour['shortSlug'].append(node['shortSlug'])
                tour['numAttendees'].append(node['numAttendees'])
                tour['startAt'].append(str(node['startAt']))
                tour['endAt'].append(str(node['endAt']))
                tour['countryCode'].append(node['countryCode'])
                tour['currency'].append(node['currency'])
                tour['hasOfflineEvents'].append(node['hasOfflineEvents'])
                tour['hasOnlineEvents'].append(node['hasOnlineEvents'])
                tour['isOnline'].append(node['isOnline'])
                if node['events']:
                    tour['gamenames'].append(json.dumps(node['events']))
                else:
                    tour['gamenames'].append(None)
                tour['timezone'].append(node['timezone'])
                tour['rules'].append(node['rules'])
                tour['venueName'].append(node['venueName'])

    tourf = pd.DataFrame(tour)
    
    
    return tourf

#Put your graphql query here as a string
query = """
        query TournamentsByVideogame ($page: Int!, $beforeDate: Timestamp) {
          tournaments(query: {
            perPage: 100
            page: $page
            sortBy: "startAt desc"
            filter: {
              beforeDate: $beforeDate,
              afterDate: 1543622400,
                    }
          }) {
            nodes {

                name
                slug
                shortSlug
                numAttendees
                startAt
                endAt
                countryCode
                currency
                hasOfflineEvents
                hasOnlineEvents
                isOnline
                events {
                  videogame {name}
                }
                timezone
                rules
                venueName

            }
          }
        }
"""

#Made an empty dataframe so my while loop could be simpler
df =  pd.DataFrame({'name': [],
     'slug': [],
     'shortSlug': [],
     'numAttendees': [],
     'startAt': [],
     'endAt': [],
     'countryCode': [],
     'currency': [],
     'hasOfflineEvents': [],
     'hasOnlineEvents': [],
     'isOnline': [],
     'gamenames': [],
     'timezone': [],
     'rules': [],
     'venueName': []})

#smashgg has a rate limit. 80 requests per minute average. 1000 objects per request. I had trouble finding a solution
#to limit my requests to the rate automatically, so I tweaked these variables to avoid hitting it.
#Still never found a solution. Seems like the api stops you when you get to 10000 objects in some unknown timeframe, 
#so future work is to convert this into a crawler that runs periodically once I get more info from devs
page = 1
beforeDate = 1589932800
#beforeDate = 1545435000
rnum = 50

loop = True
while loop:
       
    og_count = len(df.index)
        
    page, rlist = gg_reqs(page, beforeDate, query, rnum)
    df = pd.concat([ df, tour_parser(rlist)])
    
    new_count = len(df.index)
    
    #Stop looping if more rows aren't added. At that point I would check if I hit the rate limit.
    if og_count == new_count:
        loop = False
        
    time.sleep(120)

     
    #beforeDate = int(df['startAt'].sort_values().iloc[0])
    
#Add startDate and endDate columns for analysis
#Then add data to csv
startDate = df['startAt'].map(lambda val: datetime.utcfromtimestamp(int(val)).strftime('%m-%d-%Y')).rename("startDate")
endDate = df['endAt'].map(lambda val: datetime.utcfromtimestamp(int(val)).strftime('%m-%d-%Y')).rename("endDate")

newdf = pd.concat([df, startDate, endDate], axis = 1)

#Had to save several csvs due to rate limit interruptions. Concatenated them for my analysis. Here's an example
newdf.to_csv("example.csv")

