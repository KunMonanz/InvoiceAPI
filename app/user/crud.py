from pydantic import EmailStr

from app.models.black_listed_tokens import BlackListedToken
from app.models.users import User
from app.security.password import hash_password

class UserRepository():
    
    @staticmethod
    async def get_or_create_user(
        email: EmailStr, 
        first_name: str, 
        last_name: str,
        picture: str
    ):
        user, created = await User.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "picture": picture
            }
        )
        
        return user, created

    @staticmethod
    async def register_user(
        email: EmailStr,
        password: str,
        first_name: str|None = None,
        last_name: str|None = None,
        organization_name: str|None = None
    ):
        hashed_password = hash_password(password)
        
        user = await User.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            organization_name=organization_name
        ) 
        
        return user

    @staticmethod
    async def get_user_by_email(email: EmailStr):
        return await User.get_or_none(email=email)

    @staticmethod
    async def get_user_by_id(user_id: str):
        return await User.get_or_none(id=user_id)
    
    @staticmethod
    async def deactivate_user(user: User):
        if user.is_active:
            return user
        user.is_active = False
        await user.save()
        return user
    
    @staticmethod
    async def activate_user(user: User):
        if not user.is_active:
            return user
        user.is_active = True
        await user.save()
        return user
        
    @staticmethod
    async def blacklist_token(jti: str):
        await BlackListedToken.create(jti=jti)