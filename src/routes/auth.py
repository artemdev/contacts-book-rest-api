from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from src.schemas import UserResponse, RequestEmail
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas import UserSchema, TokenSchema, UserResponse
from src.services.email import send_email
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user signup. It checks if the user already exists, if not, it creates a new user and sends a confirmation email.

    Args:
        body (UserSchema): User details.
        bt (BackgroundTasks): For running tasks in the background.
        request (Request): Incoming request.
        db (AsyncSession): Database session.

    Returns:
        UserResponse: The created user.
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)

    bt.add_task(send_email, new_user.email,
                new_user.username, str(request.base_url))
    return new_user


@router.post("/login",  response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user login. It checks if the user exists and if the password is correct. If everything is fine, it generates and returns JWT tokens.

    Args:
        body (OAuth2PasswordRequestForm): User login details.
        db (AsyncSession): Database session.

    Returns:
        TokenSchema: Access and refresh JWT tokens.
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "test"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token',  response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Endpoint for refreshing JWT tokens. It checks if the refresh token is valid and then generates new access and refresh tokens.

    Args:
        credentials (HTTPAuthorizationCredentials): Authorization credentials.
        db (AsyncSession): Database session.

    Returns:
        TokenSchema: New access and refresh JWT tokens.
    """
    token = credentials.credentials
    email = await auth_service.get_email_form_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for confirming the user's email. It checks if the token is valid and then confirms the user's email.

    Args:
        token (str): Email confirmation token.
        db (AsyncSession): Database session.

    Returns:
        dict: Confirmation message.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.is_confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Endpoint for requesting a confirmation email. It checks if the user's email is already confirmed, if not, it sends a confirmation email.

    Args:
        body (RequestEmail): Email request details.
        background_tasks (BackgroundTasks): For running tasks in the background.
        request (Request): Incoming request.
        db (AsyncSession): Database session.

    Returns:
        dict: Confirmation message.
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.is_confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
