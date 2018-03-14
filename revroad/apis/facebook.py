import logging

import requests
from django.conf import settings


def debug_facebook_access_token(token):
    try:
        r = requests.get('https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'.format(
            token, settings.FB_APP_ID, settings.FB_APP_SECRET)).json()
        # print('verify_facebook_access_token', r)
        if r['data']['app_id'] == settings.FB_APP_ID and r['data']['user_id']:
            return r['data']['user_id']
    except:
        # print('debug_facebook_access_token: Error')
        pass


def get_user_info(token, include_friends=False):
    try:
        fields = 'id,first_name,last_name,email,picture.type(large),cover'
        if include_friends:
            fields += ',friends'
        return requests.get('https://graph.facebook.com/me?access_token={}&fields={}'.format(token, fields)).json()
    except:
        logging.exception('get_user_info error')
    logging.debug('get_user_info exiting')
