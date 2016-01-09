# -*- coding: utf-8 -*-
import os
import logging
import logging.config
import flask
import icalendar
import datetime
import requests
import json

# Checking if logs folder exists
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_path):
	os.makedirs(log_path)

# Checking for logger config files
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'loggers.json')
if os.path.exists(config_path):
	with open(config_path, 'rt') as f:
		config = json.load(f)
	logging.config.dictConfig(config)
else:
	logging.basicConfig(level=logging.INFO)

app = flask.Flask(__name__, template_folder='views')

@app.route('/')
def index():
	return flask.render_template('index.html')

# Returns today's events in JSON format as a list of events
@app.route('/events')
def get_events():
	logger = logging.getLogger('mirror')
	logger.debug("Received call to Events controller")
	# Get the URL parameter from the client and attempt to GET it.
	url = flask.request.args.get('url')
	debug = flask.request.args.get('dbg')
	logger.debug("Received URL parameter: " + str(url))

	if url is None:
		logger.warning("No URL parameter supplied for calendar API, aborting request")
		flask.abort(400, "No URL parameter supplied")

	try:
		response = requests.get(url)
	except requests.exceptions.MissingSchema:
		logger.warning("Invalid URL parameter supplied for calendar API, aborting request")
		flask.abort(400, "No URL schema supplied. Perhaps you meant http://{0}?".format(str(url)))
	# Attempt to parse the result into an icalendar object.
	try:
		logger.debug(str(response.content))
		calendar = icalendar.Calendar.from_ical(response.content)
	except ValueError:
		logger.warning("Request to external calendar API did not provide a valid iCalendar format")
		flask.abort(400, "Not a valid ical calendar.")

	events = []
	for event in calendar.walk('VEVENT'):
		start_datetime = event['dtstart'].dt
		end_datetime = event['dtend'].dt
		# event['dtstart'].dt and event['dtend'].dt will return a date object and not a datetime object if the event is a full-day event.
		# Since a date object does not have a date() method, calling date() on an all-day event will fail.
		if isinstance(start_datetime, datetime.datetime):
			start_date = start_datetime.date()
		else:
			start_date = start_datetime

		if datetime.date.today() <= start_date:
			events.append({	'summary' : event['summary'],
							'description' : event['description'],
							'location' : event['location'],
							'start' : str(start_datetime),
							'end' : str(end_datetime)})
	logger.info("Calendar request succeeded and yielded {0} events".format(len(events)))
	return flask.jsonify(results=events)

