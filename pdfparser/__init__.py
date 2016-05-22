import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('pdfparser')
# create file handler which logs even debug messages
fh = logging.FileHandler('summarizer.log', mode='w')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
#logger.addHandler(ch)

# LOG_LEVEL = logging.INFO
_log_level = 1  # verbosity of log. 1:normal - 2:verbose - 3:visual

logger.debug('Logging object initialized with log level {level}'.format(level=_log_level))
