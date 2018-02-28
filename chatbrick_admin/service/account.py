import logging
import requests

from flask import request, session

from chatbrick_admin import app
from chatbrick_admin.util.trans import as_json, get_facebook_account

logger = logging.getLogger(__name__)


@app.route('/api/login/', methods=['POST', 'DELETE', 'GET', 'PUT'])
@as_json
def brick_login():
    try:
        if request.method == 'POST':
            if request.form.get('test', False):
                session['fb_id'] = 'test'
                session['fb_profile'] = ''
                session['fb_name'] = ''
                session['fb_access_token'] = ''
                return {
                    'success': True,
                    'facebook': get_facebook_account(),
                    'is_test': True
                }

            fb_access_token = request.form.get('fb_access_token', False)
            data = {
                'client_id': '134243977372890',
                'client_secret': '37f41797e0e6c53677f185817d08589f',
                'short_access_token': fb_access_token,
                'redirect_url': 'https://www.chatbrick.io'
            }
            res = requests.get(
                'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={client_id}&client_secret={client_secret}&fb_exchange_token={short_access_token}'.format(
                    **data))

            fb_long_lived_access_token = res.json()['access_token']
            data['long_access_token'] = fb_long_lived_access_token

            profile_res = requests.get(
                'https://graph.facebook.com/v2.12/me?fields=id,name&access_token=%s' % fb_long_lived_access_token
            )

            fb_id = profile_res.json()['id']
            fb_name = profile_res.json()['name']

            profile_image_res = requests.get(
                'https://graph.facebook.com/v2.12/%s/picture?access_token=%s&redirect=false' % (fb_id, fb_long_lived_access_token),
                headers={
                    'Content-Type': 'application/json'
                }
            )

            code_res = requests.get(
                'https://graph.facebook.com/oauth/client_code?access_token={long_access_token}&client_secret={client_secret}&redirect_uri={redirect_url}&client_id={client_id}'.format(
                    **data))

            fb_code = code_res.json()['code']
            fb_profile = profile_image_res.json()['data']['url']

            if fb_id:
                session['fb_id'] = fb_id
                session['fb_profile'] = fb_profile
                session['fb_name'] = fb_name
                session['fb_access_token'] = fb_long_lived_access_token

                return {
                    'success': True,
                    'facebook': get_facebook_account(),
                    'code': fb_code
                }
        elif request.method == 'DELETE':
            if 'fb_id' in session:
                session.clear()
            return {
                'success': True
            }
        elif request.method == 'GET':
            if 'fb_id' in session:
                return {
                    'success': True,
                    'facebook': get_facebook_account(),
                }

            return {
                'success': False,
                'action': 'ERR0001',
                'msg': '로그인 상태가 아니에요.'
            }
        elif request.method == 'PUT':
            fb_access_token = request.form.get('fb_client_access_token', False)
            session['fb_client_access_token'] = fb_access_token
            return {
                'success': True,
                'facebook': get_facebook_account(),
            }

        return {
            'success': False,
            'action': 'ERR0001',
            'msg': '로그인 실패했어요.'
        }
    except Exception as ex:
        return {
            'success': False,
            'action': 'ERR0002',
            'msg': '에러가 발생했어요.\n에러 사유: %s' % str(ex)
        }
