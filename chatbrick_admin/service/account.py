import logging

from flask import request, session

from chatbrick_admin import app
from chatbrick_admin.util.trans import as_json, get_facebook_account

logger = logging.getLogger(__name__)


@app.route('/api/login/', methods=['POST', 'DELETE', 'GET'])
@as_json
def brick_login():
    if request.method == 'POST':
        fb_id = request.form.get('fb_id', False)
        fb_profile = request.form.get('fb_profile', False)
        fb_name = request.form.get('fb_name', False)
        fb_access_token = request.form.get('fb_access_token', False)
        fb_signed_request = request.form.get('fb_signed_request', False)

        logger.info(fb_id)
        if fb_id:
            session['fb_id'] = fb_id
            session['fb_profile'] = fb_profile
            session['fb_name'] = fb_name
            session['fb_access_token'] = fb_access_token
            session['fb_signed_request'] = fb_signed_request
            return {
                'success': True,
                'facebook': get_facebook_account(),
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
            'msg': '로그인 상태가 아닙니다.'
        }

    return {
        'success': False,
        'action': 'ERR0001',
        'msg': '로그인 실패했습니다.'
    }
