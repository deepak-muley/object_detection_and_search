from elasticsearch import Elasticsearch
import logging
log = logging.getLogger(__name__)

class ElasticSearchWrapper(object):
    def __init__(self, host='localhost', port=9200):
        self._es = None
        self._host = host
        self._port = port

    def connect(self):
        self._es = Elasticsearch([{'host': self._host, 'port': self._port}])
        if self._es.ping():
            return True
        return False

    def create_index(self, index_name, settings):
        created = False
        try:
            if not self._es.indices.exists(index_name):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self._es.indices.create(index=index_name, ignore=400, body=settings)
                log.info('Index %s is created', index_name)
            created = True
        except Exception as ex:
            log.exception(str(ex))
        finally:
            return created

    def store_record(self, index_name, doc_type, record):
        try:
            return self._es.index(index=index_name, doc_type=doc_type, body=record)
        except Exception as ex:
            log.exception('Error in indexing data')