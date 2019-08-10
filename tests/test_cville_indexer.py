import json
from collections import defaultdict
from io import BytesIO
from logging import ERROR

import boto3
from moto import mock_s3

from cville_indexer import handle_extraction

def nested_dict():
    return defaultdict(nested_dict)


def test_creating_pdf():
    extraction = handle_extraction("philvarner-sources", "daily_progress/2070291.jpg")

    assert extraction == "foo"

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
