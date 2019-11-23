from itertools import chain

from awacs.aws import Policy, Allow, Statement
from awacs.awslambda import InvokeFunction
from awacs.ec2 import *
from awacs.logs import CreateLogGroup, PutLogEvents, CreateLogStream
from awacs.xray import PutTraceSegments, PutTelemetryRecords
from awacs.textract import Action as TextractAction
from awacs.s3 import Action as S3Action
from awacs.es import *

All = "*"
AllResources = ["*"]


def attach_policy_json(**kwargs):
    return attach_policy(**kwargs).to_json()


def attach_policy(*, region, acct_id):
    return Policy(
        Version='2012-10-17',
        Statement=list(chain.from_iterable([
            stmts_logging(region, acct_id),
            stmts_lambda_invocation(),
            stmts_vpc(),
            stmts_s3(),
            stmts_textract(),
            stmts_es()
        ]))
    )


def stmts_es():
    return [Statement(
        Effect=Allow,
        Action=[ESHttpPut],
        Resource=['arn:aws:es:us-east-1:843732292144:domain/cville-indexer-public/*'])
    ]


def stmts_textract():
    return [Statement(
        Effect=Allow,
        Action=[TextractAction(All)],
        Resource=AllResources)
    ]


def stmts_s3():
    return [Statement(
        Effect=Allow,
        Action=[S3Action(All)],
        Resource=['arn:aws:s3:::cville-indexer-assets/*']),
        Statement(
            Effect=Allow,
            Action=[S3Action(All)],
            Resource=['arn:aws:s3:::cville-indexer-assets']),
    ]


def stmts_logging(region, acct_id):
    return [Statement(
        Effect=Allow,
        Action=[CreateLogGroup],
        Resource=[f'arn:aws:logs:{region}:{acct_id}:*']),
        Statement(
            Effect=Allow,
            Action=[CreateLogStream, PutLogEvents],
            Resource=[f'arn:aws:logs:{region}:{acct_id}:*']
            # Resource=[f'arn:aws:logs:{region}:{acct_id}:log-group:/aws/lambda/pvarner-test-1:*'
        ), Statement(
            Effect=Allow,
            Action=[PutTraceSegments, PutTelemetryRecords],
            Resource=AllResources
        )]


def stmts_lambda_invocation():
    return [Statement(
        Effect=Allow,
        Action=[InvokeFunction],
        Resource=AllResources  # TODO: my name
    )]


def stmts_vpc():
    return [Statement(
        Effect=Allow,
        Action=[
            AttachNetworkInterface,
            CreateNetworkInterface,
            DeleteNetworkInterface,
            DescribeInstances,
            DescribeNetworkInterfaces,
            DetachNetworkInterface,
            ModifyNetworkInterfaceAttribute,
            ResetNetworkInterfaceAttribute
        ],
        Resource=AllResources)]
