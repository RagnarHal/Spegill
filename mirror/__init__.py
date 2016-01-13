from flask import Flask
app = Flask(__name__)

#-- Set up logging --#
from mirror import logger
logger = logger.init()

#-- Set up config --#

import mirror.views