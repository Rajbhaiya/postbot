from postbot.database import db
from postbot.database.db_users import *
from typing import List, Dict

CHANNEL_DB = db['channels']

def create_post(text, media_url):
    return {
        'text': text,
        'media_url': media_url
    }

def create_channel(channel_id, admin_id, sticker_id=None, emojis=None, schedule_time=None, posts=None):
    return {
        'channel_id': channel_id,
        'admin_id': admin_id,  # Changed from admin_id to user_id
        'sticker_id': sticker_id,
        'emojis': emojis if emojis is not None else [],
        'schedule_time': schedule_time,
        'posts': posts if posts is not None else []
    }

def save_channel(channel_data: dict):
    try:
        CHANNEL_DB.channels.insert_one(channel_data)
    except Exception as e:
        raise CustomDatabaseError(f"Failed to save channel: {e}")

def update_channel(channel_id: str, channel_data: dict):
    try:
        CHANNEL_DB.channels.update_one({'channel_id': channel_id}, {'$set': channel_data}, upsert=True)
    except Exception as e:
        raise CustomDatabaseError(f"Failed to update channel: {e}")

def delete_channel(channel_id):
    CHANNEL_DB.channels.delete_one({'channel_id': channel_id})
    CHANNEL_DB.posts.delete_many({'channel_id': channel_id})

def add_channel(channel_id, user_id):
    channel_data = create_channel(channel_id, user_id)
    save_channel(channel_data)

def remove_channel(channel_id, user_id):
    # First, remove the channel entry from the CHANNEL_DB
    CHANNEL_DB.channels.delete_one({'channel_id': channel_id})
    user_data = get_user(user_id)
    if user_data and 'channels' in user_data and channel_id in user_data['channels']:
        user_data['channels'].remove(channel_id)
        update_user(user_id, user_data)

def add_schedule(channel_data, schedule_minutes):
    if channel_data['schedule_time'] is None:
        channel_data['schedule_time'] = []
    channel_data['schedule_time'].append(schedule_minutes)
    update_channel(channel_data['channel_id'], channel_data)

def remove_schedule(channel_data, schedule_minutes):
    if channel_data['schedule_time'] is not None and schedule_minutes in channel_data['schedule_time']:
        channel_data['schedule_time'].remove(schedule_minutes)
        update_channel(channel_data['channel_id'], channel_data)

def get_schedule(channel_data):
    return channel_data['schedule_time'] if channel_data['schedule_time'] is not None else []

def add_emojis(channel_data, new_emojis):
    if channel_data['emojis'] is None:
        channel_data['emojis'] = []
    channel_data['emojis'].extend(new_emojis)
    update_channel(channel_data['channel_id'], channel_data)

def remove_emojis(channel_data, emojis_to_remove):
    if channel_data['emojis'] is not None:
        for emoji in emojis_to_remove:
            if emoji in channel_data['emojis']:
                channel_data['emojis'].remove(emoji)
    update_channel(channel_data['channel_id'], channel_data)

def get_emojis(channel_data):
    return channel_data['emojis'] if channel_data['emojis'] is not None else []

def set_sticker(channel_data, sticker_id):
    channel_data['sticker_id'] = sticker_id
    update_channel(channel_data['channel_id'], channel_data)

def remove_sticker(channel_data):
    channel_data['sticker_id'] = None
    update_channel(channel_data['channel_id'], channel_data)

def get_sticker(channel_data):
    return channel_data['sticker_id']

def get_channel_info(channel_id):
    channel_data = CHANNEL_DB.channels.find_one({'channel_id': channel_id})
    if channel_data:
        return True, channel_data
    return False, {}

class CustomDatabaseError(Exception):
    pass
