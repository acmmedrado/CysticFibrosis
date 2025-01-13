import logging
from datetime import datetime
from logging import config

LOG_FILENAME = datetime.now().strftime('./log/logfile_%H_%M_%S_%d_%m_%Y.log')

#https://stackoverflow.com/questions/49580313/create-a-log-file

log_config = {
    "version":1,
    "root":{
        "handlers" : ["console", "file"],
        "level": "DEBUG"
    },
    "handlers":{
        "console":{
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        },
        "file":{
            "formatter":"std_out",
            "class":"logging.FileHandler",
            "level":"DEBUG",
            "filename":LOG_FILENAME
        }
    },
    "formatters":{
        'verbose': {
            'format': ("[%(asctime)s] %(levelname)s "
                       "[%(name)s:%(lineno)s] %(message)s"),
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
}

config.dictConfig(log_config)

logger = logging.getLogger('api_logger')
batch_process_logger = logging.getLogger('batch_process_logger')