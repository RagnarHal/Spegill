import os
import json
import logging
import logging.config
from mirror import settings

def init():
	# Check if logging folder exists
	log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
	if not os.path.exists(log_path):
		os.makedirs(log_path)

	# Checking for logger config files
	config_path = settings.get('logger', 'config')
	if os.path.exists(config_path):
		with open(config_path, 'rt') as f:
			config = json.load(f)
		logging.config.dictConfig(config)
	else:
		logging.basicConfig(level=logging.INFO)

	return logging.getLogger('mirror')
