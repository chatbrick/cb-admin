

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
            data['conditions'] = [cond.to_data for cond in self.condition]

        return data


class FacebookGeneralAction(object):
    def __init__(self, message):
        self.message = message

    def to_data(self):
        return {
            'message': self.message.get_data()
        }


class FacebookBrickAction(object):
    def __init__(self, brick_id, data=None):
        self.id = brick_id
        self.data = data

    def to_data(self):
        return {
            'brick': {
                'id': self.id,
                'data': self.data
            }
        }