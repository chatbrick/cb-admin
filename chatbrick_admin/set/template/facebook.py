class FacebookBrick(object):
    def __init__(self, brick_type, value, actions, condition=None):
        self.brick_type = brick_type
        self.value = value
        self.actions = actions
        self.condition = condition

    def to_data(self):
        data = {
            'type': self.brick_type,
            'value': self.value,
            'actions': [action.to_data() for action in self.actions]
        }

        if self.condition:
            data['conditions'] = self.condition

        return data


class FacebookGeneralAction(object):
    def __init__(self, message):
        self.message = message

    def to_data(self):
        return {
            'message': self.message.get_data()
        }


class FacebookBrickAction(object):
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
