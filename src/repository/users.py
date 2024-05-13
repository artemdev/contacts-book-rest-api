from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Fetches a user by their email address.

    Args:
        email (str): The email address of the user to fetch.
        db (AsyncSession, optional): The database session.

    Returns:
        User: The fetched User object.
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Creates a new user.

    Args:
        body (UserSchema): The data for the new user.
        db (AsyncSession, optional): The database session.

    Returns:
        User: The created User object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Updates a user's refresh token.

    Args:
        user (User): The user for whom to update the refresh token.
        token (str | None): The new refresh token.
        db (AsyncSession): The database session.
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirms a user's email address.

    Args:
        email (str): The email address of the user to confirm.
        db (AsyncSession): The database session.
    """
    user = await get_user_by_email(email, db)
    user.is_confirmed = True
    await db.commit()
    print(user.is_confirmed)


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    Updates a user's avatar.

    Args:
        email (str): The email address of the user for whom to update the avatar.
        url (str): The new avatar URL.
        db (AsyncSession): The database session.

    Returns:
        User: The updated User object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
