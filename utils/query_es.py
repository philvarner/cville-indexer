from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

host = "search-cville-indexer-public-osevbtjwraifeeq5p4gcmzjejq.us-east-1.es.amazonaws.com"
session = boto3.Session(profile_name='default')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=AWS4Auth(
        session.get_credentials().access_key,
        session.get_credentials().secret_key,
        session.region_name,
        'es',
        session_token=session.get_credentials().token),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

res = es.search(index="test-index", body={"size":10000, "query": {"match": {"content": "serepta"}}})

print(res)
