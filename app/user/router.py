from datetime import timedelta
import uuid

from argon2 import verify_password
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.security.dependency import get_current_user
from app.security.jwt import create_access_token, decode_access_token
from app.security.password import dummy_hash_and_verify
from app.user.crud import UserRepository
from app.user.schema import UserLogin, UserRegister, UserResponse
# from app.main import oauth

from authlib.integrations.starlette_client import OAuthError

from app.user.utils import get_jwt_from_headers

router = APIRouter(
    prefix="/api/v1/auth"
)

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


@router.post("/users")
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
        organization_name=user_registration_payload.organization_name
    )


@router.post("/login")
async def login(user_login_payload: UserLogin):
    user = await user_repository.get_user_by_email(user_login_payload.email)
    
    invalid_email_or_password_exception = HTTPException(
                                            detail="Incorrect email or password",
                                            status_code=status.HTTP_401_UNAUTHORIZED,
                                            headers={"WWW-Authenticate": "Bearer"}
                                        )
    
    if not user:
        dummy_hash_and_verify(user_login_payload.password)
        raise invalid_email_or_password_exception
    
    if not verify_password(user.password, user_login_payload.password): # type: ignore
        raise invalid_email_or_password_exception
    
    data = {
        "sub": str(user.id),
        "jti": str(uuid.uuid4)
    }
    
    access_token = create_access_token(data, timedelta(hours=24))
    
    return Response(
        {
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
        
    
@router.post("/logout")
async def logout(request: Request):
    raw_jwt = get_jwt_from_headers(request)
    payload = await decode_access_token(raw_jwt)
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    await user_repository.blacklist_token(jti)
    return Response(
        content={
                    "success": "Logged out successfully"
                },
        status_code=status.HTTP_200_OK
    )


@router.patch("/deactivate")
async def deactivate(current_user=Depends(get_current_user)):
    await user_repository.deactivate_user(current_user)
    return Response(
        {
            "success": "Account deactivated successfully"
        },
        status_code=status.HTTP_200_OK
    )


@router.patch("/activate")
async def activate(current_user=Depends(get_current_user)):
    await user_repository.activate_user(current_user)
    return Response(
        {
            "success": "Account reactivated successfully"
        },
        status_code=status.HTTP_200_OK
    )