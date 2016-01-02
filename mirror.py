# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request
from icalendar import Calendar, Event
from datetime import datetime, date, time, timedelta
import requests

app = Flask(__name__, template_folder='views')

@app.route('/')
def index():
    return render_template('index.html')

# Returns today's events in JSON format as a list of events
@app.route('/getevents')
def getEvents():
	url = request.args.get('url')
	# TODO: Ew, this is ugly. Find a better way to catch parameter error
	if url == None:
		return render_template('error.html')
	try:
		calendar = getCalendar(url)
	except ValueError, e:
		return render_template('error.html')

	events = []
	for event in calendar.walk('VEVENT'):
		# dtstart.dt will return a date object and not a datetime object if the event is a full-day event.
		# Since a date object does not have a date() method, calling date() on an all-day event will fail.
		start_day = event['dtstart'].dt.date() if isinstance(event['dtstart'].dt, datetime) else event['dtstart'].dt
		end_day = event['dtend'].dt.date() if isinstance(event['dtend'].dt, datetime) else event['dtend'].dt
		start_time = event['dtstart'].dt.time() if isinstance(event['dtstart'].dt, datetime) else ""
		end_time = event['dtend'].dt.time() if isinstance(event['dtend'].dt, datetime) else ""

		today = date.today()

		if today <= start_day:
			events.append({	'summary' : event['summary'],
							'description' : event['description'],
							'location' : event['location'],
							'start_day' : str(start_day),
							'end_day' : str(end_day),
							'start_time' : str(start_time),
							'end_time' : str(end_time),
							'is_today' : 1 if start_day == today else 0})

	return jsonify(results=events)

# Fetches calendar from the given url and returns it as an icalendar object
def getCalendar(url):
	# TODO: Error handling: What if the response status is not 200?
	response = requests.get(url)
	if response.status_code == 200:
		calendar = Calendar.from_ical(response.content)
		return calendar
	else:
		return Calendar.from_ical(response.content)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')