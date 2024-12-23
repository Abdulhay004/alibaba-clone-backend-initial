from enum import Enum
from django.db import models

class BaseEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

    @classmethod
    def values(cls):
        return [choice.value for choice in cls]

class UserRole(BaseEnum):
    """ Don't change the role name here. It will be used in permission system. """
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"
class PolicyNameEnum(BaseEnum):
    BUYER_POLICY = "buyer_policy"
    SELLER_POLICY = "seller_policy"
    ADMIN_POLICY = "admin_policy"


class GenderChoices(models.TextChoices):
    MALE = 'Male', 'M'
    FEMALE = 'Female', 'F'

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"