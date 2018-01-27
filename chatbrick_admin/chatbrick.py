import logging
import os
import uuid
from functools import wraps
from json import loads, dumps

import requests
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Response
from flask import request, render_template, session, url_for, send_from_directory
from werkzeug.utils import secure_filename

from chatbrick_admin import app, mongo3
from chatbrick_admin.set.template import Container, PERSISTENT_MENU

logger = logging.getLogger(__name__)

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
                        headers={'Access-Control-Allow-Origin': 'http://localhost:3000',
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


@app.route('/api/file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/api/file/', methods=['POST'])
@as_json
def upload_file_to_server():
    if request.method == 'POST':
        if 'file' not in request.files:
            return {
                'success': False,
                'msg': '파일이 존재하지 않습니다.'
            }
        file = request.files['file']
        if file.filename == '':
            return {
                'success': False,
                'msg': '선택된 파일이 없습니다.'
            }
        if file and allowed_file(file.filename):
            filename = '%s_%s' % (str(uuid.uuid4()), secure_filename(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return {
                'success': True,
                'data': {
                    'url': '%s://www.chatbrick.io%s' % (request.scheme, url_for('uploaded_file', filename=filename))
                }
            }


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
            'msg': '로그인 상태가 아닙니다.'
        }

    return {
        'success': False
    }


@app.route('/api/brick/', methods=['GET'])
@as_json
def get_brick():
    if 'fb_id' in session:
        return {
            'success': True,
            'facebook': get_facebook_account(),
            'data': loads(dumps(mongo3.db.facebook.find({'user_id': session['fb_id']},
                                                        {"access_token": False, "verify_token": False,
                                                         "persistent_menu": False, "bricks": False,
                                                         "telegram": False})))
        }
    return {
        'success': False,
        'msg': '로그인 상태가 아닙니다.'
    }


@app.route('/api/brick/', methods=['PUT'])
@as_json
def create_set():
    if 'fb_id' in session:
        req = request.get_json()
        set_data = req['data']
        if req['type'] == 'designer_portfolio':
            res = Container(name=req['name'], desc=req['desc'], persistent_menu=PERSISTENT_MENU, bricks=[],
                            user_id=session['fb_id'], type='portfolio')
        return res.to_data()
    return {
        'success': False,
        'msg': '로그인 상태가 아닙니다.'
    }


@app.route('/api/brick/list/')
@as_json
def get_brick_list():
    return {
        'success': True,
        'facebook': get_facebook_account(),
        'data': loads(dumps(mongo3.db.brick.find({})))
    }


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
            print()
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'telegram': result_of_register.json()
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
                    'telegram': result_of_register.json()
                }
            }
    return {
        'success': False,
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
                }
            }
    return {
        'success': False,
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
                }
            }
    return {
        'success': False,
        'msg': '브릭이 존재하지 않습니다.'
    }


@app.route('/api/test/brick/<brick_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def brick_by_id(brick_id):
    if request.method == 'GET':
        return render_template('brick.html', brick=mongo3.db.facebook.find_one_or_404({'_id': ObjectId(brick_id)}))
    elif request.method == 'POST':
        return ''


@app.route('/api/test/brick/', methods=['GET', 'POST'])
def brick():
    if request.method == 'GET':
        return render_template('list.html', bricks=mongo3.db.facebook.find({}))
    elif request.method == 'POST':
        brick = {
            'name': 'unithon',
            'verify_token': 'verify_token_is...',
            'access_token': 'access_token_is...',
            'persistent_menu': [
                {
                    "whitelisted_domains": [
                        "https://api.maden.kr"
                    ],
                    "persistent_menu": [
                        {
                            "locale": "default",
                            "composer_input_disabled": False,
                            "call_to_actions": [
                                {
                                    "type": "postback",
                                    "title": "유니톤 참가(예정)",
                                    "payload": "UNITHON_REGISTER_MENU"
                                }
                                ,
                                {
                                    "type": "postback",
                                    "title": "유니톤 후원문의",
                                    "payload": "UNITHON_SPONSORSHIP_MENU"
                                }
                                ,
                                {
                                    "type": "postback",
                                    "title": "흥보문의 및 기타",
                                    "payload": "UNITHON_PROMOTION_MENU"
                                }
                            ]
                        }
                    ],
                    "get_started": {
                        "payload": "get_started"
                    }
                    ,
                    "home_url": {
                        "url": "https://api.maden.kr",
                        "webview_height_ratio": "tall",
                        "webview_share_button": "show",
                        "in_test": True
                    }
                }
            ],
            'bricks': [
                {
                    'type': 'quick_reply',
                    'value': 'send_action',
                    'actions': [
                        {
                            'message': {
                                "attachment": {
                                    "type": "template",
                                    "payload": {
                                        "template_type": "open_graph",
                                        "elements": [
                                            {
                                                "url": "https://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb",
                                                "buttons": [
                                                    {
                                                        "type": "web_url",
                                                        "url": "https://en.wikipedia.org/wiki/Rickrolling",
                                                        "title": "View More"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    ],
                    'conditions': [

                    ]
                },
                {
                    'type': 'fallback',
                    'value': 'payload_value',
                    'actions': [

                    ],
                    'conditions': [

                    ]
                },
                {
                    'type': 'postback',
                    'value': 'get_started',
                    'actions': [
                        {
                            'message': {
                                'text': 'hello, world'
                            }
                        },
                        {
                            'message': {
                                'text': 'Hi'
                            }
                        }
                    ],
                    'conditions': [

                    ]
                },
                {
                    'type': 'text',
                    'value': 'hi',
                    'actions': [

                    ],
                    'conditions': [

                    ]
                }
            ]
        }

        return dumps(mongo3.db.facebook.insert_one(brick))
