from elasticsearch import Elasticsearch
import os

username='elastic' #os.environ.get("elastic_username") 3o9ba lwa9t brq!
password='y8rBwtvDiyXlS9q2uoj20emj'#os.environ.get("elastic_pass") 
cloud_id='GHack:ZXVyb3BlLXdlc3Q5LmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkNzY3OTMyOTMwOWZiNGJjZDg1ZjU5OWZmY2MxN2FmYjQkMzE4NDY3YzgxMTcxNDcyNTk1ODM3ZTlmNjFhN2E4MGE=' #os.environ.get("elastic_id") 

es = Elasticsearch(
    cloud_id=cloud_id,
    http_auth=(username, password)
)

if es.ping():
    print("Connected to Elasticsearch")
else:
    raise Exception("Connection to Elasticsearch failed")


index_name = "file_key_words"

schema = {
 "mappings": {
    "properties": {
      "file_url": {
        "type": "keyword"
      },
      "keywords": {
        "type": "text",
        "analyzer": "standard"
      }
    }
 }
}

# Create the index with the schema
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=schema)
    print("Index created")
else:
    print("Index already exists")

def index_document(index_name, file_url, keywords):
    document = {
        "file_url": file_url,
        "keywords": keywords
    }
    es.index(index=index_name, body=document)

# Example
# file_url = "https://example.com/file1.pdf"
# keywords = ['technology adaptive learning', 'study adaptive learning', 'classifies adaptive education', 'developed adaptive teaching', 'adaptive educational systems']
# index_document(index_name, file_url, keywords)

def search_documents(index_name, search_query):
    response = es.search(index=index_name, body={
            "query": {
                "fuzzy": {
                    "keywords": {
                        "value": search_query,
                        "fuzziness": 2
                    }
                }
            }
        })
    
    file_urls = set(hit['_source']['file_url'] for hit in response['hits']['hits'])

    return file_urls

