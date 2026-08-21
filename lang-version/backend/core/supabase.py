from dotenv import load_dotenv
load_dotenv()

import os

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

supabase: Client = create_client(
    SUPABASE_URL, 
    SUPABASE_SECRET_KEY
)