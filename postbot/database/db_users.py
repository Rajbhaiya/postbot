from postbot.database import db

USERS_DB = db['users']

def init_user(user_id, channels=None):
    return {
        'user_id': user_id,
        'channels': channels if channels is not None else []
    }

async def save_user(user_id, channels=None):
    user_data = init_user(user_id, channels)
    await USERS_DB.users.insert_one(user_data)

async def update_user(user_id, channels):
    await USERS_DB.users.update_one(
        {'user_id': user_id},
        {'$set': {
            'channels': channels
        }}
    )

async def get_user(user_id):
    user_data = await USERS_DB.users.find_one({'user_id': user_id})
    if user_data:
        return user_data
    return None

async def add_channel(user_id, channel_id):
    user = await get_user(user_id)
    if user:
        if user['channels']:
            channels = list(set(user['channels']))
            channels.append(channel_id)
            user['channels'] = channels
        else:
            user['channels'] = [channel_id]
        await update_user(user_id, user['channels'])
    else:
        user = init_user(user_id, [channel_id])
        await save_user(user_id, user['channels'])

async def remove_channel(user_id, channel_id):
    user = await get_user(user_id)
    if user and user['channels']:
        if channel_id in user['channels']:
            user['channels'].remove(channel_id)
            if not user['channels']:
                user['channels'] = None
            await update_user(user_id, user['channels'])

async def get_channels(user_id):
    user = await get_user(user_id)
    return user['channels'] if user else []

async def users_count():
    user_count = await USERS_DB.users.count_documents({})
    return user_count
