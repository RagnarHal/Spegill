# -*- coding: utf-8 -*-
import flask
import icalendar
import datetime
import requests
import json
from ConfigParser import NoSectionError, NoOptionError
from mirror import app
from mirror import logger
from mirror import settings

@app.route('/')
def index():
	logger.debug("Received call to Index controller from " + str(flask.request.remote_addr))
	return flask.render_template('index.html')

# Returns today's events in JSON format as a list of events
@app.route('/events')
def get_events():
	logger.debug("Received call to Events controller from " + str(flask.request.remote_addr))

	# TODO: Move try/catch block out of controllers.py; doesn't belong here.
	try:
		url = settings.get('calendar', 'url')
		debug = settings.getboolean('app', 'debug')
	except (NoSectionError, NoOptionError, ValueError) as e:
		logger.warning("Config parser raised error: {0}. Please check settings.cfg.".format(e.message))
		flask.abort(500, "Server config file is not valid. Cannot process request. See log for further info.")

	logger.debug("URL parsed from config file: " + str(url))
	logger.debug("DEBUG parsed from config file: " + str(debug))

	if debug:
		calendar = fetch_calendar_mock()
	else:
		calendar = fetch_calendar(url)

	events = []
	for event in calendar.walk('VEVENT'):
		start_datetime = event['dtstart'].dt
		end_datetime = event['dtend'].dt
		try:
			location = event['location']
		except KeyError:
			# For some reason, the Google Calendar API does not include the LOCATION key on certain calendars (e.g. Holidays), thus raising a KeyError
			# when trying to retrieve the location from the calendar. So we must catch the error and assign the value an empty string if raised.
			location = ""
			
		# event['dtstart'].dt and event['dtend'].dt will return a date object and not a datetime object if the event is a full-day event.
		# Since a date object does not have a date() method, calling date() on an all-day event will fail.
		if isinstance(start_datetime, datetime.datetime):
			start_date = start_datetime.date()
		else:
			start_date = start_datetime

		if datetime.date.today() <= start_date:
			events.append({	'summary' : event['summary'],
							'description' : event['description'],
							'location' : location,
							'start' : str(start_datetime),
							'end' : str(end_datetime)})
	logger.info("Calendar request succeeded and yielded {0} events".format(len(events)))
	return flask.jsonify(results=events)

@app.route('/weather')
def get_weather_current():
	logger.debug("Received call to Current Weather controller from " + str(flask.request.remote_addr))

	# TODO: Move try/catch block out of controllers.py; doesn't belong here.
	try:
		url = settings.get('weather', 'weather')
		debug = settings.getboolean('app', 'debug')
	except (NoSectionError, NoOptionError, ValueError) as e:
		logger.warning("Config parser raised error: {0}. Please check settings.cfg.".format(e.message))
		flask.abort(500, "Server config file is not valid. Cannot process request. See log for further info.")

	logger.debug("URL parsed from config file: " + str(url))
	logger.debug("DEBUG parsed from config file: " + str(debug))

	if debug:
		weather = fetch_weather_current_mock()
	else:
		weather = fetch_weather(url)

	try:
		result = {
			"city" : weather['name'],
			"country" : weather['sys']['country'],
			# Use ISO 8601 standard for representing datetime as string, instead of the unix timestamp returned by OpenWeatherAPI
			# TODO: Handle case where API returns correct format, or different formats.
			"time" : datetime.datetime.fromtimestamp(int(weather['dt'])).strftime('%Y-%m-%d %H:%M:%S'),
			"weather" : weather['weather'],
		    "wind" : weather['wind'],
		    "cloudpercent" : weather['clouds']['all'],
		    "temp" : {
		    	"current" : weather['main']['temp'],
		    	"max" : weather['main']['temp_max'],
		    	"min" : weather['main']['temp_min']
		    },
		    "sun" : {
		    	"rise" : weather['sys']['sunrise'],
		    	"set" : weather['sys']['sunset']
		    }
		}
	except KeyError as e:
		logger.error("KeyError received on key {0}".format(e.message))
		flask.abort(400, "KeyError received on key '{0}'. This probably happened because the structure of the API response is different than expected.".format(e.message))

	return flask.jsonify(result)

