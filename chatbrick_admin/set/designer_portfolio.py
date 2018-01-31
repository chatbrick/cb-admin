import requests
from bs4 import BeautifulSoup
from chatbrick_admin.set.template import Container, FacebookBrick, FacebookGeneralAction
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
                                                   Element(title='Contact',
                                                           subtitle='%s님에게 이메일을 보내고 싶은가요?' % self.data['basic'][
                                                               'name'],
                                                           buttons=[PostBackButton(payload='CONTACT',
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
                                    PostBackButton(title='Summary', payload='VIEW_USERS_SUMMARY'),
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

        # Work / 2.1.1
        if len(self.data['work']):
            work_element = [
                Element(title='Work',
                        subtitle='%s님의 경력 사항입니다.' % self.data['basic']['name'],
                        image_url=WORK_IMAGE_URL)
            ]

            for work in self.data['work']:
                work_element.append(Element(title=work['name'], subtitle='{period}\n{field}'.format(**work)))

            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_USERS_WORK', actions=[
                FacebookGeneralAction(message=Message(
                    attachment=TemplateAttachment(
                        payload=ListTemplate(elements=work_element, top_element_style='LARGE', buttons=[
                            PostBackButton(title='Menu', payload='get_started')
                        ])
                    )
                ))
            ]))
        else:
            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_USERS_WORK', actions=[
                FacebookGeneralAction(message=Message(text='%s님이 아직 Work 항목을 입력하지 않았습니다.' % self.data['basic']['name']))
            ]))

        # Specialties / 2.1.2
        if len(self.data['specialties']):
            special_element = [
                Element(title='Specialties',
                        subtitle='%s님의 보유기술 및 능력입니다.' % self.data['basic']['name'],
                        image_url=SPECIALTIES_IMAGE_URL)
            ]

            for special in self.data['specialties']:
                special_element.append(Element(title=special['name'], subtitle=special['detail']))

            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_USERS_SPECIALTIES', actions=[
                FacebookGeneralAction(message=Message(
                    attachment=TemplateAttachment(
                        payload=ListTemplate(elements=special_element, top_element_style='LARGE', buttons=[
                            PostBackButton(title='Menu', payload='get_started')
                        ])
                    )
                ))
            ]))
        else:
            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_USERS_SPECIALTIES', actions=[
                FacebookGeneralAction(
                    message=Message(text='%s님이 아직 Specialties 항목을 입력하지 않았습니다.' % self.data['basic']['name']))
            ]))

        # Summary / 2.1.3
        if self.data['summary']:
            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_USERS_SUMMARY', actions=[
                FacebookGeneralAction(message=Message(
                    attachment=ImageAttachment(url=SUMMARY_IMAGE_URL)
                )),
                FacebookGeneralAction(message=Message(
                    text=self.data['summary']
                ))
            ]))
        else:
            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_USERS_SUMMARY', actions=[
                FacebookGeneralAction(
                    message=Message(text='%s님이 아직 Summary 항목을 입력하지 않았습니다.' % self.data['basic']['name']))
            ]))

        # Contact / 4
        if self.data['basic'].get('email', False):
            designer_brick.append(FacebookBrick(brick_type='postback', value='CONTACT', actions=[
                FacebookGeneralAction(message=Message(
                    attachment=TemplateAttachment(
                        payload=GenericTemplate(elements=[
                            Element(title='Contact',
                                    subtitle='자세한 문의는 아래의 메일보내기 버튼을 이용해주세요.',
                                    image_url=CONTACT_IMAGE_URL,
                                    buttons=[
                                        PostBackButton(title='Send E-Mail',
                                                       payload='SEND_EMAIL_TO_USER')
                                    ]
                                    )
                        ])
                    )
                ))
            ]))
        else:
            designer_brick.append(FacebookBrick(brick_type='postback', value='CONTACT', actions=[
                FacebookGeneralAction(
                    message=Message(text='%s님이 아직 이메일을 입력하지 않았습니다.' % self.data['basic']['name']))
            ]))

        if self.data.get('portfolio', False) and self.data['portfolio']:
            temp_element = []

            for portfolio in self.data['portfolio'][:10]:
                res = requests.get(portfolio,
                                   headers={
                                       'User-Agent': 'TelegramBot (like TwitterBot)',
                                       'Accept': 'text/html'
                                   })

                soup = BeautifulSoup(res.text, 'lxml')

                temp_element.append(Element(title=soup.find('meta', {'property': 'og:title'}).get('content'),
                                            subtitle=soup.find('meta', {'property': 'og:description'}).get('content'),
                                            image_url=soup.find('meta', {'property': 'og:image'}).get('content'),
                                            buttons=[
                                                UrlButton(title='View', url=portfolio)
                                            ]
                                            ))

            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_PORTFOLIO', actions=[
                FacebookGeneralAction(message=Message(
                    attachment=TemplateAttachment(
                        payload=GenericTemplate(elements=temp_element)
                    )
                ))
            ]))
        else:
            designer_brick.append(FacebookBrick(brick_type='postback', value='VIEW_PORTFOLIO', actions=[
                FacebookGeneralAction(
                    message=Message(text='%s님이 아직 Portfolio 항목을 입력하지 않았습니다.' % self.data['basic']['name']))
            ]))

        return designer_brick

    def to_data(self):
        return Container(name=self.req['name'], desc=self.req['desc'], persistent_menu=PERSISTENT_MENU,
                         bricks=self.make_the_bricks(),
                         user_id=self.fb_id, type='portfolio', id=self.req.get('id', None)).to_data()
