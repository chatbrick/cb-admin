

class Telegram(object):
    def __init__(self, token=None, bricks=None):
        self.token = token
        self.bricks = bricks

    def to_data(self):
        return {
            'token': self.token,
            'bricks': [brick.to_data for brick in self.bricks]
        }


class TelegramBrick(object):
    def __init__(self, brick_type, value, actions):
        self.brick_type = brick_type
        self.value = value
        self.actions = actions

    def to_data(self):
        return {
            'type': self.brick_type,
            'value': self.value,
            'actions': [action for action in self.actions]
        }


class TelegramGeneralAction(object):
    def __init__(self, method, message):
        self.method = method
        self.message = message

    def to_data(self):
        return {
            'method': self.method,
            'message': self.message.to_data()
        }


class TelegramBrickAction(object):
    def __init__(self, brick_id, input=None, data=None):
        self.id = brick_id
        self.data = data
        self.input = input

    def to_data(self):
        data = {
            'id': self.id,
        }

        if self.data:
            data['data'] = self.data

        if self.input:
            data['input'] = self.input

        return {
            'brick': data
        }