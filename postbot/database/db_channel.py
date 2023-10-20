from postbot.databse import db
MONGODB_DB = db['channels']


class Channel:
    def __init__(self, channel_id, admin_id, sticker_id=None, emojis=None, schedule_time=None):
        self.channel_id = channel_id
        self.admin_id = admin_id
        self.sticker_id = sticker_id
        self.emojis = emojis if emojis is not None else []
        self.schedule_time = schedule_time

    def save(self):
        MONGODB_DB.channels.insert_one({
            'channel_id': self.channel_id,
            'admin_id': self.admin_id,
            'sticker_id': self.sticker_id,
            'emojis': self.emojis,
            'schedule_time': self.schedule_time
        })

    def update(self):
        MONGODB_DB.channels.update_one(
            {'channel_id': self.channel_id},
            {'$set': {
                'admin_id': self.admin_id,
                'sticker_id': self.sticker_id,
                'emojis': self.emojis,
                'schedule_time': self.schedule_time
            }}
        )

    @classmethod
    def get(cls, channel_id):
        channel_data = MONGODB_DB.channels.find_one({'channel_id': channel_id})
        if channel_data:
            return cls(
                channel_data['channel_id'],
                channel_data['admin_id'],
                channel_data['sticker_id'],
                channel_data['emojis'],
                channel_data['schedule_time']
            )
        return None

    @classmethod
    def delete(cls, channel_id):
        MONGODB_DB.channels.delete_one({'channel_id': channel_id})

    def add_schedule(self, schedule_minutes):
        if self.schedule_time is None:
            self.schedule_time = []
        self.schedule_time.append(schedule_minutes)
        self.update()

    def remove_schedule(self, schedule_minutes):
        if self.schedule_time is not None and schedule_minutes in self.schedule_time:
            self.schedule_time.remove(schedule_minutes)
            self.update()

    def get_schedule(self):
        return self.schedule_time if self.schedule_time is not None else []

    def add_emojis(self, new_emojis):
        if self.emojis is None:
            self.emojis = []
        self.emojis.extend(new_emojis)
        self.update()

    def remove_emojis(self, emojis_to_remove):
        if self.emojis is not None:
            for emoji in emojis_to_remove:
                if emoji in self.emojis:
                    self.emojis.remove(emoji)
        self.update()

    def get_emojis(self):
        return self.emojis if self.emojis is not None else []

    def set_sticker(self, sticker_id):
        self.sticker_id = sticker_id
        self.update()

    def get_sticker(self):
        return self.sticker_id
