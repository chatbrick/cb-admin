

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
    def __init__(self, brick_type, value, actions, edits=None):
        self.brick_type = brick_type
        self.value = value
        self.actions = actions
        self.edits = edits

    def to_data(self):
        data = {
            'type': self.brick_type,
            'value': self.value,
            'actions': [action.to_data() for action in self.actions]
        }

        if self.edits:
            data['edits'] = [action.to_data() for action in self.edits]

        return data


class TelegramGeneralAction(object):
    def __init__(self, message):
        self.message = message

    def to_data(self):
        return {
            'method': self.message.get_method(),
            'message': self.message.get_data()
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