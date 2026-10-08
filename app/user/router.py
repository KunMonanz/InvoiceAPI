import uuid
from datetime import timedelta
from nt import access

from argon2 import verify_password

# from app.main import oauth
from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.security.dependency import get_current_user
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)
from app.security.password import dummy_hash_and_verify
from app.user.crud import UserRepository
from app.user.schema import (
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.user.utils import get_jwt_from_headers

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

user_repository = UserRepository()

# @router.post("/callback")
# async def auth_callback(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#     except OAuthError as error:
#         raise HTTPException(
#             detail=f"OAuth Error {error.error}",
#             status_code=status.HTTP_400_BAD_REQUEST
#         )

#     user_info = token.get("userinfo")
#     if not user_info:
#         raise HTTPException(
#             detail="Failed to fetch user data from Google",
#             status_code=status.HTTP_400_BAD_REQUEST
#         )
#     email = user_info.get("email")

#     user, created = await user_repository.get_or_create_user(
#                         email=email,
#                         first_name=user_info.get("given_name"),
#                         last_name=user_info.get("family_name"),
#                         picture=user_info.get("picture")
#                     )

#     access_token = create_access_token(
#         data={
#             "sub": user.email,
#             "user_id": user.id
#         },
#         expires_delta=timedelta(hours=24)
#     )

#     return Response(
#         {
#             "access_token": access_token,
#             "token_type": "bearer",
#             "is_new_user": created
#         }
#     )


# @router.get("/login")
# async def login(request: Request):
#     redirect_uri = request.url_for("auth_callback")
#     return await oauth.google.authorize_redirect(request, str(redirect_uri))


@router.post("/register")
async def create_user(
    user_registration_payload: UserRegister,
    response_model=UserResponse,
    response_model_exclude_none=True,
    summary="Create a new user profile",
):
    """
    **Registration Validation Rules:**
    * You must provide **either** an `organization_name` OR **both** `first_name` and `last_name`.
    * Providing only `first_name` or only `last_name` without the other will cause a validation error.
    """

    return await user_repository.register_user(
        email=user_registration_payload.email,
        first_name=user_registration_payload.first_name,
        last_name=user_registration_payload.last_name,
        password=user_registration_payload.password,
        organization_name=user_registration_payload.organization_name,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user and return access and refresh tokens",
)
async def login(
    user_login_payload: UserLogin,
):
    user = await user_repository.get_user_by_email(user_login_payload.email)

    invalid_email_or_password_exception = HTTPException(
        detail="Incorrect email or password",
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        dummy_hash_and_verify(user_login_payload.password)
        raise invalid_email_or_password_exception

    if not verify_password(user.password, user_login_payload.password):  # type: ignore
        raise invalid_email_or_password_exception

    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())

    data = {"sub": str(user.id), "jti": access_jti, "refresh_jti": refresh_jti}

    access_token = await create_access_token(data=data)
    refresh_token = await create_refresh_token(data=data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/logout")
async def logout(request: Request):
    raw_jwt = get_jwt_from_headers(request)
    payload = await decode_access_token(raw_jwt)
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    await user_repository.blacklist_token(jti)
    return Response(
        content={"success": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_access_token(payload: RefreshTokenRequest):
    token_data = await decode_access_token(
        payload.refresh_token, expected_type="refresh"
    )
    user_id = token_data.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
        )

    new_access_token = await create_access_token(
        data={"sub": str(user.id), "jti": str(uuid.uuid4())}
    )
    new_refresh_token = await create_refresh_token(
        data={"sub": str(user.id), "jti": str(uuid.uuid4())}
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.patch("/deactivate")
async def deactivate(current_user=Depends(get_current_user)):
    await user_repository.deactivate_user(current_user)
    return Response(
        {"success": "Account deactivated successfully"}, status_code=status.HTTP_200_OK
    )


@router.patch(
    "/activate",
    response_model=MessageResponse,
    summary="Reactivate user account",
)
async def activate(
    login_payload: UserLogin,
):
    user = await user_repository.get_user_by_email(login_payload.email)
    if not user or not verify_password(login_payload.password, user.password):  # pyright: ignore[reportArgumentType]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    await user_repository.activate_user(user)
    return {"message": "Account reactivated successfully"}
