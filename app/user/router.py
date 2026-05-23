from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, Response, status
from app.security.jwt import create_access_token
from app.user.crud import UserRepository
from app.user.schema import UserRegister, UserResponse
# from app.main import oauth

from authlib.integrations.starlette_client import OAuthError

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