from flask import Flask, render_template, jsonify, request
from icalendar import Calendar, Event
from datetime import datetime, date, time

import requests

app = Flask(__name__, template_folder='views')

@app.route('/')
def index():
    return render_template('index.html')

# Returns today's events in JSON format
@app.route('/todaysevents')
def todaysEvents():
	url = request.args.get('url')
	if url == None:
		return render_template('error.html')
	try:
		calendar = getCalendar(url)
	except ValueError, e:
		error = "Not a valid calendar"
		return render_template('error.html')
		return 
	events = {}
	# TODO: If the event is an all-day event with no start time, the event[].dt attribute will be a date attribute and thus have no .time() property.
	# Have to distinguish all-day events from specific-time events
	# OR just add the .dt property, then remove the date part later, leaving those with no .time() property as empty strings.
	for event in calendar.walk('VEVENT'):
		# dtstart.dt will return a date object and not a datetime object if the event is a full-day event.
		# Since a date object does not have a date() method, we have to check if which one it is, otherwise it fails.
		# Do this by, if the object is datetime, extract only the date
		startday = event['dtstart'].dt
		endday = event['dtstart'].dt
		if isinstance(startday, datetime):
			startday = startday.date()
		if isinstance(endday, datetime):
			endday = endday.date()

		if startday <= date.today() <= endday:
			events[event['summary']] = dict(start=str(event['dtstart'].dt.time()) if isinstance(event['dtstart'].dt, datetime) else "",
											end=str(event['dtend'].dt.time()) if isinstance(event['dtend'].dt, datetime) else "",
											location=event['location'],
											description=event['description'] )
	return jsonify(events)

# Fetches calendar from the given url and returns it as an icalendar object
def getCalendar(url):
	'''if __name__ == '__main__':
		url = 'https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics'
	'''
	response = requests.get(url)
	if response.status_code == 200:
		calendar = Calendar.from_ical(response.content)
		return calendar
	else:
		return Calendar.from_ical(response.content)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')