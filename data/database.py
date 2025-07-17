import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MongoDB URI found in environment variables")

client = MongoClient(MONGO_URI)
db = client["test"]
profiles_collection = db["profiles"]

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
