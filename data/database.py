import os
from pymongo import MongoClient

from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MongoDB URI found in environment variables")

client = MongoClient(MONGO_URI)
db = client["test"]
profiles_collection = db["profiles"]
warnings_collection = db["warnings"]
autoresponders_collection = db["auto-responders"]

def responder(listener: str):
    return autoresponders_collection.find_one({"Listener": str(listener)})

def get_profile(user_id: int):
    return profiles_collection.find_one({"User": str(user_id)})

def create_profile(user_id: int, name: str, device: str = "", description: str = "", pronouns: str = ""):
    if get_profile(user_id):
        return False
    profile_data = {
        "User": str(user_id),
        "Name": name,
        "Device": device,
        "Description": description,
        "Pronouns": pronouns,
    }
    profiles_collection.insert_one(profile_data)
    return True

def update_field(user_id: int, field: str, value):
    # Make sure field matches the DB field names (e.g., "Name", "Device", etc.)
    result = profiles_collection.update_one(
        {"User": str(user_id)},
        {"$set": {field: value}}
    )
    return result.modified_count > 0

def insert_warning(guild_id, user_id, reason, moderator_id, warn_num, message_id=None, channel_id=None):
    warning_data = {
        "Guild": str(guild_id),
        "User": str(user_id),
        "Reason": reason,
        "Moderator": str(moderator_id),
        "WarnNum": warn_num,
        "MessageId": str(message_id) if message_id else None,
        "ChannelId": str(channel_id) if channel_id else None,
        "Date": datetime.utcnow()
    }
    return warnings_collection.insert_one(warning_data)

from pymongo import DESCENDING

def get_warnings(guild_id: str, user_id: str):
    return list(
        warnings_collection.find({
            "Guild": str(guild_id),
            "User": str(user_id)
        }).sort("Date", DESCENDING)
    )


def delete_warning(warn_num: str, guild_id: str):
    result = warnings_collection.delete_one({
        "WarnNum": warn_num,
        "Guild": str(guild_id)
    })
    return result.deleted_count > 0

