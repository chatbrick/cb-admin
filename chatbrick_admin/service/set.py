import logging
from json import loads

from bson.json_util import dumps
from flask import request, session

from chatbrick_admin import app, mongo3
from chatbrick_admin.set import DesignerPortfolio, Hackathon, Bricks
from chatbrick_admin.util.trans import as_json, get_facebook_account, publish

logger = logging.getLogger(__name__)


@app.route('/api/brick/', methods=['GET'])
@as_json
def get_brick():
    if 'fb_id' in session:
        try:
            return {
                'success': True,
                'facebook': get_facebook_account(),
                'data': loads(dumps(mongo3.db.facebook.find({'user_id': session['fb_id']},
                                                            {"access_token": False, "verify_token": False,
                                                             "persistent_menu": False, "bricks": False,
                                                             "telegram": False,
                                                             "settings": False})))
            }
        except Exception as ex:
            return {
                'success': False,
                'action': 'ERR0002',
                'msg': '에러가 발생했어요.\n잠시 뒤에 시도해주세요.\n에러 내용: %s' % str(ex)
            }
    return {
        'success': False,
        'action': 'ERR0001',
        'msg': '로그인 상태가 아니에요.'
    }


@app.route('/api/brick/', methods=['PUT', 'PATCH'])
@as_json
def create_set():
    if 'fb_id' in session:
        try:
            req = request.get_json()
            if req.get('name') is None or len(req['name']) == 0 or len(req['name']) > 8:
                raise RuntimeError('세트 이름을 최대 8자 이내로 입력해주세요.')

            if req['type'] == 'designer_portfolio':
                res = DesignerPortfolio(fb_id=session['fb_id'], req=req).to_data()
                res['settings'] = req
            elif req['type'] == 'hackathon':
                res = Hackathon(fb_id=session['fb_id'], req=req).to_data()
                res['settings'] = req
            elif req['type'] == 'bricks':
                brick_data = mongo3.db.brick.find({})
                logger.info(brick_data)
                res = Bricks(fb_id=session['fb_id'], req=req, bricks=brick_data).to_data()
                res['settings'] = req

            if res:
                if request.method == 'PUT':
                    rslt = mongo3.db.facebook.insert_one(res)
                elif request.method == 'PATCH':
                    if 'id' in req:
                        prv_set = mongo3.db.facebook.find_one({'id': req['id']})
                        res['telegram']['token'] = prv_set['telegram']['token']

                        if prv_set.get('access_token', False):
                            res['access_token'] = prv_set['access_token']

                        if prv_set.get('page_id', False):
                            res['page_id'] = prv_set['page_id']

                        rslt = mongo3.db.facebook.update_one({'id': req['id']}, {'$set': res}, upsert=False)
                        return {
                            'success': True,
                            'data': {
                                'matched_count': rslt.matched_count,
                                'modified_count': rslt.modified_count,
                                'published': publish(res['id'])
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'action': 'ERR0002',
                            'msg': 'ID 항목이 없어요.'
                        }

            return {
                'success': True,
                'data': {
                    'inserted_ids': str(rslt.inserted_id),
                    'published': publish(res['id']),
                    'id': res['id']
                }
            }
        except Exception as ex:
            return {
                'success': False,
                'action': 'ERR0002',
                'msg': '세트 등록 실패했어요.\n실패 사유: %s' % str(ex)
            }
    else:
        return {
            'success': False,
            'action': 'ERR0001',
            'msg': '로그인 상태가 아니에요.'
        }


@app.route('/api/brick/<brick_id>/', methods=['GET', 'DELETE'])
@as_json
def select_and_delete_set(brick_id):
    try:
        if request.method == 'GET':
            result = mongo3.db.facebook.find_one({'id': brick_id}, {'persistent_menu': False, 'bricks': False})
            if result:
                if result['type'] == 'bricks':
                    if result['settings']['data'].get('brick', False):
                        if len(result['settings']['data']['brick']):
                            for idx, registerd_brick in enumerate(result['settings']['data']['brick']):
                                brick_result = mongo3.db.brick.find_one({'id': registerd_brick['id']},
                                                                        {'preview': True, 'thumb': True, 'api': True})
                                result['settings']['data']['brick'][idx].update(brick_result)

                return {
                    'success': True,
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'action': 'ERR0002',
                    'msg': '데이터가 존재하지 않아요.'
                }
        elif request.method == 'DELETE':
            result = mongo3.db.facebook.delete_one({'id': brick_id})
            if result:
                return {
                    'success': True,
                    'data': {
                        'deleted_count': result.deleted_count
                    }
                }
            else:
                return {
                    'success': False,
                    'action': 'ERR0002',
                    'msg': '데이터가 존재하지 않아 삭제를 실패했어요.'
                }
    except Exception as ex:
        return {
            'success': False,
            'action': 'ERR0002',
            'msg': '에러가 발생했어요.\n잠시 뒤에 시도해주세요.\n에러 내용: %s' % str(ex)
        }


@app.route('/api/brick/list/')
@as_json
def get_brick_list():
    return {
        'success': True,
        'facebook': get_facebook_account(),
        'data': loads(dumps(mongo3.db.brick.find({})))
    }
