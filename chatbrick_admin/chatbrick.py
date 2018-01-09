from flask import request, render_template
from chatbrick_admin import app, mongo3
from bson.json_util import dumps
from bson.objectid import ObjectId


@app.route('/brick/<brick_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def brick_by_id(brick_id):
    if request.method == 'GET':
        return render_template('brick.html', brick=mongo3.db.facebook.find_one_or_404({'_id': ObjectId(brick_id)}))
    elif request.method == 'POST':
        return ''


@app.route('/brick/', methods=['GET', 'POST'])
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
