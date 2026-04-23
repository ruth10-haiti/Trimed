import os
from datetime import datetime

# Créer le répertoire de logs s'il n'existe pas
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'api': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file_api': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(log_dir, f'api_{datetime.now().strftime("%Y%m")}.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'api',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_dir, 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'file_database': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir, 'database.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_database'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'trimedh_api': {
            'handlers': ['console', 'file_api', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        'gestion_tenants': {
            'handlers': ['console', 'file_api'],
            'level': 'INFO',
            'propagate': False,
        },
        'comptes': {
            'handlers': ['console', 'file_api', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        'patients': {
            'handlers': ['console', 'file_api'],
            'level': 'INFO',
            'propagate': False,
        },
        'medical': {
            'handlers': ['console', 'file_api'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}