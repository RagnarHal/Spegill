import os
import ConfigParser as configparser

# Initialize configuration environment
# Check if config directory exists and create it if missing.
basepath = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(basepath, 'config')):
	os.makedirs(os.path.join(basepath, 'config'))

def get_user_settings():
	# Check if config file exists and load it. If it doesn't exist, create it with default settings.
	configpath = os.path.join(basepath, 'config', 'settings.cfg')
	settings = configparser.SafeConfigParser()

	if os.path.exists(configpath):
		settings.read(configpath)
	else:
		settings.add_section('app')
		settings.set('app', 'debug', 'false')

		settings.add_section('weather')
		settings.set('weather', 'api', 'http://api.openweathermap.org/data')
		settings.set('weather', 'api_version', '2.5')
		settings.set('weather', 'city_id', 'your_cityid_here')
		settings.set('weather', 'appid', 'your_appid_here')
		settings.set('weather', 'weather', '${api}/${api_version}/weather?id=${city_id}$appid=${appid}')
		settings.set('weather', 'forecast', '${api}/${api_version}/forecast?id=${city_id}$appid=${appid}')

		settings.add_section('calendar')
		settings.set('calendar', 'url', 'your_calendar_url_here')
		settings.set('calendar', 'holidays', 'your_calendar_url_here')

		settings.add_section('logger')
		settings.set('logger', 'config', os.path.join(basepath, 'config', 'loggers.json'))

		settings.add_section('mock')
		settings.set('mock', 'calendar', os.path.join(basepath, 'testing', 'calendar.txt'))
		settings.set('mock', 'weather', os.path.join(basepath, 'testing', 'weather_current.json'))
		settings.set('mock', 'forecast', os.path.join(basepath, 'testing', 'weather_forecast.json'))

		with open(configpath, 'wb') as f:
			settings.write(f)

	return settings