@app.route('/weather')
# Get the current weather and the forecast from different APIs.
# Combine the results into one single json object
def get_weather():
	logger = logging.getLogger('mirror')
	logger.debug("Received call to Weather controller")
	# TODO: Error handling, manage with only current, only forecast, or both, or neither.
	current_url = flask.request.args.get('current')
	forecast_url = flask.request.args.get('forecast')
	debug = flask.request.args.get('dbg')
	logger.debug("Received current_url parameter: {0}".format(str(current_url)))
	logger.debug("Received forecast_url parameter: {0}".format(str(forecast_url)))
	logger.debug("Received debug parameter: {0}".format(str(debug)))

	if str(debug) == 'true':
		logger.debug("Fetching mock data (debug=true)")
		current_json = '{"coord":{"lon":-21.9,"lat":64.14},"weather":[{"id":800,"main":"Clear","description":"Sky is Clear","icon":"01n"}],"base":"cmc stations","main":{"temp":277.66,"pressure":978,"humidity":56,"temp_min":277.15,"temp_max":278.15},"wind":{"speed":12.3,"deg":80,"gust":19},"clouds":{"all":0},"dt":1452112200,"sys":{"type":1,"id":4835,"message":0.0092,"country":"IS","sunrise":1452078720,"sunset":1452095738},"id":3413829,"name":"Reykjavik","cod":200}'
		forecast_json = '{"city":{"id":3413829,"name":"Reykjavik","coord":{"lon":-21.895411,"lat":64.135483},"country":"IS","population":0,"sys":{"population":0}},"cod":"200","message":0.0101,"cnt":40,"list":[{"dt":1452124800,"main":{"temp":280.65,"temp_min":277.408,"temp_max":280.65,"pressure":964.69,"sea_level":987.96,"grnd_level":964.69,"humidity":91,"temp_kf":3.24},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":80},"wind":{"speed":8.15,"deg":83.5012},"rain":{"3h":0.34},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-07 00:00:00"},{"dt":1452135600,"main":{"temp":280.78,"temp_min":277.713,"temp_max":280.78,"pressure":964.3,"sea_level":987.54,"grnd_level":964.3,"humidity":91,"temp_kf":3.06},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":88},"wind":{"speed":9.21,"deg":95.502},"rain":{"3h":0.88},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-07 03:00:00"},{"dt":1452146400,"main":{"temp":280.14,"temp_min":277.261,"temp_max":280.14,"pressure":967.04,"sea_level":990.35,"grnd_level":967.04,"humidity":96,"temp_kf":2.88},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":8.35,"deg":105.502},"rain":{"3h":2.015},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-07 06:00:00"},{"dt":1452157200,"main":{"temp":280.34,"temp_min":277.638,"temp_max":280.34,"pressure":969.67,"sea_level":992.93,"grnd_level":969.67,"humidity":88,"temp_kf":2.7},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":76},"wind":{"speed":9.5,"deg":95.003},"rain":{"3h":1.3},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-07 09:00:00"},{"dt":1452168000,"main":{"temp":280.13,"temp_min":277.609,"temp_max":280.13,"pressure":972.95,"sea_level":996.22,"grnd_level":972.95,"humidity":83,"temp_kf":2.52},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":68},"wind":{"speed":10.08,"deg":92.0084},"rain":{"3h":0.115},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-07 12:00:00"},{"dt":1452178800,"main":{"temp":279.57,"temp_min":277.225,"temp_max":279.57,"pressure":976.07,"sea_level":999.29,"grnd_level":976.07,"humidity":82,"temp_kf":2.34},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03d"}],"clouds":{"all":48},"wind":{"speed":10.21,"deg":87.5016},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-07 15:00:00"},{"dt":1452189600,"main":{"temp":278.63,"temp_min":276.468,"temp_max":278.63,"pressure":978.97,"sea_level":1002.42,"grnd_level":978.97,"humidity":79,"temp_kf":2.16},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":12},"wind":{"speed":10.47,"deg":86.5006},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-07 18:00:00"},{"dt":1452200400,"main":{"temp":277.45,"temp_min":275.47,"temp_max":277.45,"pressure":982.02,"sea_level":1005.59,"grnd_level":982.02,"humidity":80,"temp_kf":1.98},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":9.86,"deg":83.5049},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-07 21:00:00"},{"dt":1452211200,"main":{"temp":276.7,"temp_min":274.894,"temp_max":276.7,"pressure":984.13,"sea_level":1007.79,"grnd_level":984.13,"humidity":82,"temp_kf":1.8},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":8.97,"deg":81.0005},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-08 00:00:00"},{"dt":1452222000,"main":{"temp":275.76,"temp_min":274.139,"temp_max":275.76,"pressure":985.82,"sea_level":1009.56,"grnd_level":985.82,"humidity":82,"temp_kf":1.62},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":7.9,"deg":73},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-08 03:00:00"},{"dt":1452232800,"main":{"temp":275.38,"temp_min":273.938,"temp_max":275.38,"pressure":986.43,"sea_level":1010.33,"grnd_level":986.43,"humidity":80,"temp_kf":1.44},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":7.22,"deg":71.5001},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-08 06:00:00"},{"dt":1452243600,"main":{"temp":275.42,"temp_min":274.161,"temp_max":275.42,"pressure":987.38,"sea_level":1011.33,"grnd_level":987.38,"humidity":82,"temp_kf":1.26},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":24},"wind":{"speed":6.96,"deg":71.5006},"rain":{"3h":0.01},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-08 09:00:00"},{"dt":1452254400,"main":{"temp":275.09,"temp_min":274.004,"temp_max":275.09,"pressure":988.19,"sea_level":1012.16,"grnd_level":988.19,"humidity":83,"temp_kf":1.08},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03d"}],"clouds":{"all":44},"wind":{"speed":6.56,"deg":69.0057},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-08 12:00:00"},{"dt":1452265200,"main":{"temp":275.15,"temp_min":274.246,"temp_max":275.15,"pressure":988.52,"sea_level":1012.5,"grnd_level":988.52,"humidity":81,"temp_kf":0.9},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":68},"wind":{"speed":6.77,"deg":69.0003},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-08 15:00:00"},{"dt":1452276000,"main":{"temp":274.36,"temp_min":273.639,"temp_max":274.36,"pressure":989.17,"sea_level":1013.08,"grnd_level":989.17,"humidity":82,"temp_kf":0.72},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":6.46,"deg":69.5004},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-08 18:00:00"},{"dt":1452286800,"main":{"temp":274.26,"temp_min":273.722,"temp_max":274.26,"pressure":989.81,"sea_level":1013.78,"grnd_level":989.81,"humidity":82,"temp_kf":0.54},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":6.56,"deg":73.0004},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-08 21:00:00"},{"dt":1452297600,"main":{"temp":274.01,"temp_min":273.646,"temp_max":274.01,"pressure":990.58,"sea_level":1014.6,"grnd_level":990.58,"humidity":83,"temp_kf":0.36},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":12},"wind":{"speed":6.37,"deg":73.5004},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-09 00:00:00"},{"dt":1452308400,"main":{"temp":273.45,"temp_min":273.265,"temp_max":273.45,"pressure":991.17,"sea_level":1015.23,"grnd_level":991.17,"humidity":82,"temp_kf":0.18},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":6.57,"deg":74.5025},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-09 03:00:00"},{"dt":1452319200,"main":{"temp":272.835,"temp_min":272.835,"temp_max":272.835,"pressure":991.51,"sea_level":1015.54,"grnd_level":991.51,"humidity":82,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":12},"wind":{"speed":6.26,"deg":75.001},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-09 06:00:00"},{"dt":1452330000,"main":{"temp":272.567,"temp_min":272.567,"temp_max":272.567,"pressure":992.44,"sea_level":1016.5,"grnd_level":992.44,"humidity":84,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":20},"wind":{"speed":5.86,"deg":74.0006},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-09 09:00:00"},{"dt":1452340800,"main":{"temp":272.45,"temp_min":272.45,"temp_max":272.45,"pressure":993.45,"sea_level":1017.69,"grnd_level":993.45,"humidity":85,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":20},"wind":{"speed":5.37,"deg":74.0089},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-09 12:00:00"},{"dt":1452351600,"main":{"temp":272.253,"temp_min":272.253,"temp_max":272.253,"pressure":993.85,"sea_level":1018.05,"grnd_level":993.85,"humidity":81,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":24},"wind":{"speed":4.85,"deg":71.0013},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-09 15:00:00"},{"dt":1452362400,"main":{"temp":271.89,"temp_min":271.89,"temp_max":271.89,"pressure":994.19,"sea_level":1018.4,"grnd_level":994.19,"humidity":83,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":24},"wind":{"speed":4.35,"deg":67.502},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-09 18:00:00"},{"dt":1452373200,"main":{"temp":271.721,"temp_min":271.721,"temp_max":271.721,"pressure":994.61,"sea_level":1018.98,"grnd_level":994.61,"humidity":84,"temp_kf":0},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":68},"wind":{"speed":4.06,"deg":66.0042},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-09 21:00:00"},{"dt":1452384000,"main":{"temp":272.292,"temp_min":272.292,"temp_max":272.292,"pressure":994.98,"sea_level":1019.36,"grnd_level":994.98,"humidity":83,"temp_kf":0},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"clouds":{"all":88},"wind":{"speed":3.91,"deg":67.501},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-10 00:00:00"},{"dt":1452394800,"main":{"temp":272.215,"temp_min":272.215,"temp_max":272.215,"pressure":994.97,"sea_level":1019.28,"grnd_level":994.97,"humidity":86,"temp_kf":0},"weather":[{"id":600,"main":"Snow","description":"light snow","icon":"13n"}],"clouds":{"all":92},"wind":{"speed":3.31,"deg":61.5007},"rain":{},"snow":{"3h":0.115},"sys":{"pod":"n"},"dt_txt":"2016-01-10 03:00:00"},{"dt":1452405600,"main":{"temp":271.876,"temp_min":271.876,"temp_max":271.876,"pressure":994.8,"sea_level":1019.11,"grnd_level":994.8,"humidity":89,"temp_kf":0},"weather":[{"id":600,"main":"Snow","description":"light snow","icon":"13n"}],"clouds":{"all":92},"wind":{"speed":2.51,"deg":49.501},"rain":{},"snow":{"3h":0.52},"sys":{"pod":"n"},"dt_txt":"2016-01-10 06:00:00"},{"dt":1452416400,"main":{"temp":271.316,"temp_min":271.316,"temp_max":271.316,"pressure":995.34,"sea_level":1019.67,"grnd_level":995.34,"humidity":92,"temp_kf":0},"weather":[{"id":600,"main":"Snow","description":"light snow","icon":"13n"}],"clouds":{"all":88},"wind":{"speed":2.32,"deg":49.5007},"rain":{},"snow":{"3h":0.715},"sys":{"pod":"n"},"dt_txt":"2016-01-10 09:00:00"},{"dt":1452427200,"main":{"temp":271.508,"temp_min":271.508,"temp_max":271.508,"pressure":995.8,"sea_level":1020.14,"grnd_level":995.8,"humidity":88,"temp_kf":0},"weather":[{"id":600,"main":"Snow","description":"light snow","icon":"13d"}],"clouds":{"all":88},"wind":{"speed":2.71,"deg":65.5026},"rain":{},"snow":{"3h":0.47},"sys":{"pod":"d"},"dt_txt":"2016-01-10 12:00:00"},{"dt":1452438000,"main":{"temp":271.775,"temp_min":271.775,"temp_max":271.775,"pressure":995.37,"sea_level":1019.76,"grnd_level":995.37,"humidity":86,"temp_kf":0},"weather":[{"id":600,"main":"Snow","description":"light snow","icon":"13d"}],"clouds":{"all":92},"wind":{"speed":2.35,"deg":71.0031},"rain":{},"snow":{"3h":0.03},"sys":{"pod":"d"},"dt_txt":"2016-01-10 15:00:00"},{"dt":1452448800,"main":{"temp":269.129,"temp_min":269.129,"temp_max":269.129,"pressure":995.38,"sea_level":1019.82,"grnd_level":995.38,"humidity":91,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":32},"wind":{"speed":2.27,"deg":65.5074},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-10 18:00:00"},{"dt":1452459600,"main":{"temp":266.85,"temp_min":266.85,"temp_max":266.85,"pressure":995.68,"sea_level":1020.18,"grnd_level":995.68,"humidity":88,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":44},"wind":{"speed":2.42,"deg":59.5018},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-10 21:00:00"},{"dt":1452470400,"main":{"temp":266.406,"temp_min":266.406,"temp_max":266.406,"pressure":995.56,"sea_level":1020.15,"grnd_level":995.56,"humidity":91,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":44},"wind":{"speed":2.52,"deg":54.0025},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-11 00:00:00"},{"dt":1452481200,"main":{"temp":265.581,"temp_min":265.581,"temp_max":265.581,"pressure":995.14,"sea_level":1019.78,"grnd_level":995.14,"humidity":92,"temp_kf":0},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":56},"wind":{"speed":1.96,"deg":53.5055},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-11 03:00:00"},{"dt":1452492000,"main":{"temp":264.906,"temp_min":264.906,"temp_max":264.906,"pressure":994.72,"sea_level":1019.45,"grnd_level":994.72,"humidity":92,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":36},"wind":{"speed":1.91,"deg":56.0039},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-11 06:00:00"},{"dt":1452502800,"main":{"temp":262.711,"temp_min":262.711,"temp_max":262.711,"pressure":994.8,"sea_level":1019.55,"grnd_level":994.8,"humidity":98,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":1.82,"deg":42.5001},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-11 09:00:00"},{"dt":1452513600,"main":{"temp":261.838,"temp_min":261.838,"temp_max":261.838,"pressure":994.73,"sea_level":1019.49,"grnd_level":994.73,"humidity":93,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":1.88,"deg":33.5006},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-11 12:00:00"},{"dt":1452524400,"main":{"temp":262.173,"temp_min":262.173,"temp_max":262.173,"pressure":994.1,"sea_level":1018.77,"grnd_level":994.1,"humidity":96,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":1.52,"deg":23.0012},"rain":{},"snow":{},"sys":{"pod":"d"},"dt_txt":"2016-01-11 15:00:00"},{"dt":1452535200,"main":{"temp":260.732,"temp_min":260.732,"temp_max":260.732,"pressure":993.39,"sea_level":1018.15,"grnd_level":993.39,"humidity":100,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":1.42,"deg":1.50079},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-11 18:00:00"},{"dt":1452546000,"main":{"temp":260.977,"temp_min":260.977,"temp_max":260.977,"pressure":992.64,"sea_level":1017.31,"grnd_level":992.64,"humidity":99,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":24},"wind":{"speed":2.76,"deg":353.502},"rain":{},"snow":{},"sys":{"pod":"n"},"dt_txt":"2016-01-11 21:00:00"}]}'
	else:
		logger.debug("Fetching real data (debug=false)")
		current_json = requests.get(current_url).content
		forecast_json = requests.get(forecast_url).content

	# Extract the needed information. Create a dict with two keys, current and forecast.
	# On the 'current' key will be a dict containing other dicts, each dict being a certain segment of info.
	# On the 'forecast' key will be a list containing dicts, one dict for each forecast.
	current = json.loads(current_json)
	forecast = json.loads(forecast_json)

	result = {
		"current" : {
			"city" : current['name'],
			"country" : current['sys']['country'],
			"weather" : current['weather'],
		    "wind" : current['wind'],
		    "cloudpercent" : current['clouds']['all'],
		    "temp" : {
		    	"current" : current['main']['temp'],
		    	"max" : current['main']['temp_max'],
		    	"min" : current['main']['temp_min']
		    },
		    "sun" : {
		    	"rise" : current['sys']['sunrise'],
		    	"set" : current['sys']['sunset']
		    }
		},
		"forecast" : {
			"city" : forecast['city']['name'],
			"country" : forecast['city']['country'],

			"forecasts" : [	{ 
				"time" : fc['dt'],
				"cloudpercent" : fc['clouds']['all'],
				"wind" : fc['wind'],
				"temp" : {
					"current" : fc['main']['temp'],
					"max" : fc['main']['temp_max'],
					"min" : fc['main']['temp_min'],
				}
			} for fc in forecast['list']]
		}
	}

	return flask.jsonify(result)

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