@app.route('/forecast')
def get_weather_forecast():
	logger.debug("Received call to Forecast Weather controller from " + str(flask.request.remote_addr))

	try:
		url = settings.get('weather', 'forecast')
		debug = settings.getboolean('app', 'debug')
	except (NoSectionError, NoOptionError, ValueError) as e:
		logger.warning("Config parser raised error: {0}. Please check settings.cfg.".format(e.message))
		flask.abort(500, "Server config file is not valid. Cannot process request. See log for further info.")

	logger.debug("URL parsed from config file: " + str(url))
	logger.debug("DEBUG parsed from config file: " + str(debug))

	if debug:
		weather = fetch_weather_forecast_mock()
	else:
		weather = fetch_weather(url)

	try:
		result = {
			"city" : weather['city']['name'],
			"country" : weather['city']['country'],
			"forecasts" : [	{ 
				# Use ISO 8601 standard for representing datetime as string, instead of the unix timestamp returned by OpenWeatherAPI
				# TODO: Handle case where API returns correct format, or different formats.
				"time" : datetime.datetime.fromtimestamp(int(forecast['dt'])).strftime('%Y-%m-%d %H:%M:%S'),
				"cloudpercent" : forecast['clouds'],
				"weather" : forecast['weather'],
				"wind" : forecast['wind'],
				"temp" : {
					"current" : forecast['main']['temp'],
					"max" : forecast['main']['temp_max'],
					"min" : forecast['main']['temp_min'],
				}
			} for forecast in weather['list']]
		}
	except KeyError as e:
		logger.error("KeyError received on key {0}".format(e.message))
		flask.abort(400, "KeyError received on key '{0}'. This probably happened because the structure of the API response is different than expected.".format(e.message))

	return flask.jsonify(result)

@app.route('/holidays')
def get_holidays():
	logger.debug("Received call to Holidays controller from " + str(flask.request.remote_addr))

	with open(settings.get('calendar', 'holidays')) as f:
		calendar = icalendar.Calendar.from_ical(f.read())

	events = []
	for event in calendar.walk('VEVENT'):
		if datetime.date.today() <= event['dtstart'].dt:
			events.append({	'summary' : event['summary'],
							'start' : str(event['dtstart'].dt),
							'end' : str(event['dtend'].dt)})

	logger.info("Holiday request succeeded and yielded {0} holidays".format(len(events)))
	return flask.jsonify(results=events)

def fetch_calendar_mock():
	logger.debug("Fetching mock calendar data")

	with open(settings.get('mock', 'calendar')) as f:
		return icalendar.Calendar.from_ical(f.read())

def fetch_calendar(url):
	logger.debug("Fetching real calendar data")

	if url is None:
		logger.warning("No URL parameter supplied for calendar API, aborting request")
		flask.abort(400, "No URL parameter supplied")

	try:
		response = requests.get(url)
	except requests.exceptions.MissingSchema as e:
		logger.error("Exception {0} caught while trying to GET calendar. Message: {1}".format(e.__class__, e.message))
		flask.abort(400, e.message)

	try:
		calendar = icalendar.Calendar.from_ical(response.content)
	except ValueError as e:
		logger.error("Parsing API response failed. Request to external calendar API did not provide a valid iCalendar format.")
		flask.abort(400, "Not a valid ical calendar.")

	return calendar

def fetch_weather_current_mock():
	logger.debug("Fetching mock data for current weather")

	with open(settings.get('mock', 'weather')) as f:
		return json.load(f)

def fetch_weather_forecast_mock():
	logger.debug("Fetching mock data for forecast weather")

	with open(settings.get('mock', 'forecast')) as f:
		return json.load(f)

def fetch_weather(url):
	logger.debug("Fetching real weather data")

	try:
		response = requests.get(url)
	except requests.exceptions.MissingSchema as e:
		logger.error("Exception {0} caught while trying to GET current weather. Message: {1}".format(e.__class__, e.message))
		flask.abort(400, e.message)

	try:
		weather = json.loads(response.content)
	except ValueError as e:
		logger.error("Exception {0} caught while trying to parse JSON for current weather. Message: {1}. Data: {2}".format(e.__class__, e.message, str(weather_json)))
		flask.abort(400, e.message)

	return weather

@app.errorhandler(404)
def not_found(e):
	logger.warning("404 error encountered. Message: {0}".format(e.description))
	resp = flask.make_response(e.description, 404)
	return resp

@app.errorhandler(500)
def server_error(e):
	logger.warning("500 error encountered. Message: {0}".format(e.description))
	resp = flask.make_response(e.description, 500)
	return resp