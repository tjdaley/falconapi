"""
log_util.py - Logging utilities
"""
import logging
import os

def get_logger(name: str) -> logging.Logger:
	"""
	Return a logger object
	"""
	level = convert_level(os.environ.get('LOG_LEVEL', 'INFO').upper())
	logger = logging.getLogger(name)
	logger.setLevel(level)

	# Create console handler
	ch = logging.StreamHandler()
	ch.setLevel(level)

	# Create formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# Add formatter to console handler
	ch.setFormatter(formatter)

	# Add console handler to logger
	logger.addHandler(ch)

	return logger

def convert_level(log_level: str) -> int:
	"""
	Convert a log level string to a log level integer
	"""
	if log_level == 'DEBUG':
		return logging.DEBUG
	elif log_level == 'INFO':
		return logging.INFO
	elif log_level == 'WARNING':
		return logging.WARNING
	elif log_level == 'ERROR':
		return logging.ERROR
	elif log_level == 'CRITICAL':
		return logging.CRITICAL
	else:
		return logging.INFO