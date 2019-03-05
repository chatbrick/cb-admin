import logging

import requests
from flask import request, session

from chatbrick_admin import app, mongo3
from chatbrick_admin.util.trans import as_json, get_facebook_account, publish

logger = logging.getLogger(__name__)


@app.route('/api/brick/<brick_id>/telegram/<telegram_token>/', methods=['PUT', 'DELETE'])
@as_json
def set_token_to_telegram(brick_id, telegram_token):
    if request.method == 'PUT':
        count_token = mongo3.db.facebook.find({'telegram.token': telegram_token}).count()

        if count_token:
            return {
                'success': False,
                'action': 'ERR0002',
                'msg': '이미 등록된 토큰입니다.\n해당 토큰의 사용해제 후 사용해주세요.'
            }

        result = mongo3.db.facebook.update_one({'id': brick_id}, {'$set': {'telegram.token': telegram_token}},
                                               upsert=False)

        if result.matched_count:
            requests.get(
                url='https://www.chatbrick.io/webhooks/api/telegram/register/?token=%s&brick_id=%s' % (
                    telegram_token, brick_id))

            bot_name = mongo3.db.telegram_token.find_one({'token': telegram_token})

            if bot_name is None:
                res = requests.get('https://api.telegram.org/bot%s/getMe' % telegram_token).json()

                if res.get('result', False):
                    res = res.get('result')
                    res['token'] = telegram_token
                    bot_name = res
                    mongo3.db.telegram_token.insert_one(res)

            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'telegram': {
                        'ok': True,
                        'result': True,
                        'description': "Webhook was set"
                    },
                    'bot': bot_name,
                    'published': True
                }
            }
        else:
            return {
                'success': False,
                'action': 'ERR0002',
                'msg': '텔레그램 봇 등록 실패했어요.'
            }
    elif request.method == 'DELETE':
        result = mongo3.db.facebook.update_one({'id': brick_id}, {'$set': {'telegram.token': ''}},
                                               upsert=False)
        if result.matched_count:
            requests.get(
                url='https://www.chatbrick.io/webhooks/api/telegram/delete/?token=%s&brick_id=%s' % (
                    telegram_token, brick_id))
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'telegram': {
                        'ok': True,
                        'result': True,
                        'description': "Webhook was set"
                    },
                    'published': True
                }
            }
    return {
        'success': False,
        'action': 'ERR0002',
        'msg': '세트가 존재하지 않아요.'
    }


@app.route('/api/brick/<brick_id>/facebook/<page_id>/<access_token>/', methods=['PUT'])
@as_json
def set_token_to_facebook(brick_id, page_id, access_token):
    try:
        log_id = request.args.get('log_id', None)
        if request.method == 'PUT':
            user_inform = get_facebook_account()

            result = mongo3.db.facebook.update_one({'id': brick_id},
                                                   {'$set': {'page_id': page_id, 'access_token': access_token}},
                                                   upsert=False)
            user_id = user_inform.get('fb_id')

            if result.matched_count:
                return {
                    'success': True,
                    'facebook': user_inform,
                    'data': {
                        'matched_count': result.matched_count,
                        'modified_count': result.modified_count,
                        'published': publish(brick_id, log_id=log_id, user_id=user_id)
                    }
                }
        return {
            'success': False,
            'action': 'ERR0002',
            'msg': '세트가 존재하지 않아요.'
        }
    except:
        pass


@app.route('/api/brick/<brick_id>/facebook/', methods=['DELETE'])
@as_json
def delete_token_to_facebook(brick_id):
    try:
        log_id = request.args.get('log_id', None)

        if request.method == 'DELETE':
            user_inform = get_facebook_account()
            user_id = user_inform.get('fb_id')

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
                        'published': publish(brick_id, log_id=log_id, user_id=user_id)
                    }
                }
        return {
            'success': False,
            'action': 'ERR0002',
            'msg': '세트가 존재하지 않습니다.'
        }
    except:
        pass
    # finally:
    #     if log_id is not None and user_id is not None:
    #         save_log_on_server({
    #             'log_id': log_id,
    #             'user_id': user_id,
    #             'user-agent': request.headers.get('User-Agent', None),
    #             'api_code': 'delete_token_to_facebook',
    #             'api_provider_code': 'facebook',
    #             'origin': 'admin_server',
    #             'start': task_start,
    #             'end': int(time.time() * 1000),
    #             'remark': '챗브릭 서버에 페이스북 페이지 정보 삭제'
    #
    #         })


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
                'msg': '로그인 상태가 아니에요'
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
                'msg': '로그인 상태가 아니에요.'
            }
