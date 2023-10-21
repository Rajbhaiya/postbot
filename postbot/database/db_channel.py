from postbot.database import db
MONGODB_DB = db['channels']

class Post:
    def __init__(self, text, media_url):
        self.text = text
        self.media_url = media_url

class Channel:
    def __init__(self, channel_id, admin_id, sticker_id=None, emojis=None, schedule_time=None, posts=None):
        self.channel_id = channel_id
        self.admin_id = admin_id
        self.sticker_id = sticker_id
        self.emojis = emojis if emojis is not None else []
        self.schedule_time = schedule_time
        self.posts = posts if posts is not None else []

    async def save(self):
        await MONGODB_DB.channels.insert_one({
            'channel_id': self.channel_id,
            'admin_id': self.admin_id,
            'sticker_id': self.sticker_id,
            'emojis': self.emojis,
            'schedule_time': self.schedule_time
        })

        # Save associated posts
        for post in self.posts:
            await MONGODB_DB.posts.insert_one({
                'channel_id': self.channel_id,
                'text': post.text,
                'media_url': post.media_url
            })

    async def update(self):
        await MONGODB_DB.channels.update_one(
            {'channel_id': self.channel_id},
            {'$set': {
                'admin_id': self.admin_id,
                'sticker_id': self.sticker_id,
                'emojis': self.emojis,
                'schedule_time': self.schedule_time
            }}
        )

        # Update associated posts
        await MONGODB_DB.posts.delete_many({'channel_id': self.channel_id})
        for post in self.posts:
            await MONGODB_DB.posts.insert_one({
                'channel_id': self.channel_id,
                'text': post.text,
                'media_url': post.media_url
            })

    @classmethod
    async def get(cls, channel_id):
        channel_data = await MONGODB_DB.channels.find_one({'channel_id': channel_id})
        if channel_data:
            channel = cls(
                channel_data['channel_id'],
                channel_data['admin_id'],
                channel_data['sticker_id'],
                channel_data['emojis'],
                channel_data['schedule_time']
            )
            post_data = await MONGODB_DB.posts.find({'channel_id': channel_id})
            channel.posts = [Post(post['text'], post['media_url']) async for post in post_data]
            return channel
        return None

    @classmethod
    async def delete(cls, channel_id):
        await MONGODB_DB.channels.delete_one({'channel_id': channel_id})
        await MONGODB_DB.posts.delete_many({'channel_id': channel_id})

    async def add_schedule(self, schedule_minutes):
        if self.schedule_time is None:
            self.schedule_time = []
        self.schedule_time.append(schedule_minutes)
        await self.update()

    async def remove_schedule(self, schedule_minutes):
        if self.schedule_time is not None and schedule_minutes in self.schedule_time:
            self.schedule_time.remove(schedule_minutes)
            await self.update()

    async def get_schedule(self):
        return self.schedule_time if self.schedule_time is not None else []

    async def add_emojis(self, new_emojis):
        if self.emojis is None:
            self.emojis = []
        self.emojis.extend(new_emojis)
        await self.update()

    async def remove_emojis(self, emojis_to_remove):
        if self.emojis is not None:
            for emoji in emojis_to_remove:
                if emoji in self.emojis:
                    self.emojis.remove(emoji)
        await self.update()

    def get_emojis(self):
        return self.emojis if self.emojis is not None else []

    def set_sticker(self, sticker_id):
        self.sticker_id = sticker_id
        await self.update()

    def get_sticker(self):
        return self.sticker_id

    @classmethod
    async def get_channel_info(cls, channel_id):
        channel_data = await MONGODB_DB.channels.find_one({'channel_id': channel_id})
        if channel_data:
            return True, {
                'channel_id': channel_data['channel_id'],
                'admin_id': channel_data['admin_id'],
                'sticker_id': channel_data['sticker_id'],
                'emojis': channel_data['emojis']
            }
        return False, {}
