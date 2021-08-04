#!/usr/bin/env python
#
# returns list of the repositories from workspace (or all public repositories if workspace is missing)
#
# BB_USER: login or user's workspace ID
# BB_PASSWORD: password or https://bitbucket.org/account/settings/app-passwords
# BB_WORKSPACE: worspace to requests repositories list

import os
import json
import requests

base_url = 'https://api.bitbucket.org/'
user = os.environ.get('BB_USER')
password = os.environ.get('BB_PASSWORD')
workspace = os.environ.get('BB_WORKSPACE')

endpoint = '2.0/repositories'
if(workspace):
    endpoint = '2.0/repositories/' + workspace

def api_get(url, user, password):
    resp = requests.get(url, auth=(user, password))
    if ('application/json' in resp.headers.get('Content-Type')):
        return resp.json()
    else:
        return {}

response = api_get(base_url + endpoint, user, password)
repositories = response['values']

while ('next' in response):
    response = api_get(response['next'], user, password)
    repositories += response['values']

print("{0:60s} {1:40s} {2}".format('full name', 'updated on', 'size'))
for r in repositories:
    print("{0:60s} {1:40s} {2}".format(r['full_name'], r['updated_on'], r['size']))

