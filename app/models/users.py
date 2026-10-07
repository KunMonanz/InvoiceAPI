import uuid6
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.UUIDField(pk=True, default=uuid6.uuid7, index=True)
    email = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)
    organization_name = fields.CharField(max_length=100, null=True)
    picture = fields.CharField(max_length=500, null=True)
    password = fields.CharField(max_length=500, null=False)
    is_active = fields.BooleanField(default=True)
    is_premium = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:  # type: ignore
        table = "users"
