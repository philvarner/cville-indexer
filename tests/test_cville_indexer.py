import json
from collections import defaultdict
from io import BytesIO
from logging import ERROR

import boto3
# from moto import mock_s3

import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from cville_indexer import handle_extraction, handle_indexing


host = "search-cville-indexer-public-osevbtjwraifeeq5p4gcmzjejq.us-east-1.es.amazonaws.com"

def nested_dict():
    return defaultdict(nested_dict)


def _test_extracting_jpeg():
    extraction = handle_extraction("philvarner-sources", "daily_progress/2070291.jpg")

    assert len(extraction['Blocks']) == 1282


def _test_indexing_extraction():
    extraction = handle_indexing("philvarner-sources", "daily_progress/2070291.json")

    assert extraction['bucket'] == "philvarner-sources"
    assert extraction['key'] == 'daily_progress/2070291.json'
    # assert 'Charlottesville' in extraction['content']

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

    res = es.search(index="test-index", body={"query": {"match": { "content": "Charlottesville"}}})

    assert res == ""

event = "{'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2019-08-11T14:12:51.876Z', 'eventName': 'ObjectCreated:Copy', 'userIdentity': {'principalId': 'AWS:AIDAJ7SPB7L6VK5AADZGO'}, 'requestParameters': {'sourceIPAddress': '216.197.76.110'}, 'responseElements': {'x-amz-request-id': '06427FF927587D24', 'x-amz-id-2': 'qwo9Syb6Vy40pcUicZfgwLVHqJKR76q4VBs36aP+HWwloG3c2XXVAGo+osRZZTv9QezEqAxWOr4='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'cville-indexer-dev-philvarner:cville_indexer.handler', 'bucket': {'name': 'cville-indexer-assets', 'ownerIdentity': {'principalId': 'A13086R24I2F4M'}, 'arn': 'arn:aws:s3:::cville-indexer-assets'}, 'object': {'key': 'daily_progress/2070291.jpg', 'size': 2319935, 'eTag': '1c82ecc0487f4c9f168e929791442268', 'sequencer': '005D502263B1B509BD'}}}]}"
# @mock_s3
# def test_get_source_from_s3():
#     # given
#     client = boto3.client('s3')
#     client.create_bucket(Bucket='bucket1')
#     client.put_object(
#         Bucket='bucket1',
#         Key='key1.json',
#         Body=BytesIO(b"some initial binary data: \x00\x01")
#     )
#
#     result = get_source_from_s3('bucket1', 'key1.json')
#
#     assert result['Body'] is not None
#     assert result['ContentLength'] == 28
#
#
# def test_lambda_handler():
#     # given
#     client = boto3.client('s3')
#     client.create_bucket(Bucket='bucket1')
#     client.put_object(
#         Bucket='bucket1',
#         Key='key1.json',
#         Body=BytesIO(bytearray(json.dumps(example_json_dict1), 'UTF-8'))
#     )
#
#     event = {
#         "Records": [
#             {
#                 "eventVersion": "2.0",
#                 "eventSource": "aws:s3",
#                 "awsRegion": "us-east-1",
#                 "eventTime": "1970-01-01T00:00:00.000Z",
#                 "eventName": "ObjectCreated:Put",
#                 "s3": {
#                     "s3SchemaVersion": "1.0",
#                     "bucket": {
#                         "name": "bucket1"
#                     },
#                     "object": {
#                         "key": "key1.json",
#                         "size": 3
#                     }
#                 }
#             }
#         ]
#     }
#
#     # when
#     generate(event, None)
#
#     # then
#     assert client.get_object(
#         Bucket='bucket1',
#         Key='key1.pdf'
#     ) is not None
