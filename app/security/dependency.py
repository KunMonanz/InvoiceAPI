from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.users import User
from app.security.jwt import decode_access_token
from app.user.crud import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_repository = UserRepository()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Gets the current user based on the bearer token
    
    Args:
        token: The bearer token sent on a request that is to be decoded
        
    Return: 
        user: The user object the token belongs to
    """
    
    credential_exection = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    payload = await decode_access_token(token)
    user_id: str = str(payload.get("sub"))
    
    user = await user_repository.get_user_by_id(user_id)
    if user is None:
        raise credential_exection
    return user