# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Retrieve calendar events to produce meeting statistics.

A detailed description of this module.
"""

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import csv
import pytz
from datetime import datetime, timedelta
from collections import Counter


try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('--user', '-u', '-U', help="User. Default is you.")
    parser.add_argument('--csv', '-c', '-C', help="Generate a csv file")
    flags = parser.parse_args()
except ImportError:
    flags = None


# helper function to sum elements in a list
def listsum(numList):
    theSum = 0
    for i in numList:
        theSum = theSum + i
    return theSum


def main():

    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        # If you're browsing this code you'll need to download the client secret file
        # from cloud.google.com/console/your_project
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)

    pacific = pytz.timezone('America/Los_Angeles')
    now = datetime.now(tz=pacific)
    now_minus_thirtydays = now - timedelta(days=30)

    # This example uses the primary value as this is your personal calendar
    # You can use any calendar you want, however
    # The calendar ID is under settings in the web UI
    # calendarId = 'google.com_somecomplicatedstring@group.calendar.google.com'

    # Personal Calendar ID
    if flags.user:
        user = flags.user
    else:
        #user = 'google.com_726f6f6d5f75735f6b69725f367468625f315f313334@resource.calendar.google.com'
        user = 'google.com_dpk94f0p96vmhe7nn7kdnanb48group.calendar.google.com'

    calendarId = user

    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Use the service to get the events from the
    # AUTHENTICATED user's calendar
    events = service.events().list(
        calendarId=calendarId,
        singleEvents=True,
        orderBy='startTime',
        timeMin=now_minus_thirtydays.strftime('%Y-%m-%dT%H:%M:%S-00:00'),
        timeMax=now.strftime('%Y-%m-%dT%H:%M:%S-00:00')).execute()

    """
    If you want to list all day events you will need to use the 'date' key but
    if you want to list individual events you'll have to use the 'dateTime' key.
    """

    # initialize lists that will get populated below
    # lists are used to sum and create a csv below
    # initialize a list to collect all start times
    start = []
    # initialize a list to collect all end times
    end = []
    # initialize a list that will be used to sum duration in seconds
    total_duration = []
    # initialize a list to sum the number of events and to create a csv
    events_list = []
    # list to collect duration of each event
    dur = []
    # list to collect duration of each event in seconds
    dur_s = []

    while True:
        for event in events['items']:
            try:
                if 'dateTime' in event['start']:
                    # not every event has a summary
                    # to avoid a key error use the get method
                    e = event.get('summary', [])
                    # populate list in order to count total list items
                    events_list.append(e)
                    e_start = event['start']['dateTime']
                    start.append(e_start)
                    e_end = event['end']['dateTime']
                    end.append(e_end)
                    # delete UTC offset
                    e_start_format = datetime.strptime(
                        e_start[:-6], '%Y-%m-%dT%H:%M:%S')
                    e_end_format = datetime.strptime(
                        e_end[:-6], '%Y-%m-%dT%H:%M:%S')
                    duration = e_end_format - e_start_format
                    dur.append(duration)
                    duration_s = duration.total_seconds()
                    dur_s.append(duration_s)
                    # populate list in order to count total duration seconds
                    # below
                    total_duration.append(int(duration_s))
                    print('Event: ', e)
                    print('Start Time: ', e_start_format)
                    print('End Time: ', e_end_format)
                    print('Duration: ', duration)
                    print('Duration: ', duration_s)

                elif 'date' in event['start']:
                    e_start = event['start']['date']
                    e_end = event['end']['date']
                    # not every event has a summary
                    # to avoid a key error use the get method
                    e = event.get('summary', [])
                    e_start_format = datetime.strptime(e_start, '%Y-%m-%d')
                    e_end_format = datetime.strptime(e_end, '%Y-%m-%d')
                    duration = e_end_format - e_start_format
            except:
                print('failed')

        else:
            break

if __name__ == '__main__':
    main()
