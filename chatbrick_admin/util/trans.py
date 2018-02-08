from functools import wraps
from json import dumps

import requests
from bson.json_util import dumps
from flask import Response
from flask import session

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8',
                        headers={'Access-Control-Allow-Origin': 'http://localhost:3000 https://www.chatbrick.io',
                                 'Access-Control-Allow-Credentials': 'true'})

    return decorated_function


def cursor_to_dict(datas):
    dict_data = []
    for data in datas:
        dict_data.append(data)

    return dict_data


def get_facebook_account():
    return {
        'fb_id': session['fb_id'],
        'fb_profile': session['fb_profile'],
        'fb_name': session['fb_name'],
        'fb_access_token': session['fb_access_token'],
        'fb_signed_request': session['fb_signed_request']
    }


def publish(set_id):
    publish_res = requests.post('https://www.chatbrick.io/webhooks/refresh/%s/' % set_id)
    if publish_res.status_code == 200:
        return True
    else:
        return False