import logging

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
