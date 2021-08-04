#!/usr/bin/env python
#
# changes atlassian account nickname to mailbox (sample of how atlassian api can be used)
#
# reference: https://developer.atlassian.com/cloud/admin/rest-apis/
#
# BB_API_KEY: https://admin.atlassian.com - select your organization - Settings - API keys

import os
import json
import requests
import argparse

base_url = 'https://api.atlassian.com'
api_key = os.environ.get('BB_API_KEY')

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--update', dest='update', action='store_true')
args = parser.parse_args()

def api_request(method, url, token, data = {}):
    headers = {
       "Accept": "application/json",
       "Content-Type": "application/json",
       "Authorization": "Bearer " + token
    }
    response = requests.request(method, url, data=data, headers=headers)
    if ('application/json' in response.headers.get('Content-Type')):
        return response.json()
    print(response.text)
    raise ValueError

def api_get(url, token):
    response = api_request('GET', url, token)
    if('next' in response.get('links',{})):
        result = response['data']
        while ('next' in response.get('links',{})):
            response = api_request('GET', response['links']['next'], token)
            result += response['data']
        return result
    return response

def is_bitbucket(user):
    if([e for e in user['product_access'] if e['name'] == 'Bitbucket']):
        return True
    return False

org_id=api_request('GET', base_url + '/admin/v1/orgs', api_key)['data'][0]['id']
org_users=api_get(base_url +'/admin/v1/orgs/' + org_id + '/users', api_key)

for user in org_users:
    if (user['account_status'] == 'active' and is_bitbucket(user)):
        profile = api_request('GET', base_url + '/users/' + user['account_id'] + '/manage/profile', api_key)
        if (args.update):
            result = 'unknown'
            public_name = profile['account']['email'].split('@')[0]
            if (profile['account']['nickname'] != public_name):
                payload = json.dumps({"nickname": public_name})
                response = api_request('PATCH', base_url + '/users/' + user['account_id'] + '/manage/profile', api_key, data=payload)
                if (response['account']['nickname'] == public_name):
                    result = 'updated'
                else:
                    result = 'failed'
            else:
                result = 'unaffected'
            print("{} {} {}".format(user['account_id'], profile['account']['email'], result))
        else:
            print("{0:50s} {1:40s} {2:40s}".format(user['account_id'], profile['account']['email'], profile['account']['nickname']))

