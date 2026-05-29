import uuid
from tortoise import models, fields


class BlackListedToken(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    jti = fields.CharField(max_length=100, unique=True, null=False)
    