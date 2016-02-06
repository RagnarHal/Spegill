# -*- coding: utf-8 -*-
import json
import datetime
from ConfigParser import NoSectionError, NoOptionError

import flask
import icalendar
import requests

from mirror import app
from mirror import logger
from mirror import settings

@app.route('/')
def index():
	logger.debug("Received call to Index controller from {0}".format(str(flask.request.remote_addr)))
	return flask.render_template('index.html')

@app.route('/events')
def get_events():
	logger.debug("Received call to Events controller from {0}".format(str(flask.request.remote_addr)))

	calendar = fetch_calendar('events')
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
			events.append(
				{   'summary' : event['summary'],
					'description' : event['description'],
					'location' : location,
					'start' : str(start_datetime),
					'end' : str(end_datetime)})
	logger.info("Calendar request succeeded and yielded {0} events".format(len(events)))
	return flask.jsonify(results=events)

@app.route('/holidays')
def get_holidays():
	logger.debug("Received call to Holidays controller from {0}".format(str(flask.request.remote_addr)))

	if settings.getboolean('calendar', 'hide_holidays'):
		return flask.jsonify(results=[])

	calendar = fetch_calendar('holidays')
	events = []
	for event in calendar.walk('VEVENT'):
		if datetime.date.today() <= event['dtstart'].dt:
			events.append({	'summary' : event['summary'],
							'start' : str(event['dtstart'].dt),
							'end' : str(event['dtend'].dt)})

	logger.info("Holiday request succeeded and yielded {0} holidays".format(len(events)))
	return flask.jsonify(results=events)


@app.route('/weather')
def get_weather_current():
	logger.debug("Received call to Current Weather controller from {0}".format(str(flask.request.remote_addr)))

	weather = fetch_weather('weather')
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
	logger.debug("Received call to Forecast Weather controller from {0}".format(str(flask.request.remote_addr)))

	weather = fetch_weather('forecast')
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

def fetch_calendar(token):
	logger.debug("Fetching calendar data for token '{0}'".format(str(token)))

	url = settings.get('mock', token) \
		if settings.getboolean('app', 'debug') and settings.has_section('mock') \
		else settings.get('calendar', token)

	logger.debug("CALENDAR - URL fetched for calendar data was '{0}'".format(str(url)))

	if url.startswith('http'):
		logger.debug("CALENDAR - URL '{0}' has http, attempting http request".format(str(url)))
		try:
			calendar = icalendar.Calendar.from_ical(requests.get(url).content)
		except (requests.exceptions.MissingSchema, ValueError) as e:
			# icalendar throws ValueError on invalid ical format
			logger.error("Exception {0} caught while trying to fetch calendar. Message: {1}".format(e.__class__, e.message))
			flask.abort(400, e.message)
	else:
		logger.debug("CALENDAR - URL '{0}' had no http, attempting to open file".format(str(url)))
		try:
			with open(url, 'rb') as f:
				calendar = icalendar.Calendar.from_ical(f.read())
		except IOError as e:
			logger.error("Exception {0} caught while trying to fetch calendar. Message: {1}".format(e.__class__, e.message))
			flask.abort(500, e.message)

	return calendar

def fetch_weather(token):
	logger.debug("Fetching weather data for token '{0}'".format(str(token)))
	url = settings.get('mock', token) \
		if settings.getboolean('app', 'debug') and settings.has_section('mock') \
		else settings.get('weather', token)

	logger.debug("WEATHER - URL fetched for weather data was '{0}'".format(str(url)))

	if url.startswith('http'):
		logger.debug("WEATHER - URL '{0}' has http, attempting http request".format(str(url)))
		try:
			weather = json.loads(requests.get(url).content)
		except (requests.exceptions.missingSchema, ValueError) as e:
			# json.loads throws ValueError on invalid json string
			logger.error("Exception {0} caught while trying to fetch weather. Message: {1}".format(e.__class__, e.message))
			flask.abort(400, e.message)
	else:
		logger.debug("WEATHER - URL '{0}' had no http, attempting to open file".format(str(url)))
		try:
			with open(url, 'rb') as f:
				weather = json.load(f)
		except IOError as e:
			logger.error("Exception {0} caught while trying to fetch weather. Message: {1}".format(e.__class__, e.message))
			flask.abort(500, e.message)

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