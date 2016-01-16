from flask import Flask
app = Flask(__name__)

#-- Set up app config --#
from mirror import config
settings = config.get_user_settings()

#-- Set up logging --#
from mirror import logger
logger = logger.init()

import mirror.controllers