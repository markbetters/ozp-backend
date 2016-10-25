# get_listings.py
# This script is for learning
# This script will get all the listing data in Appsmall and put it in elastic search
import json
import requests
import sys
from elasticsearch import Elasticsearch


url = 'http://127.0.0.1:8001/api/listing'
headers = {'Authorization': 'Basic YmlnYnJvdGhlcjpwYXNzd29yZA=='}

response = requests.get(url, headers=headers)
response_json_obj = json.loads(response.text)

# for item in response_json_obj:
#     print(item)


ES_HOST = {
    "host" : "localhost",
    "port" : 9200
}

INDEX_NAME = 'appsmall'
TYPE_NAME = 'listings'

ID_FIELD = 'id'


bulk_data = []

for record in response_json_obj:
    if 'counts' in record:
        pass  # Skip

    else:
        op_dict = {
            "index": {
                "_index": INDEX_NAME,
                "_type": TYPE_NAME,
                 "_id": record[ID_FIELD]
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


# For the mappings
# http://127.0.0.1:9200/appsmall/_mappings?pretty

# Search API
# http://127.0.0.1:9200/appsmall/_search
