"""
log_util.py - Logging utilities
"""
import logging
import os
import psutil

def get_logger(name: str) -> logging.Logger:
	"""
	Return a logger object
	"""
	if running_as_service():
		logging.basicConfig(format='%(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		level = convert_level(os.environ.get('LOG_LEVEL', 'INFO').upper())
	else:
		logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		level=logging.DEBUG
	logger = logging.getLogger(name)
	logger.setLevel(level)

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

def running_as_service() -> bool:
	"""
	Return True if we are running as a service
	"""
	parent_pid = os.getppid()
	print("Parent PID:", parent_pid)
	return parent_pid == 1
	# return 'SYSTEMD_INVOCATION' in os.environ
