import datetime
import logging
import math
import uuid

import httpagentparser
import pymongo
from flask import request, render_template
from openpyxl import Workbook

from chatbrick_admin import app, mongo3
from chatbrick_admin.util.trans import as_json, get_facebook_account

logger = logging.getLogger(__name__)


@app.route('/api/log/', methods=['PUT'])
@as_json
def save_log_to_server():
    req_json = request.get_json()
    if 'log_id' not in req_json:
        raise RuntimeError('로그 ID 값이 존재하지 않습니다.')

    if 'start' not in req_json:
        raise RuntimeError('시작 시간이 존재하지 않습니다.')

    if 'end' not in req_json:
        raise RuntimeError('종료 시간이 존재하지 않습니다.')

    if 'task_code' not in req_json and 'api_code' not in req_json:
        raise RuntimeError('Task 코드나 API 코드 중 하나는 존재해야합니다.')

    if req_json.get('user_id') is None or str(req_json.get('user_id')).strip() == '':
        req_json['user_id'] = get_facebook_account().get('fb_id', 'No_ID')

    req_json['user-agent'] = request.headers.get('User-Agent', None)

    mongo3.db.log.insert_one(req_json)

    return {
        'success': True
    }


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    try:
        if type(date) is str:
            date = float(date)
        parsed_date = datetime.datetime.fromtimestamp(date / 1000.0)
        # parsed_date = parsed_date.replace(tzinfo=pytz.timezone('Asia/Seoul'))
        return '%02d/%02d %02d:%02d:%02d.%s' % (
            parsed_date.month, parsed_date.day, parsed_date.hour, parsed_date.minute, parsed_date.second,
            str(parsed_date.microsecond)[:2])
    except:
        return ''


@app.route('/api/log/download/', methods=['GET'])
@as_json
def download_log():
    items = mongo3.db.log.find({}).sort([
        ('start', pymongo.DESCENDING),
        ('task_code', pymongo.DESCENDING),
        # ('start', pymongo.ASCENDING)
    ])

    result = []

    for item in items:
        if item.get('task_code', False) and item.get('task_code').strip() != '':
            if item.get('application') == 'chatbrick_web':

                item['client_start'] = item.get('start')
                item['client_end'] = item.get('end')
                try:
                    item['remain_time'] = int(item.get('end')) - int(item.get('start'))
                except:
                    item['remain_time'] = 0
            else:
                item['server_start'] = item.get('start')
                item['server_end'] = item.get('end')
                try:
                    item['remain_time'] = int(item.get('end')) - int(item.get('start'))
                except:
                    item['remain_time'] = 0

            if item.get('user-agent', False):
                item['os'], _ = httpagentparser.simple_detect(item.get('user-agent'))

            result.append(item)
    export_data = []
    for result_item in result:
        if result_item.get('client_start', False):
            result_item['start_time'] = _jinja2_filter_datetime(result_item['client_start'])
            result_item['end_time'] = _jinja2_filter_datetime(result_item['client_end'])

        elif result_item.get('server_start', False):
            result_item['start_time'] = _jinja2_filter_datetime(result_item['server_start'])
            result_item['end_time'] = _jinja2_filter_datetime(result_item['server_end'])
        else:
            result_item['start_time'] = ''
            result_item['end_time'] = ''

        export_data.append(result_item)

    result = sorted(export_data, key=lambda export_data: export_data['start_time'], reverse=True)
    file_name = '%s.xlsx' % str(uuid.uuid4())
    wb = Workbook()
    ws = wb.active
    ws.append(['생성일', '사용자아이디', 'OS', '애플리케이션', 'Function', '시작시간', '종료시간', '총소요시간(ms)'])

    for appended_item in result:
        ws.append(
            [appended_item.get('start_time', ''), appended_item.get('user_id', ''), appended_item.get('os', ''),
             appended_item.get('application', ''), appended_item.get('task_code', ''),
             appended_item.get('start_time', ''),
             appended_item.get('end_time', ''), appended_item.get('remain_time', '')])

    wb.save('%s/%s' % (app.config['UPLOAD_FOLDER'], file_name))

    return {
        'url': '/api/static/%s' % file_name
    }


