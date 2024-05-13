
import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserResponse
from src.services.auth import auth_service
from src.conf.config import settings
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=settings.CLD_NAME,
    api_key=settings.CLD_API_KEY,
    api_secret=settings.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=20))],
)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates the avatar of the current user. This endpoint is rate-limited to 2 requests every 20 seconds.

    Args:
        file (UploadFile): The new avatar image to upload.
        user (User): The current user.
        db (AsyncSession): Database session.

    Returns:
        UserResponse: The updated user.

    Raises:
        HTTPException: If the image upload fails.
    """
    public_id = f"Web16/{user.email}"
    res = cloudinary.uploader.upload(
        file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar(user.email, res_url, db)
    return user
