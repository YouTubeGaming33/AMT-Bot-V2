import json
import os
import random

from pymongo import MongoClient

from datetime import datetime, timedelta

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MongoDB URI found in environment variables")

client = MongoClient(MONGO_URI)
db = client["test"]
profiles_collection = db["profiles"]
warnings_collection = db["warnings"]
autoresponders_collection = db["auto-responders"]
levelling_collection = db["levels"]

def get_achievements(user_id: int):
    profile = profiles_collection.find_one({"User": str(user_id)})
    if profile:
        return profile.get("Achievements", [])
    return []

def add_achievement(user_id: int, achievement: str):
    print(f"Attempting to add achievement '{achievement}' for user {user_id}")
    profile = profiles_collection.find_one({"User": str(user_id)})
    if not profile:
        create_profile(user_id)

    # Prevent duplicates
    achievements = profile.get("Achievements", [])
    if achievement not in achievements:
        achievements.append(achievement)
        profiles_collection.update_one(
            {"User": str(user_id)},
            {"$set": {"Achievements": achievements}}
        )

def create_level(user_id: int, xp: int, level: int, achievements: list = None):

    level_data = {
        "User": str(user_id),
        "XP": xp,
        "Level": level,
    }
    levelling_collection.insert_one(level_data)
    return True

def get_level(user_id: int):
    return levelling_collection.find_one({"User": str(user_id)})

def update_level(user_id: int, xp: int, level: int):
    result = levelling_collection.update_one(
        {"User": str(user_id)},
        {"$set": {
            "XP": xp,
            "Level": level
        }}
    )
    return result.modified_count > 0

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

DAILY_MISSION_FILE = "data/missions.json"
WEEKLY_MISSION_FILE = "data/weeklymissions.json"
USER_DATA_FILE = "data/user_missions.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str)


def can_claim(last_time: str, cooldown_hours: int) -> bool:
    last_dt = datetime.fromisoformat(last_time)
    return datetime.utcnow() >= last_dt + timedelta(hours=cooldown_hours)

def assign_missions(user_id: str):
    user_data = {}

    if os.path.exists(USER_DATA_FILE):
        user_data = load_json(USER_DATA_FILE)

    if user_id not in user_data:
        user_data[user_id] = {}

    daily_pool = load_json(DAILY_MISSION_FILE)
    weekly_pool = load_json(WEEKLY_MISSION_FILE)

    user = user_data[user_id]

  # Handle daily missions
    if "daily" not in user or can_claim(user["daily"]["last_claimed"], 24):
        user["daily"] = {
            "last_claimed": datetime.utcnow().isoformat(),
            "missions": [random.choice(daily_pool)]
        }

    # Handle weekly missions
    if "weekly" not in user or can_claim(user["weekly"]["last_claimed"], 24 * 7):
        user["weekly"] = {
            "last_claimed": datetime.utcnow().isoformat(),
            "missions": [random.choice(weekly_pool)]
        }
        
    user_data[user_id] = user
    save_json(USER_DATA_FILE, user_data)

    return user
