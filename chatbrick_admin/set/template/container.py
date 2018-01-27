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
            'type': self.data['type']
        }

        if 'id' not in self.data:
            data['id'] = uuid.uuid4()
        else:
            data['id'] = self.data['id']

        if 'access_token' in self.data:
            data['access_token'] = self.data['access_token']

        if 'persistent_menu' in self.data:
            data['persistent_menu'] = self.data['persistent_menu']

        if 'bricks' in self.data:
            data['bricks'] = [brick.to_data for brick in self.data['bricks']]

        if 'telegram' in self.data:
            data['telegram'] = self.data['telegram'].to_data()

        return data

