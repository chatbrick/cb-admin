import dateutil.parser
import datetime

from chatbrick_admin.set.template import Container, FacebookBrick, FacebookGeneralAction
from blueforge.apis.facebook import Message, TemplateAttachment, ListTemplate, Element, PostBackButton, GenericTemplate, \
    ImageAttachment, UrlButton, ButtonTemplate


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
                        "type": "postback",
                        "title": "문의하기",
                        "payload": "CONTACT"
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


class Hackathon(object):
    def __init__(self, fb_id, req):
        self.fb_id = fb_id
        self.req = req
        self.data = req['data']

    def make_the_bricks_for_facebook(self):
        designer_brick = []
        hackathon_name = self.data['basic']['name']

        # get_started (1, 2) - 참가 신청 날짜 일 때,
        designer_brick.append(
            FacebookBrick(brick_type='postback', value='get_started', condition=[
                {
                    'type': 'date_between',
                    'data': {
                        'start_date': self.data['date']['application_period']['start'],
                        'end_data': self.data['date']['application_period']['end']
                    }
                }
            ],
                          actions=[
                              FacebookGeneralAction(message=Message(
                                  text=self.data['custom_settings']['get_started']
                              )),
                              FacebookGeneralAction(message=Message(
                                  attachment=TemplateAttachment(
                                      payload=GenericTemplate(elements=[
                                          Element(title='%s 안내' % hackathon_name,
                                                  image_url=self.data['basic']['poster_image'],
                                                  subtitle='%s에 대한 안내정보에요.' % hackathon_name,
                                                  buttons=[
                                                      PostBackButton(title='일정 및 장소안내',
                                                                     payload='VIEW_SCHEDULE_AND_PLACE'),
                                                      PostBackButton(title='참가요건',
                                                                     payload='VIEW_REQUIREMENTS'),
                                                      PostBackButton(title='시상 및 참가혜택',
                                                                     payload='VIEW_PRIZE_AND_BENEFIT')
                                                  ]),
                                          Element(title='%s 참가신청' % hackathon_name,
                                                  image_url=WORK_IMAGE_URL,
                                                  subtitle='우리 함께 %s에 참가해요.' % hackathon_name,
                                                  buttons=[
                                                      UrlButton(title='참가 신청하기', url=self.data['application']['url'])
                                                  ]),
                                          Element(image_url=WORK_IMAGE_URL,
                                                  title='문의',
                                                  subtitle='%s에 대해 궁금하신점을 말씀해주세요' % hackathon_name,
                                                  buttons=[
                                                      PostBackButton(title='문의하기', payload='CONTACT')
                                                  ]),
                                          Element(image_url=WORK_IMAGE_URL,
                                                  title='주최/주관/후원 정보',
                                                  subtitle='%s의 주최/주관/후원 정보에요.' % hackathon_name,
                                                  buttons=[
                                                      PostBackButton(title='보기', payload='VIEW_SPONSOR')
                                                  ])
                                      ])
                                  )
                              ))
                          ])
        )

        # get_started (1, 2) - 참가 신청 날짜가 아닐 때,
        designer_brick.append(
            FacebookBrick(brick_type='postback', value='get_started', condition=[
                {
                    'type': 'date_not_between',
                    'data': {
                        'start_date': self.data['date']['application_period']['start'],
                        'end_data': self.data['date']['application_period']['end']
                    }
                }
            ],
                          actions=[
                              FacebookGeneralAction(message=Message(
                                  text=self.data['custom_settings']['get_started']
                              )),
                              FacebookGeneralAction(message=Message(
                                  attachment=TemplateAttachment(
                                      payload=GenericTemplate(elements=[
                                          Element(title='%s 안내' % hackathon_name,
                                                  image_url=self.data['basic']['poster_image'],
                                                  subtitle='%s에 대한 안내정보에요.' % hackathon_name,
                                                  buttons=[
                                                      PostBackButton(title='일정 및 장소안내',
                                                                     payload='VIEW_SCHEDULE_AND_PLACE'),
                                                      PostBackButton(title='참가요건',
                                                                     payload='VIEW_REQUIREMENTS'),
                                                      PostBackButton(title='시상 및 참가혜택',
                                                                     payload='VIEW_PRIZE_AND_BENEFIT')
                                                  ]),
                                          Element(title='%s 참가신청' % hackathon_name,
                                                  image_url=WORK_IMAGE_URL,
                                                  subtitle='우리 함께 %s에 참가해요.' % hackathon_name
                                                  ),
                                          Element(image_url=WORK_IMAGE_URL,
                                                  title='문의',
                                                  subtitle='%s에 대해 궁금하신점을 말씀해주세요' % hackathon_name,
                                                  buttons=[
                                                      PostBackButton(title='문의하기', payload='CONTACT')
                                                  ]),
                                          Element(image_url=WORK_IMAGE_URL,
                                                  title='주최/주관/후원 정보',
                                                  subtitle='%s의 주최/주관/후원 정보에요.' % hackathon_name,
                                                  buttons=[
                                                      PostBackButton(title='보기', payload='VIEW_SPONSOR')
                                                  ])
                                      ])
                                  )
                              ))
                          ])
        )

        # 일정 및 장소안내 / 3.1
        place_button = [
            PostBackButton(title='본행사 장소보기',
                           payload='VIEW_PLACE_OF_MAIN_MEETING')
        ]

        if self.data['place'].get('pre-meeting', False):
            place_button.insert(0, PostBackButton(title='사전일정 장소보기',
                                                  payload='VIEW_PLACE_OF_PRE_MEETING'))

        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='VIEW_SCHEDULE_AND_PLACE',
                actions=[
                    FacebookGeneralAction(
                        message=Message(
                            attachment=TemplateAttachment(
                                payload=GenericTemplate(
                                    elements=[
                                        Element(image_url=WORK_IMAGE_URL,
                                                title='%s의 진행 일정정보에요.' % hackathon_name,
                                                buttons=[
                                                    # 4
                                                    PostBackButton(title='일정보기',
                                                                   payload='VIEW_SCHEDULE')
                                                ]),
                                        Element(image_url=WORK_IMAGE_URL,
                                                title='%s이 진행되는 장소에요.' % hackathon_name,
                                                buttons=place_button)
                                    ]
                                )
                            )
                        )
                    )
                ]
            )
        )

        # 일정안내(1) / 4
        schedule_action = [
            FacebookGeneralAction(
                message=Message(
                    attachment=ImageAttachment(
                        url=self.data['basic']['poster_image']
                    )
                )
            ),
            FacebookGeneralAction(
                message=Message(
                    text='참가 신청 일정\n%s ~ %s' % (self.data['date']['application_period']['start'],
                                                self.data['date']['application_period']['end'])
                )
            )
        ]

        if self.data['contents'].get('pre-meeting', False):
            schedule_action.insert(1, FacebookGeneralAction(
                message=Message(
                    text='사전일정\n:%s\n사전일정 내용\n:%s' % (self.data['date']['pre-meeting'],
                                                      self.data['contents']['pre-meeting'])
                )
            ))

        now_date = dateutil.parser.parse(self.data['date']['main-meeting']['start'])
        for idx, content in enumerate(self.data['contents']['main-meeting']):
            if (idx+1) == len(self.data['contents']['main-meeting']):
                schedule_action.append(
                    FacebookGeneralAction(
                        message=Message(
                            attachment=TemplateAttachment(
                                payload=ButtonTemplate(
                                    text='본행사 %d년 %d월 %d일\n%s' % (now_date.year, now_date.month, now_date.day, content),
                                    buttons=[
                                        UrlButton(title='참가신청하기', url=self.data['application']['url'])
                                    ]
                                )
                            )
                        )
                    )
                )
            else:
                schedule_action.append(
                    FacebookGeneralAction(
                        message=Message(
                            text='본행사 %d년 %d월 %d일\n%s' % (now_date.year, now_date.month, now_date.day, content)
                        )
                    )
                )

            now_date = now_date + datetime.timedelta(days=1)

        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='VIEW_SCHEDULE',
                actions=schedule_action
            )
        )

        # 사전일정 장소안내 / 5
        if self.data['place'].get('pre-meeting', False):
            designer_brick.append(
                FacebookBrick(
                    brick_type='postback',
                    value='VIEW_PLACE_OF_PRE_MEETING',
                    actions=[
                        FacebookGeneralAction(
                            message=Message(
                                attachment=TemplateAttachment(
                                    payload=ButtonTemplate(
                                        text='{name}\n{address}'.format(**self.data['place']['pre-meeting']),
                                        buttons=[
                                            UrlButton(
                                                title='지도보기',
                                                url=self.data['place']['pre-meeting']['url']
                                            )
                                        ]
                                    )
                                )
                            )
                        )
                    ]
                )
            )

        # 본행사 장소안내 / 6
        if self.data['place'].get('main-meeting', False):
            designer_brick.append(
                FacebookBrick(
                    brick_type='postback',
                    value='VIEW_PLACE_OF_MAIN_MEETING',
                    actions=[
                        FacebookGeneralAction(
                            message=Message(
                                attachment=TemplateAttachment(
                                    payload=ButtonTemplate(
                                        text='{name}\n{address}'.format(**self.data['place']['main-meeting']),
                                        buttons=[
                                            UrlButton(
                                                title='지도보기',
                                                url=self.data['place']['main-meeting']['url']
                                            )
                                        ]
                                    )
                                )
                            )
                        )
                    ]
                )
            )

        # 참여요건 / 7
        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='VIEW_REQUIREMENTS',
                actions=[
                    FacebookGeneralAction(
                        message=Message(
                            text=self.data['application']['requirements']
                        )
                    ),
                    FacebookGeneralAction(
                        message=Message(
                            attachment=TemplateAttachment(
                                payload=ButtonTemplate(
                                    text=self.data['application']['preparation'],
                                    buttons=[
                                        UrlButton(title='참가신청하기', url=self.data['application']['url'])
                                    ]
                                )
                            )
                        )
                    )
                ]
            )
        )

        # 시상 및 참가혜택 / 8
        prize_text = '시상\n======================\n'
        for prize in self.data['prize']:
            prize_text += '{name} / {desc} / {benefit}\n'.format(**prize)

        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='VIEW_PRIZE_AND_BENEFIT',
                actions=[
                    FacebookGeneralAction(
                        message=Message(
                            text=prize_text
                        )
                    ),
                    FacebookGeneralAction(
                        message=Message(
                            attachment=TemplateAttachment(
                                payload=ButtonTemplate(
                                    text=self.data['benefit_of_participant'],
                                    buttons=[
                                        UrlButton(title='참가신청하기', url=self.data['application']['url'])
                                    ]
                                )
                            )
                        )
                    )
                ]
            )
        )

        # 문의하기 / 10
        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='CONTACT',
                actions=[
                    FacebookGeneralAction(
                        message=Message(
                            text='문의사항은 아래의 메일 / 전화를 이용해주세요.\n{email}\n{tel}'.format(**self.data['basic'])
                        )
                    )
                ]
            )
        )

        # 주최/주관/후원정보 / 11
        sponsor_text = []

        thanks = self.data['thanks']

        if thanks.get('hoster', False):
            if thanks['hoster'].strip() != '':
                sponsor_text.append('주최\n:%s' % thanks['hoster'])

        if thanks.get('organizer', False):
            if thanks['organizer'].strip() != '':
                sponsor_text.append('주관\n:%s' % thanks['organizer'])

        if thanks.get('sponsor', False):
            if thanks['sponsor'].strip() != '':
                sponsor_text.append('협찬\n:%s' % thanks['sponsor'])

        designer_brick.append(
            FacebookBrick(
                brick_type='postback',
                value='VIEW_SPONSOR',
                actions=[
                    FacebookGeneralAction(
                        message=Message(
                            attachment=ImageAttachment(url=WORK_IMAGE_URL)
                        )
                    ),
                    FacebookGeneralAction(
                        message=Message(
                            text='\n\n'.join(sponsor_text)
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
                         user_id=self.fb_id, type='hackathon', id=self.req.get('id', None)).to_data()
