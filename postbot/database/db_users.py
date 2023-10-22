from postbot.database import db

USERS_MONGODB_DB = db['users']

class Users:
    def __init__(self, user_id, channels=None):
        self.user_id = user_id
        self.channels = channels if channels is not None else []

    async def save(self):
        await USERS_MONGODB_DB.users.insert_one({
            'user_id': self.user_id,
            'channels': self.channels
        })

    async def update(self):
        await USERS_MONGODB_DB.users.update_one(
            {'user_id': self.user_id},
            {'$set': {
                'channels': self.channels
            }}
        )

    @classmethod
    async def get(cls, user_id):
        user_data = await USERS_MONGODB_DB.users.find_one({'user_id': user_id})
        if user_data:
            return cls(
                user_data['user_id'],
                user_data['channels']
            )
        return None

    @classmethod
    async def add_channel(cls, user_id, channel_id):
        user = await cls.get(user_id)
        if user:
            if user.channels:
                channels = list(set(user.channels))
                channels.append(channel_id)
                user.channels = channels
            else:
                user.channels = [channel_id]
            await user.update()
        else:
            user = cls(user_id, [channel_id])
            await user.save()

    @classmethod
    async def remove_channel(cls, user_id, channel_id):
        user = await cls.get(user_id)
        if user and user.channels:
            if channel_id in user.channels:
                user.channels.remove(channel_id)
                if not user.channels:
                    user.channels = None
                await user.update()

    @classmethod
    async def get_channels(cls, user_id):
        user = await cls.get(user_id)
        return user.channels if user else []

    @classmethod
    async def users_count(cls):
        # Calculate and return the number of users
        return await USERS_MONGODB_DB.users.count_documents({})
