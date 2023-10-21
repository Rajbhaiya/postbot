# db_reaction.py

from postbot.database import db
MONGODB_DB = db['reactions']

class Reaction:
    def __init__(self, channel_id, post_id, emoji, count):
        self.channel_id = channel_id
        self.post_id = post_id
        self.emoji = emoji
        self.count = count

    async def save(self):
        await MONGODB_DB.reactions.insert_one({
            'channel_id': self.channel_id,
            'post_id': self.post_id,
            'emoji': self.emoji,
            'count': self.count
        })

    # Add other methods to update and retrieve reactions as needed

    @classmethod
    async def get(cls, channel_id, post_id, emoji):
        reaction_data = await MONGODB_DB.reactions.find_one({
            'channel_id': channel_id,
            'post_id': post_id,
            'emoji': emoji
        })
        if reaction_data:
            return cls(
                reaction_data['channel_id'],
                reaction_data['post_id'],
                reaction_data['emoji'],
                reaction_data['count']
            )
        return None
