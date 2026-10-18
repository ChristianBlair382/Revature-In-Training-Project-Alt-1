import re
from datetime import datetime, timedelta, timezone

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.dependencies_mongo import require_permission
from app.orm_models.refresh_token_mongo import Refresh_Token
from app.orm_models.user_mongo import User
from app.schemas.user_mongo import (
    Token,
    User_Create,
    User_Read,
    Refresh_Token_Request,
)
from app.security import (
    create_access_token,
    create_refresh_token,
    encrypt_password,
    hash_refresh_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

def invalid_refresh_token() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token.",
    )

@router.post("/token", response_model=Token)
async def login(
    login_form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    target_user = await User.find_one(User.username == login_form_data.username)
    if (
        target_user is None
        or not verify_password(
            login_form_data.password,
            target_user.hashed_password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or Password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": target_user.username, "role": target_user.role.value}
    )
    now = datetime.now(timezone.utc)
    raw_refresh_token = create_refresh_token()
    await Refresh_Token(
        user=target_user,
        token_hash=hash_refresh_token(raw_refresh_token),
        created_at=now,
        expires_at=now + timedelta(days=Refresh_Token.DAYS_TILL_EXPIRE),
    ).insert()

    return Token(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
    )

@router.post(
    "/register",
    response_model=User_Read,
    status_code=status.HTTP_201_CREATED,
)
async def register_new_user(
    payload: User_Create,
    _: User = Depends(require_permission("users:create")),
) -> User:
    existing_user = await User.find_one(
        {
            "username": {
                "$regex": f"^{re.escape(payload.username)}$",
                "$options": "i",
            }
        }
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"User '{payload.username}' already exists. "
                "Please try a different username."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_user = User(
        username=payload.username,
        hashed_password=encrypt_password(payload.password),
        role=payload.role,
    )
    try:
        await new_user.insert()
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"User '{payload.username}' already exists. "
                "Please try a different username."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return new_user

async def revoke_active_family_tokens(
    family_id: PydanticObjectId | object,
    revoked_at: datetime,
) -> None:
    active_tokens = await Refresh_Token.find(
        Refresh_Token.family_id == family_id,
        Refresh_Token.revoked_at == None,  # noqa: E711
    ).to_list()
    for active_token in active_tokens:
        active_token.revoked_at = revoked_at
        await active_token.save()

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    payload: Refresh_Token_Request,
) -> Token:
    now = datetime.now(timezone.utc)
    token_hash = hash_refresh_token(payload.refresh_token)
    target_refresh_token = await Refresh_Token.find_one(
        Refresh_Token.token_hash == token_hash
    )
    if target_refresh_token is None:
        raise invalid_refresh_token()

    if target_refresh_token.revoked_at is not None:
        await revoke_active_family_tokens(target_refresh_token.family_id, now)
        raise invalid_refresh_token()

    if now >= target_refresh_token.expires_at:
        raise invalid_refresh_token()

    previous = await Refresh_Token.get_motor_collection().find_one_and_update(
        {
            "_id": target_refresh_token.id,
            "revoked_at": None,
        },
        {"$set": {"revoked_at": now}},
        return_document=ReturnDocument.BEFORE,
    )
    if previous is None:
        latest_token = await Refresh_Token.get(target_refresh_token.id)
        if latest_token is not None and latest_token.revoked_at is not None:
            await revoke_active_family_tokens(latest_token.family_id, now)
        raise invalid_refresh_token()

    user_reference = getattr(target_refresh_token.user, "ref", target_refresh_token.user)
    target_user = await User.get(user_reference.id)
    if target_user is None or not target_user.is_active:
        raise invalid_refresh_token()

    raw_refresh_token = create_refresh_token()
    new_access_token = create_access_token(
        data={"sub": target_user.username, "role": target_user.role.value}
    )
    await Refresh_Token(
        user=target_user,
        family_id=target_refresh_token.family_id,
        token_hash=hash_refresh_token(raw_refresh_token),
        created_at=now,
        expires_at=now + timedelta(days=Refresh_Token.DAYS_TILL_EXPIRE),
    ).insert()

    return Token(
        access_token=new_access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
    )
