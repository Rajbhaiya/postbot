from postbot.database import db

USERS_MONGODB_DB = db['users']

class Users:
    def __init__(self, user_id, channels=None):
        self.user_id = user_id
        self.channels = channels

    def save(self):
        USERS_MONGODB_DB.users.insert_one({
            'user_id': self.user_id,
            'channels': self.channels
        })

    def update(self):
        USERS_MONGODB_DB.users.update_one(
            {'user_id': self.user_id},
            {'$set': {
                'channels': self.channels
            }}
        )

    @classmethod
    def get(cls, user_id):
        user_data = USERS_MONGODB_DB.users.find_one({'user_id': user_id})
        if user_data:
            return cls(
                user_data['user_id'],
                user_data['channels']
            )
        return None

    @classmethod
    def add_channel(cls, user_id, channel_id):
        user = cls.get(user_id)
        if user:
            if user.channels:
                channels = list(set(user.channels))
                channels.append(channel_id)
                user.channels = channels
            else:
                user.channels = [channel_id]
            user.update()
        else:
            user = cls(user_id, [channel_id])
            user.save()

    @classmethod
    def remove_channel(cls, user_id, channel_id):
        user = cls.get(user_id)
        if user and user.channels:
            if channel_id in user.channels:
                user.channels.remove(channel_id)
                if not user.channels:
                    user.channels = None
                user.update()

    @classmethod
    def get_channels(cls, user_id):
        user = cls.get(user_id)
        return user.channels if user else []

    @classmethod
    def users_count(cls):
        # Calculate and return the number of users
        return USERS_MONGODB_DB.users.count_documents({})
