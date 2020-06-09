# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
from datetime import datetime
from ratelimit import limits, sleep_and_retry

ONE_MINUTE=60

#Decorators to limit API calls. SmashGG says limit is 80 per minute, average. I limited it to 60 per minute.
@sleep_and_retry #If rate limit is reached, wait til end of period then try again
@limits(calls=60, period=ONE_MINUTE) #60 calls per minute
def gg_req(page, beforeDate, query):

    #Go to https://smashgg-developer-portal.netlify.app for documentation. They have a blog where\
    #you can post your projects
    url = 'https://api.smash.gg/gql/alpha'
    
    #Get token by making smashgg account
    token = #token goes here as string

    variables = {
      "page": page, #Results divided into pages, this is which page you want
      "beforeDate": beforeDate #Only returns data with startAt before this Unix Timestamp
    }

    myobject = {
      "query": query, #Your graphql query as a string
        "variables": variables
    }

    #You can use software to make your requests like Postman. Need your token to be in the
    #Authorization header of your request
    response = requests.post(url, json = myobject, headers = {"Authorization": "Bearer {}".format(token)})

    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    return response

#Each response comes back in json, this is to a list of them into a pandas dataframe
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
    for resp in rlist:
        parsed = json.loads(resp.text)
        #On graphql error, response will have 'error' instead of 'data
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

#smashgg has a rate limit. 80 requests per minute average. 1000 objects per request. I limited my api calls to 60/ minute but
#still got stopped. Seems like the api stops you when you get to 10000 objects in some unknown timeframe, 
#so future work is to convert this into a crawler that runs periodically once I get more info from devs
                
page = 1
beforeDate = 1589932800

loop = True
while loop:
       
    og_count = len(df.index) #Starting size of dataframe each loop
    
    rlist = []
    badpages = []
    
    while page <= 200:
        try:
            rlist.append(gg_req(page,beforeDate,query))  
        except Exception as e:
            print("Exception: ",e,"Page: ",page)
            badpages.append(page)
            
        page +=1
    
    df = pd.concat([ df, tour_parser(rlist)])
    
    new_count = len(df.index) #Size of dataframe at end of loop
    
    #Stop looping if more rows aren't added. Can add counter here to let it try more times before quitting.
    if og_count == new_count:
        loop = False
       
   
#Add startDate and endDate columns for analysis
#Then add data to csv
startDate = df['startAt'].map(lambda val: datetime.utcfromtimestamp(int(val)).strftime('%m-%d-%Y')).rename("startDate")
endDate = df['endAt'].map(lambda val: datetime.utcfromtimestamp(int(val)).strftime('%m-%d-%Y')).rename("endDate")

newdf = pd.concat([df, startDate, endDate], axis = 1)

#Had to save several csvs due to rate limit interruptions. Concatenated them for my analysis. Here's an example
newdf.to_csv("example.csv")

