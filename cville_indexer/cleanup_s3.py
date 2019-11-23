import boto3
import subprocess
import random
import string
from multiprocessing import Pool
import os

pool = Pool(20)

bucket = 'philvarner-sources'
prefix = 'daily_progress/'
kwargs = {'Bucket': bucket, 'Prefix': prefix}

s3 = boto3.Session().client('s3')
continuation_token=''
is_truncated=True


def process_obj(obj):
    key = obj['Key']
    size = obj['Size']
    if key.endswith('.jpg'):
        if size < 1000000 or size > 5000000:
            print(f'deleting: s3://{str(bucket)}/{str(key)} size: {size}')
            s3.delete_object(Bucket=bucket, Key=key)
        else:
            filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) + '.jpg'
            aws_cp = subprocess.Popen(('aws', 's3', 'cp', f's3://{str(bucket)}/{str(key)}', filename))
            aws_cp.wait()
            output = str(subprocess.check_output(('identify', filename)))
            if 'Gray 256c' not in output:
                print(f'not gray, so not copying: s3://{str(bucket)}/{str(key)} size: {size} {output}')
            else:
                s3.put_object(Body=open(filename, 'rb'), Bucket='pvarner-dailyprogress', Key=str(key))
                print(f'ok: copy {str(key)} size: {size}')
            os.remove(filename)
            s3.delete_object(Bucket=bucket, Key=key)
    else:
        print(f'ignoring: {str(bucket)}/{str(key)} size: {size}')
    return f'{str(bucket)}/{str(key)}'


def f(x):
    print(x)
    return x


def process_page(page):
    print(pool.map(process_obj, page))


if __name__ == '__main__':
    while True:
        resp = s3.list_objects_v2(**kwargs)
        process_page(resp['Contents'])
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
