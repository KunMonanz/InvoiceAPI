import uuid
from tortoise import models, fields


class BlackListedToken(models.Model):
    """
    Model to store blacklisted tokens from logout operations
    or banning
    """
    
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    jti = fields.CharField(max_length=100, unique=True, null=False)
    created_at = fields.DatetimeField(auto_now_add=True)