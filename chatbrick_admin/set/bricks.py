import requests
from bs4 import BeautifulSoup
from chatbrick_admin.set.template import Container, FacebookBrick, FacebookGeneralAction, FacebookBrickAction
from blueforge.apis.facebook import Message, TemplateAttachment, ListTemplate, Element, PostBackButton, GenericTemplate, \
    ImageAttachment, UrlButton

WORK_IMAGE_URL = 'https://www.chatbrick.io/api/static/img_work_ex.png'
SPECIALTIES_IMAGE_URL = 'https://www.chatbrick.io/api/static/img_specialties.png'
SUMMARY_IMAGE_URL = 'https://www.chatbrick.io/api/static/img_summary.png'
CONTACT_IMAGE_URL = 'https://www.chatbrick.io/api/static/img_contact.png'
PERSISTENT_MENU = [
    {
        "whitelisted_domains": [
            "https://www.chatbrick.io"
        ],
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": "처음으로",
                        "payload": "get_started"
                    },
                    {
                        "type": "web_url",
                        "title": "chatbrick",
                        "url": "https://www.chatbrick.io/",
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ],
        "get_started": {
            "payload": "get_started"
        },
        "home_url": {
            "url": "https://www.chatbrick.io/",
            "webview_height_ratio": "tall",
            "webview_share_button": "show",
            "in_test": True
        }
    }
]


class Bricks(object):
    def __init__(self, fb_id, req, bricks):
        self.fb_id = fb_id
        self.req = req
        self.data = req['data']
        self.bricks = bricks

    def make_the_bricks_for_facebook(self):
        designer_brick = []
        elements = []

        for brick in self.data['brick']:
            designer_brick.append(
                FacebookBrick(
                    brick_type='postback',
                    value=brick['id'],
                    actions=[
                        FacebookBrickAction(
                            brick_id=brick['id'],
                            data=brick['data']
                        )
                    ]
                )
            )
            for keyword in brick['keywords']:
                designer_brick.append(
                    FacebookBrick(
                        brick_type='text',
                        value=keyword,
                        actions=[
                            FacebookBrickAction(
                                brick_id=brick['id'],
                                data=brick['data']
                            )
                        ]
                    )
                )
            for brick_rec in self.bricks:
                if brick_rec['id'] == brick['id']:
                    elements.append(
                        Element(
                            title=brick_rec['name'],
                            subtitle=brick_rec['api']['desc'],
                            image_url=brick_rec['img'],
                            buttons=[
                                PostBackButton(
                                    title='선택',
                                    payload=brick['id']
                                )
                            ]
                        )
                    )
                    break

        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='get_started',
                actions=[
                    FacebookGeneralAction(
                        message=Message(
                            attachment=TemplateAttachment(
                                payload=GenericTemplate(
                                    elements=elements
                                )
                            )
                        )
                    )
                ]
            )
        )

        return designer_brick

    def make_the_bricks_for_telegram(self):
        designer_brick = []

        return designer_brick

    def to_data(self):
        return Container(name=self.req['name'], desc=self.req['desc'], persistent_menu=PERSISTENT_MENU,
                         bricks=self.make_the_bricks_for_facebook(), telegram=self.make_the_bricks_for_telegram(),
                         user_id=self.fb_id, type='bricks', id=self.req.get('id', None)).to_data()
