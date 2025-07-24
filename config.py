# Required Libary(s) and Import(s)
import os
from dotenv import load_dotenv

# Loads .env File
load_dotenv()

# Pulls Mongo URI from .env File
MONGO_URI = os.getenv("MONGO_URI")

# Guild ID for AMT Server
GUILD_ID = 925867675513659473

# Staff IDs
STAFF = []