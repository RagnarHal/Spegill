from flask import Flask, render_template, jsonify
from icalendar import Calendar, Event
from datetime import datetime, date

import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Returns today's events in JSON format
@app.route('/todaysevents')
def todaysEvents(url=None):
	calendar = getCalendar(url)
	events = {}
	# TODO: If the event is an all-day event with no start time, the event[].dt attribute will be a date attribute and thus have no .time() property.
	# Have to distinguish all-day events from specific-time events
	# OR just add the .dt property, then remove the date part later, leaving those with no .time() property as empty strings.
	for event in calendar.walk('VEVENT'):
		if event['dtstart'].dt.date() <= date.today() <= event['dtend'].dt.date():
			events[event['summary']] = dict(start=str(event['dtstart'].dt.time()),
											end=str(event['dtend'].dt.time()),
											location=event['location'],
											description=event['description'] )

	# Sort the dictionary with the timeless events at the top, then by ascending start time order
	return jsonify(events)

# Fetches calendar from the given url and returns it as an icalendar object
def getCalendar(url):
	if __name__ == '__main__':
		url = 'https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics'
	
	response = requests.get(url)
	# TODO: Add status code check and error handling
	return Calendar.from_ical(response.content)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')