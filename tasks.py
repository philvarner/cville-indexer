import os
import re

from invoke import task

from cville_indexer.zappa_attach_policy import attach_policy_json
from cville_indexer.zappa_settings import generate_zappa_settings

ACCT_ID = 'acct_id'
REGION = 'region'

config = {
    'dev': {
        ACCT_ID: '843732292144',
        REGION: 'us-east-1'
    },
    'sandbox': {
        ACCT_ID: '843732292144',
        REGION: 'us-east-1'
    },
    'qa': {
        ACCT_ID: '843732292144',
        REGION: 'us-east-1'
    },
    'production': {
        ACCT_ID: '843732292144',
        REGION: 'us-east-1'
    }
}


@task
def tests(ctx, marker=None, open=False, stdout=False):
    marker_flag = f'-m {marker}' if marker else ''
    stdout_flag = '-s' if stdout else ''
    ctx.run(
        f'pytest {stdout_flag} --cov=cville-indexer'
        f' --cov-report html:tmp/cov_html'
        f' "{marker_flag}" tests',
        pty=True)
    if open:
        ctx.run('open tmp/cov_html/index.html')


@task
def create(ctx, env):
    zappa(ctx, 'deploy', env, resource_suffix(env))
    certify(ctx, env)


@task
def certify(ctx, env):
    zappa(ctx, 'certify', env, resource_suffix(env))


@task
def delete(ctx, env):
    zappa(ctx, 'undeploy', env, resource_suffix(env))


@task
def update(ctx, env):
    zappa(ctx, 'update', env, resource_suffix(env))


@task
def tail(ctx, env):
    zappa(ctx, 'tail', env, resource_suffix(env))


@task
def build_attach_policy(ctx, env):
    output_filename = 'tmp/attach_policy.json'

    with open(output_filename, 'wt') as f:
        f.write(
            attach_policy_json(
                region=config[env][REGION],
                acct_id=config[env][ACCT_ID]
            )
        )

    print(f"Wrote {output_filename}")


@task
def build_zappa_settings(ctx, env, resource_suffix, username):
    output_filename = 'tmp/zappa_settings.yaml'

    with open(output_filename, 'wt') as f:
        f.write(
            generate_zappa_settings(
                template='settings/zappa_settings_template.yaml',
                resource_suffix=resource_suffix,
                region=config[env][REGION],
                username=username
            )
        )

    print(f"Wrote {output_filename}")


def zappa(ctx, cmd, env, resource_suffix):
    build_attach_policy(ctx, env)
    build_zappa_settings(ctx, env, resource_suffix, user())
    stage = f'dev_{user()}' if env == 'dev' else env
    zappa_cmd = f"zappa {cmd} {stage} -s tmp/zappa_settings.yaml"
    if cmd == 'certify' or cmd == 'undeploy':
        zappa_cmd += ' --yes'
    ctx.run(zappa_cmd, pty=True)


def user():
    return re.sub('\.', '', os.environ.get('USER'))


def resource_suffix(env):
    return f'dev-{user()}' if env == 'dev' else env
