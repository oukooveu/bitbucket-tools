#!/usr/bin/env python
#
# bulk rename of repositories in bitbucket
#
# supported environment variables:
#   BB_USER: login or user's workspace ID
#   BB_PASSWORD: password or https://bitbucket.org/account/settings/app-passwords

import os
import json
import argparse
import re
import requests
from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', default=os.environ.get('BB_USER'), help='login or user workspace ID')
parser.add_argument('-p', '--password', default=os.environ.get('BB_PASSWORD'), help='user or application password')
parser.add_argument('-w', '--workspace', help='workspace to look for repositories', required=True)
parser.add_argument('-s', '--search', help='search regex pattern (raw string)', required=True)
parser.add_argument('-r', '--replace', help='replacement regex pattern (raw string)', required=True)
parser.add_argument('--project', action='append', default=[], help='project keys')
parser.add_argument('--run', dest='run', action='store_true')
parser.add_argument('--no-run', dest='run', action='store_false')
parser.set_defaults(run=False)
args = parser.parse_args()

if not args.user or not args.password:
    exit(parser.print_usage())

base_url = 'https://api.bitbucket.org/2.0/repositories/' + args.workspace

def bitbucket_api(url, user, password, data={}):
    try:
        if(len(data) == 0):
            resp = requests.get(url, auth=(user, password))
        else:
            resp = requests.put(url, auth=(user, password), data=payload)
        resp.raise_for_status()
        if ('application/json' in resp.headers.get('Content-Type')):
            return resp.json()
        else:
            return {}
    except HTTPError as http_err:
        print(f'error (http): {http_err}')
    except Exception as err:
        print(f'error: {err}')

get_url = base_url
if(args.project):
    get_url += '?role=member&'
    get_url += 'q=' + ' AND '.join(['project.key = \"' + s + '"' for s in args.project])

response = bitbucket_api(get_url, args.user, args.password)
if response.get('type','') == 'error':
    print('error: request has been failed')
    exit(response)
repositories = response['values']

while ('next' in response):
    response = bitbucket_api(response['next'], args.user, args.password)
    repositories += response['values']

status = 'DRY RUN'
print("{0:10s} {1:40s} {2:40s} {3:10s}".format('project', 'repository (old)', 'repository (new)', 'status'))
for r in repositories:
    new_name = re.sub(r'{}'.format(args.search),r'{}'.format(args.replace),r['name'])
    if(args.run):
        payload = {'name': new_name}
        status = 'OK'
        response = bitbucket_api(base_url + '/' + r['name'], args.user, args.password, payload)
        if response.get('name', '') != new_name:
            status = 'FAILED'
    print("{0:10s} {1:40s} {2:40s} {3:10s}".format(r['project']['key'], r['name'], new_name, status))
