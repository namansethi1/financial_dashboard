import os
import logging.config

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)

# Define logging configuration with separate handlers and loggers
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },

    'handlers': {
        # Console handler for all log messages
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG'
        },
        # Rotating file handler for general logging
        'general_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'logs/general.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB per file
            'backupCount': 5,
            'level': 'DEBUG',
            'encoding': 'utf8'
        },
        # Rotating file handler for Alpha Vantage logs
        'alpha_vantage_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'logs/alpha_vantage.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'level': 'INFO',
            'encoding': 'utf8'
        },
        # Rotating file handler for Yahoo Finance logs
        'yahoo_finance_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'logs/yahoo_finance.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'level': 'INFO',
            'encoding': 'utf8'
        }
    },

    'loggers': {
        # Logger for Alpha Vantage events
        'alpha_vantage': {
            'handlers': ['console', 'alpha_vantage_file', 'general_file'],
            'level': 'INFO',
            'propagate': False
        },
        # Logger for Yahoo Finance events
        'yahoo_finance': {
            'handlers': ['console', 'yahoo_finance_file', 'general_file'],
            'level': 'INFO',
            'propagate': False
        }
    },

    # Root logger for general logging
    'root': {
        'handlers': ['console', 'general_file'],
        'level': 'DEBUG'
    }
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Create loggers
alpha_logger = logging.getLogger('alpha_vantage')
yahoo_logger = logging.getLogger('yahoo_finance')
logger = logging.getLogger()
