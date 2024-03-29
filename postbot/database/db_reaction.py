# db_reaction.py

from postbot.database import db
MONGODB_DB = db['reactions']
    
async def get_reaction(channel_id, post_id, emoji):
    reaction_data = await MONGODB_DB.reactions.find_one({
        'channel_id': channel_id,
        'post_id': post_id,
        'emoji': emoji
    })
    if reaction_data:
        return {
            'channel_id': reaction_data['channel_id'],
            'post_id': reaction_data['post_id'],
            'emoji': reaction_data['emoji'],
            'count': reaction_data['count']
        }
    return None

async def update_reaction(channel_id, post_id, emoji, new_count):
    await MONGODB_DB.reactions.update_one(
        {'channel_id': channel_id, 'post_id': post_id, 'emoji': emoji},
        {'$set': {'count': new_count}}
    )

async def save_reaction(channel_id, post_id, emoji, count):
    await MONGODB_DB.reactions.insert_one({
        'channel_id': channel_id,
        'post_id': post_id,
        'emoji': emoji,
        'count': count
    })

async def delete_reaction(channel_id, post_id, emoji):
    await MONGODB_DB.reactions.delete_one({
        'channel_id': channel_id,
        'post_id': post_id,
        'emoji': emoji
    })
