#!/usr/bin/python3

import os
import sys

from myLogger import myLogger

log_file = '/tmp/myLogger-log-test'
logger = myLogger(
    file=log_file,
    format_line='{datatimeiso} - {name} - {levelname} - {message}',
    format_data={
        'name': 'PID:' + str(os.getpid())
    },
    stdout=sys.stdout,
    stderr=sys.stderr)
logger.info('Simple string information', *sys.argv)