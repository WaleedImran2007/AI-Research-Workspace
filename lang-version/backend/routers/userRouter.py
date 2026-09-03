from fastapi import APIRouter, HTTPException, Depends

from middlewares.authMiddleware import get_current_user

from database import users_collection

from bson import ObjectId

router = APIRouter()

# RETURN USER'S REMAINING AI REQUESTS AND RESET DATE
@router.get("/ai-requests")
def get_ai_requests(current_user: dict = Depends(get_current_user)):
    print("CURRENT USER PAYLOAD:", current_user)
    user = users_collection.find_one(
        {
            "_id": ObjectId(current_user["id"])
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "aiRequestsRemaining": user.get("aiRequestsRemaining", 0),
        "aiResetDate": user.get("aiResetDate")
    }