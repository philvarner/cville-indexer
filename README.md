# Cville Indexer

Index docs relevant to Charlottesville, including Daily Progress images from 1893-1968 and City Council meeting notes.

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

wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm -P /tmp

sudo yum install -y /tmp/epel-release-latest-7.noarch.rpm

sudo yum install -y --enablerepo epel moreutils

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
