import logging
import os
import uuid
import json
import requests
from bs4 import BeautifulSoup
from flask import request, url_for, send_from_directory
from werkzeug.utils import secure_filename

from chatbrick_admin import app, mongo3
from chatbrick_admin.util.trans import allowed_file, as_json, get_facebook_account

logger = logging.getLogger(__name__)


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
                'msg': '파일이 존재하지 않아요.'
            }
        file = request.files['file']
        if file.filename == '':
            return {
                'success': False,
                'msg': '선택된 파일이 없어요.'
            }

        if file and allowed_file(file.filename):
            try:
                filename = '%s_%s' % (str(uuid.uuid4()), secure_filename(file.filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return {
                    'success': True,
                    'data': {
                        'url': '%s://www.chatbrick.io%s' % (request.scheme, url_for('uploaded_file', filename=filename))
                    }
                }
            except Exception as ex:
                return {
                    'success': False,
                    'action': 'ERR0002',
                    'msg': '에러가 발생했어요.\n잠시 후 다시 시도해주세요.\n에러 내용: %s' % str(ex)
                }
        else:
            return {
                'success': False,
                'action': 'ERR0002',
                'msg': '업로드할 수 있는 확장자가 아닙에요.\npng, jpg, jpeg, gif 중 하나를 선택하여 업로드 해주세요.'
            }


@app.route('/api/meta/', methods=['GET'])
@as_json
def get_metas():
    portfolio = request.args.get('url', False)

    if portfolio:
        try:
            res_data = {
                'url': portfolio,
                'title': '',
                'sub_title': '',
                'image_url': ''
            }

            res = requests.get(portfolio,
                               headers={
                                   'User-Agent': 'TelegramBot (like TwitterBot)',
                                   'Accept': 'text/html'
                               })

            soup = BeautifulSoup(res.text, 'lxml')

            title = soup.find('meta', {'property': 'og:title'})
            sub_title = soup.find('meta', {'property': 'og:description'})
            image_url = soup.find('meta', {'property': 'og:image'})

            if title:
                res_data['title'] = title.get('content')

            if sub_title:
                res_data['sub_title'] = sub_title.get('content')

            if image_url:
                res_data['image_url'] = image_url.get('content')

            return {
                'success': True,
                'data': res_data
            }
        except Exception as ex:
            logger.error(ex)
    return {
        'success': False,
        'action': 'ERR0002',
        'msg': '메타 데이터 가져오기가 실패했습니다.'
    }


@app.route('/api/log/', methods=['POST'])
@as_json
def save_log_to_server():
    log_type = request.form.get('log_type', 'request')
    set_id = request.form.get('set_id', '')
    brick_id = request.form.get('brick_id', '')
    platform = request.form.get('platform', '')
    start_time = request.form.get('start', '')
    end_time = request.form.get('end', '')
    data = request.form.get('data', {})
    tag = request.form.get('tag', '')
    elapsed_time = request.form.get('elapsed', '')
    fb_id = get_facebook_account().get('fb_id', '')
    remark = request.form.get('remark', '')

    if fb_id is None or fb_id.strip() == '':
        fb_id = request.form.get('fb_id', '')

    try:
        data = json.loads(data)
    except Exception as ex:
        data = request.form.get('data', {})
        logger.error(ex)

    if start_time != '' and end_time != '':
        elapsed_time = int(end_time) - int(start_time)

    rslt = mongo3.db.log.insert_one({
        'fb_id': fb_id,
        'type': log_type,
        'platform': platform,
        'set': set_id,
        'brick': brick_id,
        'start': start_time,
        'end': end_time,
        'elapsed': elapsed_time,
        'data': data,
        'tag': tag,
        'remark': remark,
    })

    logger.info(rslt)
    return {
        'success': True
    }


@app.route('/api/log/error/', methods=['POST'])
@as_json
def save_error_msg():
    req = request.get_json()
    rslt = mongo3.db.brick_error.insert_one(req)
    return {
        'success': True,
        'result': str(rslt.inserted_id)
    }
