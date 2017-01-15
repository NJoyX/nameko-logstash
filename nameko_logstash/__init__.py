from __future__ import unicode_literals, print_function, absolute_import

import logging
import os

import logstash
from nameko.extensions import DependencyProvider

__author__ = 'Fill Q'
__all__ = ['Logstash']

_levelNames = ['CRITICAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG']
LOGSTASH_HOST = 'LOGSTASH_HOST'
LOGSTASH_PORT = 'LOGSTASH_PORT'
LOGSTASH_VERSION = 'LOGSTASH_VERSION'


class Logstash(DependencyProvider):
    def __init__(self, host='logstash', port=5959, version=1, tags=list()):
        self.host = os.environ.get(LOGSTASH_HOST, host)
        self.port = os.environ.get(LOGSTASH_PORT, port)
        self.version = os.environ.get(LOGSTASH_VERSION, version)
        self.logger = None
        self.tags = list(tags) if isinstance(tags, (list, tuple)) else []

    def setup(self):
        _tags = ['trinity', self.container.service_name]
        self.logger = logging.getLogger(self.container.service_name)
        self.logger.setLevel(self._loglevel)
        if self.tags:
            _tags += self.tags
        _handler = logstash.TCPLogstashHandler(
            self.container.config.get(LOGSTASH_HOST, self.host),
            self.container.config.get(LOGSTASH_PORT, self.port),
            version=self.container.config.get(LOGSTASH_VERSION, self.version),
            tags=list(set(_tags)),
            message_type='microservice'
        )
        self.logger.addHandler(_handler)

    @property
    def _loglevel(self):
        _default = 'DEBUG'
        _level = self.container.config.get('LOGLEVEL', _default)
        if _level in _levelNames:
            return getattr(logging, _level, _default)
        return logging.ERROR

    def get_dependency(self, worker_ctx):
        return self.logger
