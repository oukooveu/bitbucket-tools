#!/usr/bin/env python
#
# returns list of the repositories from workspace (or all public repositories if workspace is missing)
#
# BB_USER: login or user's workspace ID
# BB_PASSWORD: password or https://bitbucket.org/account/settings/app-passwords
# BB_WORKSPACE: workspace to requests repositories list

import os
import json
import requests
import argparse

base_url = 'https://api.bitbucket.org/'

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', default=os.environ.get('BB_USER'), help='login or user workspace ID')
parser.add_argument('-p', '--password', default=os.environ.get('BB_PASSWORD'), help='user or application password')
parser.add_argument('-w', '--workspace', help='workspace to look for repositories')
parser.add_argument('-e', '--exclude', action='append', default=[], help='exclude project keys')
args = parser.parse_args()

if not args.user or not args.password:
    exit(parser.print_usage())

endpoint = '2.0/repositories'
if(args.workspace):
    endpoint += '/' + args.workspace
if(args.exclude):
    endpoint += '?role=member&'
    endpoint += 'q=' + ' AND '.join(['project.key != \"' + s + '"' for s in args.exclude])

def api_get(url, user, password):
    resp = requests.get(url, auth=(user, password))
    if ('application/json' in resp.headers.get('Content-Type')):
        return resp.json()
    else:
        return {}

response = api_get(base_url + endpoint, args.user, args.password)
repositories = response['values']

while ('next' in response):
    response = api_get(response['next'], args.user, args.password)
    repositories += response['values']

print("{0:60s} {1:10s} {2:40s} {3}".format('repository', 'project', 'updated on', 'size'))
for r in repositories:
    print("{0:60s} {1:10s} {2:40s} {3}".format(r['full_name'], r['project']['key'], r['updated_on'], r['size']))

