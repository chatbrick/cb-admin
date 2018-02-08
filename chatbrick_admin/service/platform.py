import logging
from json import loads

import requests
from bson.json_util import dumps
from flask import request, session

from chatbrick_admin import app, mongo3
from chatbrick_admin.util.trans import as_json, get_facebook_account, publish

logger = logging.getLogger(__name__)


@app.route('/api/brick/<brick_id>/telegram/<telegram_token>/', methods=['PUT', 'DELETE'])
@as_json
def set_token_to_telegram(brick_id, telegram_token):
    if request.method == 'PUT':
        result = mongo3.db.facebook.update_one({'id': brick_id}, {'$set': {'telegram.token': telegram_token}},
                                               upsert=False)
        if result.matched_count:
            result_of_register = requests.post(url='https://api.telegram.org/bot%s/setWebhook' % telegram_token, data={
                'url': 'https://www.chatbrick.io/webhooks/%s/tg/' % brick_id
            })
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'telegram': result_of_register.json(),
                    'published': publish(brick_id)
                }
            }
    elif request.method == 'DELETE':
        result = mongo3.db.facebook.update_one({'id': brick_id}, {'$set': {'telegram.token': ''}},
                                               upsert=False)
        if result.matched_count:
            result_of_register = requests.post(url='https://api.telegram.org/bot%s/deleteWebhook' % telegram_token)
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'telegram': result_of_register.json(),
                    'published': publish(brick_id)
                }
            }
    return {
        'success': False,
        'action': 'ERR0002',
        'msg': '브릭이 존재하지 않습니다.'
    }


@app.route('/api/brick/<brick_id>/facebook/<page_id>/<access_token>/', methods=['PUT'])
@as_json
def set_token_to_facebook(brick_id, page_id, access_token):
    if request.method == 'PUT':
        result = mongo3.db.facebook.update_one({'id': brick_id},
                                               {'$set': {'page_id': page_id, 'access_token': access_token}},
                                               upsert=False)
        if result.matched_count:
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'published': publish(brick_id)
                }
            }
    return {
        'success': False,
        'action': 'ERR0002',
        'msg': '브릭이 존재하지 않습니다.'
    }


@app.route('/api/brick/<brick_id>/facebook/', methods=['DELETE'])
@as_json
def delete_token_to_facebook(brick_id):
    if request.method == 'DELETE':
        result = mongo3.db.facebook.update_one({'id': brick_id},
                                               {'$set': {'page_id': '', 'access_token': ''}},
                                               upsert=False)
        if result.matched_count:
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'published': publish(brick_id)
                }
            }
    return {
        'success': False,
        'action': 'ERR0002',
        'msg': '브릭이 존재하지 않습니다.'
    }


@app.route('/api/user/platform/', methods=['GET'])
@as_json
def get_users_connected_platforms():
    if request.method == 'GET':
        if 'fb_id' in session:
            rslt_data = {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {

                }
             }

            result = mongo3.db.facebook.find({
                'user_id': session['fb_id']
            }, {
                'name': True,
                'page_id': True
            })

            if result:
                rslt_data['data']['registered_page_list'] = result

            return rslt_data
        else:
            return {
                'success': False,
                'action': 'ERR0001',
                'msg': '로그인 상태가 아닙니다.'
            }

@app.route('/api/user/platform/brick/<brick_id>/', methods=['GET'])
@as_json
def get_users_connected_platforms_by_id(brick_id):
    if request.method == 'GET':
        if 'fb_id' in session:
            rslt_data = {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                }
            }
            result = mongo3.db.facebook.find({
                'user_id': session['fb_id']
            }, {
                'id': True,
                'name': True,
                'page_id': True,
            })

            tg_result = mongo3.db.facebook.find_one({
                'user_id': session['fb_id'],
                'id': brick_id
            }, {
                'telegram.token': True
            })

            if result:
                rslt_data['data']['registered_page_list'] = result

            if 'telegram' in tg_result:
                if 'token' in tg_result['telegram']:
                    token = tg_result['telegram']['token']
                    if token is not None and token.strip() != '':
                        res = requests.get('https://api.telegram.org/bot%s/getMe' % token)
                        rslt_data['data']['telegram'] = res.json().get('result', {})

            return rslt_data

        else:
            return {
                'success': False,
                'action': 'ERR0001',
                'msg': '로그인 상태가 아닙니다.'
            }
