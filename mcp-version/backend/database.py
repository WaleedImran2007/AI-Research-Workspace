import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["ai_research_workspace"]

users_collection = db["users"]
collections_collection = db["collections"]
documents_collection = db["documents"]
knowledge_chunks_collection = db["knowledge_chunks"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]
page_layouts_collection = db["page_layouts"]
memories_collection = db["memories"]

try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB")
except Exception as e:
    print(e)