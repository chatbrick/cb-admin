import logging

import blueforge.apis.telegram as tg
from blueforge.apis.facebook import Message, TemplateAttachment, Element, PostBackButton, GenericTemplate

from chatbrick_admin.set.template import Container, FacebookBrick, FacebookGeneralAction, FacebookBrickAction, \
    TelegramBrick, TelegramGeneralAction, TelegramBrickAction

logger = logging.getLogger(__name__)

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
        self.bricks = []
        self.brick_data = {}
        if bricks:
            for brick in bricks:
                self.bricks.append(brick)

    def make_the_bricks_for_facebook(self):
        designer_brick = []
        elements = []

        for brick in self.data['brick']:
            self.brick_data[brick['id']] = brick['data']
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
            if 'keywords' in brick:
                for keyword in brick['keywords']:
                    if len(keyword) == 0 or len(keyword) > 8:
                        raise RuntimeError('키워드를 최대 8자 이내로 입력해주세요.')

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
                    FacebookGeneralAction(message=Message(text=self.data['custom_settings']['get_started'])),
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
        temp_element = []
        description = []
        for brick in self.data['brick']:
            self.brick_data[brick['id']] = brick['data']
            designer_brick.append(
                TelegramBrick(
                    brick_type='callback',
                    value=brick['id'],
                    actions=[
                        TelegramBrickAction(
                            brick_id=brick['id'],
                            data=brick['data']
                        )
                    ]
                )
            )

            if 'keywords' in brick:
                for keyword in brick['keywords']:
                    if len(keyword) == 0 or len(keyword) > 8:
                        raise RuntimeError('키워드를 최대 8자 이내로 입력해주세요.')

                    designer_brick.append(
                        TelegramBrick(
                            brick_type='text',
                            value=keyword,
                            actions=[
                                TelegramBrickAction(
                                    brick_id=brick['id'],
                                    data=brick['data']
                                )
                            ]
                        )
                )

            for brick_rec in self.bricks:
                if brick_rec['id'] == brick['id']:
                    temp_element.append(
                        tg.CallbackButton(
                            text=brick_rec['name'],
                            callback_data=brick['id']
                        )
                    )
                    description.append(
                        '\n*[%s]*\n%s\n' % (brick_rec['name'], brick_rec['api']['desc']))
                    break

        temp_idx = 0
        temp_len = len(temp_element)
        temp_array = []
        if len(temp_element) == 1:
            temp_array.append([
                temp_element[0]
            ])
        else:
            for i in range(0, round(temp_len / 2)):
                temp_sub_array = []
                for a in range(0, 2):
                    if temp_idx == temp_len:
                        break
                    temp_sub_array.append(temp_element[temp_idx])
                    temp_idx += 1
                temp_array.append(temp_sub_array)

        designer_brick.append(
            TelegramBrick(
                brick_type='bot_command',
                value='start',
                actions=[
                    TelegramGeneralAction(
                        message=tg.SendMessage(
                            text=self.data['custom_settings']['get_started']
                        )
                    ),
                    TelegramGeneralAction(
                        message=tg.SendMessage(
                            text='*원하는 브릭을 선택해주세요.*\n%s' % '\n'.join(description),
                            parse_mode='Markdown',
                            reply_markup=tg.MarkUpContainer(
                                inline_keyboard=temp_array
                            )
                        )
                    )
                ]
            )
        )
        return designer_brick

    def to_data(self):
        return Container(name=self.req['name'], desc=self.req['desc'], persistent_menu=PERSISTENT_MENU,
                         bricks=self.make_the_bricks_for_facebook(), telegram=self.make_the_bricks_for_telegram(),
                         user_id=self.fb_id, type='bricks', brick_data=self.brick_data,
                         id=self.req.get('id', None)).to_data()
