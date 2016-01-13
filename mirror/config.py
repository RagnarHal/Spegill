import os
import ConfigParser as configparser

# Initialize configuration environment
def init():
	# Check if config directory exists and create it if missing.
	config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lars')
	if not os.path.exists(config_path):
		os.makedirs(config_path)

def mirror():
	# Check if config file exists and load it. If it doesn't exist, create it with default settings. If a section doesn't exist, load None
	config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'mirror.cfg')

def logger():
	return False