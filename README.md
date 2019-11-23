# Cville Indexer

Index docs relevant to Charlottesville, including Daily Progress images from 1893-1968 and City Council meeting notes.

    brew install tesseract

## Run Daily Progress image puller
create a t3.small EC2 instance

```bash
sudo yum update
(wget -O - pi.dk/3 || curl pi.dk/3/ || fetch -o - pi.dk/3) | bash
parallel --citation

export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=

vi get_dp.sh # add it
chmod u+x get_dp.sh
screen -L ./get_dp.sh
```


# Overview

Components in this repo:
1. S3 event listener

The repo consists of:
1. Invoke library build definitions for deploying CloudFormation templates and Zappa project
1. Generator for Zappa execution IAM Policy
1. Generator for Zappa config file

In this project,
* `cville-indexer` is used as the example application and package name
* `rcollimore` is used as the example username

Most of the configuration for deploying to AWS is generated from templates to allow multiple developers to deploy to
the same AWS account without stepping on each other's resources, so elements are usually suffixed with a unique name,
e.g., 'dev-rcollimore'.

[Credstash](https://github.com/fugue/credstash) is used for storing the (single) secret token validated by the
custom authorizer.

#  Setting up a dev environment

## Dependencies

* Python or [pyenv](https://github.com/pyenv/pyenv) 3.6 to bootstrap pipenv

## Install pipenv

```bash
pip3 install pipenv
```

## Setting up a pipenv virtualenv

From within this repo, run:

```bash
pipenv install --dev
```

## Running the linter

```bash
pipenv run pycodestyle .
```

## Running the tests

```bash
pipenv run pytest tests
```

## Execution

### Initially deploy environment 'dev' to AWS

```bash
invoke create --env dev
```

### Initially setup SSL certs for environment 'dev' in AWS

```bash
invoke certify --env dev
```

### Update existing environment 'dev' to AWS

```bash
invoke update --env dev
```

Debug:
```bash
invoke tail --env dev
```

```bash
virtualenv python --python=python3.7
source python/bin/activate and then pip3 install boto3
zip -r boto3_layer.zip python/lib/
Create new Lambda Layer with boto3_layer.zip and add layer to Lambda Function
```

## Athena Tables

```
CREATE DATABASE IF NOT EXISTS cville_indexer
```
then
```
CREATE EXTERNAL TABLE cville_indexer.cville_indexer_assets_inventory (
  bucket string,
  key string,
  size bigint,
  last_modified_date timestamp
  )
  PARTITIONED BY (dt string)
  ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.orc.OrcSerde'
  STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat'
  OUTPUTFORMAT  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat'
  LOCATION 's3://philvarner-inventories/cville-indexer-assets/cville-indexer-assets/hive'
```

then

```
MSCK REPAIR TABLE cville_indexer.cville_indexer_assets_inventory
```