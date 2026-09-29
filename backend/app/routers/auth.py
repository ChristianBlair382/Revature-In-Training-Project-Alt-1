from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import User, USER_ROLE
from app.schemas import User_Create, User_Read, Token
from app.security import create_access_token, encrypt_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login(
    login_form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    db_command = select(User).where(User.username == login_form_data.username)
    output = await db.execute(db_command)
    target_user = output.scalar_one_or_none()

    # Checks that the username of the specified User is correct, along with their password.
    if (target_user is None or not verify_password(login_form_data.password, target_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or Password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    new_access_token = create_access_token(data={"sub": target_user.username, "role": target_user.role.value})
    return Token(access_token=new_access_token, token_type="bearer")

@router.post("/register", response_model=User_Read, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    payload: User_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
) -> User:
    # Check that there isn't a User in the database with the same username as the attempted payload.
    db_command = select(User).where(func.lower(User.username) == payload.username.lower())
    existing_user = await db.execute(db_command)
    if (existing_user.scalar_one_or_none() is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{payload.username}' already exists. Please try a different username.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # If no such User exists, proceed with creating a new user.
    new_user = User(
        username = payload.username,
        hashed_password = encrypt_password(payload.password),
        role = payload.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user