# index.py
import json
import requests

import sys
from elasticsearch import Elasticsearch

# Vars
FILE_URL = "https://gist.githubusercontent.com/mannyrivera2010/25931f8b24be958e03acd2bb6c0503a6/raw/d885a8900ec089e7af29a77b6d569ba2c12b9b62/gistfile1.txt"

ES_HOST = {
    "host" : "localhost",
    "port" : 9200
}

INDEX_NAME = 'titanic'
TYPE_NAME = 'passenger'

ID_FIELD = 'PassengerId'


response = requests.get(FILE_URL)
response_json_obj = json.loads(response.text)


bulk_data = []

for record in response_json_obj:
    op_dict = {
        "index": {
        	"_index": INDEX_NAME,
        	"_type": TYPE_NAME
        	# "_id": record[ID_FIELD]
        }
    }

    bulk_data.append(op_dict)
    bulk_data.append(record)

# create ES client, create index
es = Elasticsearch(hosts = [ES_HOST])

if es.indices.exists(INDEX_NAME):
    print("deleting '%s' index..." % (INDEX_NAME))
    res = es.indices.delete(index = INDEX_NAME)
    print(" response: '%s'" % (res))

request_body = {
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

print("creating '%s' index..." % (INDEX_NAME))
res = es.indices.create(index = INDEX_NAME, body = request_body)
print(" response: '%s'" % (res))


# bulk index the data
print("bulk indexing...")
res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)
#print(" response: '%s'" % (res))


# sanity check
print("searching...")
res = es.search(index = INDEX_NAME, size=2, body={"query": {"match_all": {}}})
print(" response: '%s'" % (res))

print("results:")
for hit in res['hits']['hits']:
    print(hit["_source"])
