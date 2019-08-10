import json
import logging

import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

host = "vpc-cville-indexer-cffwqjesu5zyxr3erdivfqzzaa.us-east-1.es.amazonaws.com"


def handler(event, _context):
    try:
        if event['Records'][0]['eventSource'] != 'aws:s3' \
                or not event['Records'][0]['eventName'].startswith('ObjectCreated:'):
            logger.error('invalid event, not aws:s3 ObjectCreated')
            return

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        if key.endswith('.jpg') or key.endswith('.pdf'):
            handle_extraction(bucket, key)
        elif key.endswith(".json"):
            handle_indexing(bucket, key)
        else:
            logger.error('ignoring: ' + str(bucket) + "/" + str(key), exc_info=True)
    except KeyError:
        logger.error('key error', exc_info=True)
    except IndexError:
        logger.error('index error', exc_info=True)
    except TypeError:
        logger.error('None passed for dict or list', exc_info=True)


def handle_extraction(bucket, key):
    session = boto3.Session(profile_name='default')

    extraction = session.client('textract').detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        })
    # logger.error('response: ' + str(extraction), exc_info=True)
    session.client('s3').put_object(
        Bucket=bucket,
        Key=key[:-4] + '.json',
        Body=json.dumps(extraction),
        ContentType='application/json'
    )
    # logger.error('response: ' + str(put), exc_info=True)
    return extraction


def handle_indexing(bucket, key):

    session = boto3.Session(profile_name='default')
    obj = session.client('s3').get_object(
        Bucket=bucket,
        Key=key
    )
    extraction = json.loads(obj['Body'].read().decode('utf-8'))
    all_words = ' '.join(list(map(lambda x: x["Text"],
                                  list(filter(lambda x: x["BlockType"] == "LINE", extraction["Blocks"]))
                                  )))
    credentials = session.get_credentials()
    region = session.region_name
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es',
                       session_token=credentials.token)
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    doc = {
        "name": "{}".format(key),
        "bucket": "{}".format(bucket),
        "content": all_words
    }
    res = es.index(index="test-index", id=key, body=doc)
    logger.info(res['result'])



