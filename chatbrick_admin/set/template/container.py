import uuid


class Container(object):
    def __init__(self, **kwargs):
        self.data = kwargs

    def to_data(self):
        data = {
            'name': self.data['name'],
            'persistent_menu': self.data['persistent_menu'],
            'bricks': self.data['bricks'],
            'user_id': self.data['user_id'],
            'desc': self.data['desc'],
            'type': self.data['type'],
            'telegram': {
                'token': ''
            }
        }

        if 'id' not in self.data or not self.data['id']:
            data['id'] = str(uuid.uuid4())
        else:
            data['id'] = self.data['id']

        if 'access_token' in self.data:
            data['access_token'] = self.data['access_token']

        if 'telegram' in self.data:
            data['telegram']['bricks'] = [brick.to_data() for brick in self.data['telegram']]

        if 'persistent_menu' in self.data:
            data['persistent_menu'] = self.data['persistent_menu']

        if 'bricks' in self.data:
            data['bricks'] = [brick.to_data() for brick in self.data['bricks']]

        if 'brick_data' in self.data:
            data['brick_data'] = self.data['brick_data']

        return data

