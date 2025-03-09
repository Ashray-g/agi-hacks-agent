from icalevents.icalevents import events
from datetime import datetime, timedelta
import json

url = "webcal://p179-caldav.icloud.com/published/2/MjA0Mzc1NzQxNDcyMDQzN0fNYht_gMSe657HCOk5kNoJGoSGy6u-Zu8ybYtWxKLNcNyoDlQPesdUsE7B-wnfiX6E4tL07R9jMNIM3IlFE-c"


# get all events from now to one year in the future
start_date = datetime.now()
end_date = start_date + timedelta(days=365)

# get events with apple fix for icloud calendars
es = events(url=url, start=start_date, end=end_date, fix_apple=True)

# create a list to store event dictionaries
events_list = []

# process all events
print(f"found {len(es)} events:")
for event in es:
    # create a dictionary for each event
    event_dict = {
        'title': event.summary,
        'description': event.description,
        'location': event.location,
        'start': event.start.isoformat() if event.start else None,
        'end': event.end.isoformat() if event.end else None,
        'all_day': event.all_day if hasattr(event, 'all_day') else False,
        'attendees': [],
        'categories': [],
        'status': None,
        'organizer': "None",
        'source': 'ical'
    }
    
    # add event to the list
    events_list.append(event_dict)

# sort events by start date and time
events_list.sort(key=lambda x: x['start'] if x['start'] is not None else '')

# save events to json file
with open("shadow-events.json", "w") as json_file:
    json.dump(events_list, json_file, indent=4)

print("events saved to shadow-events.json")

