import boto3
import subprocess
import random
import string
from multiprocessing import Pool
import os


bucket = 'philvarner-sources'
prefix = 'daily_progress/'


def process_obj(obj):
    s3 = boto3.Session().client('s3')
    key = obj['Key']
    size = obj['Size']
    if key.endswith('.jpg'):
        print(f'checking s3://{str(bucket)}/{str(key)} size: {size}')
        if size < 1000000 or size > 5000000:
            print(f'deleting: s3://{str(bucket)}/{str(key)} size: {size}')
            s3.delete_object(Bucket=bucket, Key=key)
        else:
            filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) + '.jpg'
            s3.download_file(bucket, key, filename)
            output = str(subprocess.check_output(('identify', filename)))
            if 'Gray 256c' in output or '8-bit PseudoClass 256c' in output:
                f = open(filename, "rb")
                file_content = f.read()
                f.close()
                s3.put_object(Body=file_content, Bucket='pvarner-dailyprogress', Key=str(key))
                print(f'ok: copy {str(key)} size: {size} {output}')
            else:
                print(f'not gray, so not copying: s3://{str(bucket)}/{str(key)}')
            os.remove(filename)
            s3.delete_object(Bucket=bucket, Key=key)
    else:
        print(f'ignoring: {str(bucket)}/{str(key)} size: {size}')
    return f'{str(bucket)}/{str(key)}'


def process_page(page):
    print(f"processing page...")
    result = pool.map(process_obj, page)
    print(f"processed page.")


if __name__ == '__main__':
    pool = Pool(10)
    s3client = boto3.Session().client('s3')
    kwargs = {'Bucket': bucket, 'Prefix': prefix}
    while True:
        print("Processing page...")
        resp = s3client.list_objects_v2(**kwargs)
        process_page(resp['Contents'])
        print("Processing page done.")
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
