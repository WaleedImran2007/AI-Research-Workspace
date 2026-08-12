from fastapi import APIRouter, Depends, HTTPException, status

from schemas.user import SignUpSchema, LoginSchema, UserResponse, LoginResponse

from utils.hash import hash_password, verify_password
from utils.serializer import user_serializer
from utils.jwt import create_access_token

from database import users_collection

from datetime import datetime, UTC

import os

router = APIRouter()

# SIGN UP
@router.post("/signup", response_model=UserResponse)
def signup(user: SignUpSchema):
    # Check if the user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    # Check if username exists
    existing_username = users_collection.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Hash the password
    hashed_password = hash_password(user.password)
    role = 'user'  # Default role is 'user'

    if user.email == os.getenv("ADMIN_EMAIL"):
        role = 'admin'

    # Create a new user document
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "role": role,
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }

    # Insert the new user into the database
    result = users_collection.insert_one(new_user)

    # Return the created user (excluding the password)
    return user_serializer(users_collection.find_one({"_id": result.inserted_id}))

# LOGIN
@router.post("/login", response_model=LoginResponse)
def login(user: LoginSchema):
    # check if user exists
    existing_user = users_collection.find_one({"email": user.email})

    if not existing_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )

    # VERIFY PASSWORD
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )

    # CREATE TOKEN
    token = create_access_token({
        "id": str(existing_user["_id"]),
        "username": existing_user["username"],
        "email": existing_user["email"],
        "role": existing_user["role"]
    })

    # return token and user data
    return {
        "token": token,
        "user": user_serializer(existing_user)
    }