import logging
from math import ceil

from chatbrick_admin import mongo3
from chatbrick_admin.util.trans import get_facebook_account

logger = logging.getLogger(__name__)


def save_log_on_server(req_json):
    logger.info(req_json)
    if 'log_id' not in req_json:
        raise RuntimeError('로그 ID 값이 존재하지 않습니다.')

    if 'start' not in req_json:
        raise RuntimeError('시작 시간이 존재하지 않습니다.')

    if 'end' not in req_json:
        raise RuntimeError('종료 시간이 존재하지 않습니다.')

    if 'task_code' not in req_json and 'api_code' not in req_json:
        raise RuntimeError('Task 코드나 API 코드 중 하나는 존재해야합니다.')

    if req_json.get('user_id') is None or str(req_json.get('user_id')).strip() == '':
        req_json['user_id'] = get_facebook_account().get('fb_id')

    result = mongo3.db.log.insert_one(req_json)

    logger.info(result)
    return {
        'success': True
    }


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=0, left_current=4,
                   right_current=5, right_edge=0):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                    num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
