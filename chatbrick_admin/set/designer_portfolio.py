from chatbrick_admin.set.template import Container, FacebookBrick, FacebookGeneralAction
from blueforge.apis.facebook import Message, TemplateAttachment, ListTemplate, Element, PostBackButton, GenericTemplate

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
                        "payload": "VIEW_PROFILE"
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


class DesignerPortfolio(object):
    def __init__(self, fb_id, req):
        self.fb_id = fb_id
        self.req = req
        self.data = req['data']

    def make_the_bricks(self):
        designer_brick = []
        # get_started (1.1, 1.2)
        designer_brick.append(FacebookBrick(brick_type='postback', value='get_started', actions=[
            FacebookGeneralAction(message=Message(text=self.data['custom_settings']['get_started'])),
            FacebookGeneralAction(message=Message(
                attachment=TemplateAttachment(
                    payload=ListTemplate(top_element_style='LARGE',
                                         elements=[Element(title=self.data['basic']['name'],
                                                           image_url=self.data['basic']['profile_image'],
                                                           buttons=[PostBackButton(payload='VIEW_PROFILE',
                                                                                   title='View')]),
                                                   Element(title='Portfolio',
                                                           subtitle='%s님의 포트폴리오를 보고 싶은가요?' % self.data['basic']['name'],
                                                           buttons=[
                                                               PostBackButton(payload='VIEW_PORTFOLIO',
                                                                              title='View')]),
                                                   Element(title='Portfolio',
                                                           subtitle='%s님의 포트폴리오를 보고 싶은가요?' % self.data['basic'][
                                                               'name'],
                                                           buttons=[PostBackButton(payload='VIEW_PORTFOLIO',
                                                                                   title='View')])
                                                   ]
                                         )
                )
            )
            )
        ]
                                            )
                              )
        # Profile(1) / 2
        designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_PROFILE', actions=[
            FacebookGeneralAction(message=Message(
                attachment=TemplateAttachment(
                    payload=GenericTemplate(elements=[
                        Element(title=self.data['basic']['name'],
                                subtitle='{special}\n{residence}'.format(**self.data['basic']),
                                image_url=self.data['basic']['profile_image'],
                                buttons=[
                                    PostBackButton(title='Work', payload='VIEW_USERS_WORK'),
                                    PostBackButton(title='Specialties', payload='VIEW_USERS_SPECIALTIES'),
                                    PostBackButton(title='Summary', payload='VIEW_USERS_SUMMARY')
                                ],
                                default_action={
                                        'type': 'web_url',
                                        'url': self.data['basic']['social'],
                                        'webview_height_ratio': 'tall'
                                    }
                                )
                    ])
                )
            ))
        ]))

        #Profile / 2.1.1

        return designer_brick

    def to_data(self):
        return Container(name=self.req['name'], desc=self.req['desc'], persistent_menu=PERSISTENT_MENU,
                         bricks=self.make_the_bricks(),
                         user_id=self.fb_id, type='portfolio').to_data()
