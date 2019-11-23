import json
import logging
import time

import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

host = "search-cville-indexer-public-osevbtjwraifeeq5p4gcmzjejq.us-east-1.es.amazonaws.com"


def handler(event, _context):
    try:
        if event['Records'][0]['eventSource'] != 'aws:s3' \
                or not event['Records'][0]['eventName'].startswith('ObjectCreated:'):
            logger.error('invalid event, not aws:s3 ObjectCreated')
            return

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        size = event['Records'][0]['s3']['object']['size']

        if key.endswith('.jpg') and key.startswith('daily_progress/') and 1800000 <= size <= 3000000:
            handle_extraction(bucket, key)
        elif key.endswith('.pdf'):
            handle_extraction(bucket, key)
        elif key.endswith(".json"):
            handle_indexing(bucket, key)
        else:
            logger.error(f'ignoring: {str(bucket)}/{str(key)} size: {size}', exc_info=True)
    except KeyError:
        logger.error('key error', exc_info=True)
    except IndexError:
        logger.error('index error', exc_info=True)
    except TypeError:
        logger.error('None passed for dict or list', exc_info=True)


def handle_extraction(bucket, key):
    time.sleep(5) # Textract has a default limit of 0.25 transactions / sec, so sleep a long time... ugh
    session = boto3.Session()

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
    session = boto3.Session()
    obj = session.client('s3').get_object(
        Bucket=bucket,
        Key=key
    )
    extraction = json.loads(obj['Body'].read().decode('utf-8'))
    all_words = ' '.join(list(map(lambda x: x["Text"],
                                   list(filter(lambda x: x["BlockType"] == "LINE", extraction["Blocks"]))
                                   )))
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
    doc = {
        "bucket": "{}".format(bucket),
        "key": "{}".format(key),
        "content": all_words
    }
    res = es.index(index="test-index", doc_type="item", id=key, body=doc)
    logger.info(res['result'])
    return doc
