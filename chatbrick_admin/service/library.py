import logging
import os
import uuid

import requests
from bs4 import BeautifulSoup
from flask import request, url_for, send_from_directory
from werkzeug.utils import secure_filename

from chatbrick_admin import app
from chatbrick_admin.util.trans import allowed_file, as_json

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
                'msg': '파일이 존재하지 않습니다.'
            }
        file = request.files['file']
        if file.filename == '':
            return {
                'success': False,
                'msg': '선택된 파일이 없습니다.'
            }
        if file and allowed_file(file.filename):
            filename = '%s_%s' % (str(uuid.uuid4()), secure_filename(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return {
                'success': True,
                'data': {
                    'url': '%s://www.chatbrick.io%s' % (request.scheme, url_for('uploaded_file', filename=filename))
                }
            }


@app.route('/api/meta/', methods=['GET'])
@as_json
def get_metas():
    portfolio = request.args.get('url', False)

    if portfolio:
        res_data = {
            'url': portfolio
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

        return res_data
    else:
        return {
            'success': False,
            'action': 'ERR0002',
            'msg': '정상 URL이 아닙니다.'
        }
