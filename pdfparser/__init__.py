import ConfigParser
import logging
import os

# Get configuration parameters
basedir = os.path.abspath(os.path.dirname(__file__))
_config = ConfigParser.SafeConfigParser()
_config.read(os.path.join(basedir, 'pdfparser.conf'))

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('pdfparser')
# create file handler which logs even debug messages
fh = logging.FileHandler('summarizer.log', mode='w')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

# LOG_LEVEL = logging.INFO
_log_level = 3  # verbosity of log. 1:debug - 2:verbose - 3:visual

logger.debug('Logging object initialized with log level {level}'.format(level=_log_level))

