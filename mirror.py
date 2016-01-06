# -*- coding: utf-8 -*-

import flask
import icalendar
import datetime
import requests
import json

app = flask.Flask(__name__, template_folder='views')

@app.route('/')
def index():
    return flask.render_template('index.html')

# Returns today's events in JSON format as a list of events
@app.route('/events')
def get_events():
	# Get the URL parameter from the client and attempt to GET it.
	url = flask.request.args.get('url')
	# TODO: Error logging
	try:
		response = requests.get(url)
	except requests.exceptions.MissingSchema:
		flask.abort(400, "No URL schema supplied. Perhaps you meant http://" + url + "?")
	# Attempt to parse the result into an icalendar object.
	try:
		calendar = icalendar.Calendar.from_ical(response.content)
	except ValueError:
		flask.abort(400, "Not a valid ical calendar.")

	events = []
	for event in calendar.walk('VEVENT'):
		# dtstart.dt will return a date object and not a datetime object if the event is a full-day event.
		# Since a date object does not have a date() method, calling date() on an all-day event will fail.
		start_day = event['dtstart'].dt.date() if isinstance(event['dtstart'].dt, datetime.datetime) else event['dtstart'].dt
		end_day = event['dtend'].dt.date() if isinstance(event['dtend'].dt, datetime.datetime) else event['dtend'].dt
		start_time = event['dtstart'].dt.time() if isinstance(event['dtstart'].dt, datetime.datetime) else ""
		end_time = event['dtend'].dt.time() if isinstance(event['dtend'].dt, datetime.datetime) else ""

		today = datetime.date.today()

		if today <= start_day:
			events.append({	'summary' : event['summary'],
							'description' : event['description'],
							'location' : event['location'],
							'start_day' : str(start_day),
							'end_day' : str(end_day),
							'start_time' : str(start_time),
							'end_time' : str(end_time),
							'is_today' : 1 if start_day == today else 0})

	return flask.jsonify(results=events)

@app.route('/weather')
def get_weather():
	#url = flask.request.args.get('url')
	#response = requests.get(url)
	# For now, just return the json string straight up to the client.
	# Later, maybe filter out useless information
	d = '{"coord":{"lon":-21.86,"lat":64.12},"weather":[{"id":800,"main":"Clear","description":"Sky is Clear","icon":"01n"}],"base":"stations","main":{"temp":273.15,"pressure":996,"humidity":85,"temp_min":273.15,"temp_max":273.15},"visibility":10000,"wind":{"speed":7.2,"deg":70},"clouds":{"all":0},"dt":1452029400,"sys":{"type":1,"id":4832,"message":0.0316,"country":"IS","sunrise":1451992382,"sunset":1452009206},"id":6692263,"name":"Reykjavik","cod":200}'
	
	return flask.jsonify(results=json.loads(d))

@app.errorhandler(404)
def not_found(e):
	resp = flask.make_response(e.description, 404)
	return resp

@app.errorhandler(500)
def server_error(e):
	resp = flask.make_response(e.description, 500)
	return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')