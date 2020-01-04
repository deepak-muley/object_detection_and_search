import unittest
from es import ElasticSearchWrapper
  
class ElasticSearchTest(unittest.TestCase): 
  
    def setUp(self): 
        self._es = ElasticSearchWrapper("elasticsearch", 9200)

    # Returns True or False.  
    def testESConnection(self):         
        self.assertTrue(self._es.connect())
        
    def testESCreateIndex(self):
        self._es.connect()
        # index settings
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "members": {
                    "dynamic": "strict",
                    "properties": {
                        "title": {
                            "type": "text"
                        },
                        "submitter": {
                            "type": "text"
                        },
                        "description": {
                            "type": "text"
                        },
                        "calories": {
                            "type": "integer"
                        },
                    }
                }
            }
        }
        index_name = "testindex"
        self._es.create_index(index_name, settings)
  
if __name__ == '__main__': 
    unittest.main() 