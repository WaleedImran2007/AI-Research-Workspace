from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from database import users_collection

PAKISTAN_TZ = ZoneInfo("Asia/Karachi")

now_pk = datetime.now(PAKISTAN_TZ)

next_midnight_pk = (
    now_pk.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    ) + timedelta(days=1)
)

users_collection.update_many(
    {
        "aiResetDate": {"$exists": False}
    },
    {
        "$set": {
            "aiResetDate": next_midnight_pk
        }
    }
)