@app.route('/api/log/', methods=['GET'])
def get_log():
    log_type = request.args.get('type', False)
    page_size = int(request.args.get('pagesize', 50))
    page_num = int(request.args.get('page', 1))

    start_item = (page_size * (page_num - 1)) - 1

    if page_num == 1:
        start_item = 0

    end_item = (start_item + page_size) - 1

    items = mongo3.db.log.find({}).sort([
        ('start', pymongo.DESCENDING),
        ('task_code', pymongo.DESCENDING),
        # ('start', pymongo.ASCENDING)
    ])

    if log_type == 'detail':
        result = {
        }

        for item in items:
            log_id = item.get('log_id')
            try:

                if item.get('start'):
                    item['start'] = int(item['start'])
                else:
                    item['start'] = 0
            except Exception as ex:
                item['start'] = 0

            try:
                if item.get('end'):
                    item['end'] = int(item['end'])
                else:
                    item['end'] = 0
            except Exception as ex:
                item['end'] = 0
            if log_id not in result:
                result[log_id] = {
                    'api': []
                }
            if item.get('task_code', False) and item.get('task_code').strip() != '':
                if 'task_code' not in result[log_id]:
                    result[log_id].update(item)

                if item.get('application') == 'chatbrick_web':
                    result[log_id]['client_start'] = item.get('start')
                    result[log_id]['client_end'] = item.get('end')
                    result[log_id]['remain_time'] = item.get('end') - item.get('start')
                else:
                    result[log_id]['server_start'] = item.get('start')
                    result[log_id]['server_end'] = item.get('end')

                    if not result[log_id].get('remain_time', False):
                        result[log_id]['remain_time'] = item.get('end') - item.get('start')

            else:
                if item.get('api_code', False) and item.get('api_code').strip() != '':
                    # if type(item['start']) is not int:
                    #     item['start'] = 0
                    #
                    # if type(item['end']) is not int:
                    #     item['end'] = 0
 
                    result[log_id]['api'].append(item)
        total_item = len(result.keys())
        end_page_num = total_item / page_size
        key_array = [a for a in result.keys()]
        key_array = key_array[start_item:end_item + 1]

        final_result = {}

        for key in key_array:
            final_result[key] = result[key]
        # print(final_result)

        return render_template('full_log.html', result=final_result, page={
            'end': range(1, int(end_page_num) + 1),
            'total': total_item,
            'size': page_size,
            'num': page_num,
        })

    else:

        result = []

        for item in items:
            try:

                if item.get('start'):
                    item['start'] = int(item['start'])
                else:
                    item['start'] = 0
            except Exception as ex:
                item['start'] = 0

            try:
                if item.get('end'):
                    item['end'] = int(item['end'])
                else:
                    item['end'] = 0
            except Exception as ex:
                item['end'] = 0

            if item.get('task_code', False) and item.get('task_code').strip() != '':
                if item.get('application') == 'chatbrick_web':
                    item['client_start'] = item.get('start')
                    item['client_end'] = item.get('end')
                    item['remain_time'] = item.get('end') - item.get('start')
                else:
                    # if 'task_code' not in result[item.get('log_id')]:
                    #     result[item.get('log_id')].update(item)
                    item['server_start'] = item.get('start')
                    item['server_end'] = item.get('end')

                    if not item.get('remain_time', False):
                        item['remain_time'] = item.get('end') - item.get('start')

                if item.get('user-agent', False):
                    item['os'], _ = httpagentparser.simple_detect(item.get('user-agent'))

                result.append(item)

        result = sorted(result, key=lambda result: result['start'], reverse=True)
        total_item = len(result)
        end_page_num = math.ceil(total_item / page_size)
        return render_template('log.html', result=result[start_item:end_item + 1], page={
            'end': range(1, int(end_page_num) + 1),
            'total': total_item,
            'size': page_size,
            'num': page_num
        })


@app.route('/api/log/<log_id>/', methods=['GET'])
def get_log_detail(log_id):
    result = []

    items = mongo3.db.log.find({'log_id': log_id}).sort([
        ('task_code', pymongo.DESCENDING),
    ]).sort([
        ('start', pymongo.ASCENDING)
    ])

    logger.info(items)
    for item in items:
        if item.get('api_code', False) and item.get('api_code').strip() != '':
            try:
                item['remain_time'] = int(item.get('end')) - int(item.get('start'))
            except:
                item['remain_time'] = 0
            result.append(item)

    return render_template('log_detail.html', items=result)


@app.route('/api/log/error/', methods=['POST'])
@as_json
def save_error_msg():
    req = request.get_json()
    rslt = mongo3.db.brick_error.insert_one(req)
    return {
        'success': True,
        'result': str(rslt.inserted_id)
    }
