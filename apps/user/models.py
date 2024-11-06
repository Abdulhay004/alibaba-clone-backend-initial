from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager, Permission)

import uuid
from django.utils import timezone

class Policy(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    permissions = models.ManyToManyField(Permission, related_name='policy_permissions', blank=True)

    class Meta:
        db_table = 'policy'
        ordering = ["-created_at"]
        app_label = 'user'


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    policies = models.ManyToManyField(Policy, related_name='groups', blank=True)
    permissions = models.ManyToManyField(Permission, related_name='group_permissions', blank=True)

    class Meta:
        db_table = 'group'
        ordering = ['-created_at']
        app_label = 'user'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Emailni kiritish shart.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser uchun is_staff = True bo\'lishi shart.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser uchun is_superuser = True bo\'lishi shart.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=13, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(Group, related_name='users', blank=True)
    policies = models.ManyToManyField(Policy, related_name='users', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        db_table = 'user'
        ordering = ['-created_at']
        permissions = [
            ('can_view', 'Can view something'),
            ('can_edit', 'Can edit something'),
        ]

    def __str__(self):
        return self.first_name

class SellerPolicy(models.Model):
    seller_user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100)

    # Permissions
    can_add_log_entry = models.BooleanField(default=False)
    can_change_log_entry = models.BooleanField(default=False)
    can_delete_log_entry = models.BooleanField(default=False)
    can_view_log_entry = models.BooleanField(default=False)

    can_add_group = models.BooleanField(default=False)
    can_change_group = models.BooleanField(default=False)
    can_delete_group = models.BooleanField(default=False)
    can_view_group = models.BooleanField(default=False)

    can_add_permission = models.BooleanField(default=False)
    can_change_permission = models.BooleanField(default=False)
    can_delete_permission = models.BooleanField(default=False)
    can_view_permission = models.BooleanField(default=False)

    can_add_content_type = models.BooleanField(default=False)

    # Product-related permissions
    can_add_product = models.BooleanField(default=False)
    can_change_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)
    can_view_product = models.BooleanField(default=False)

    # Category-related permissions
    can_view_category = models.BooleanField(default=False)

    # Color-related permissions
    can_add_color = models.BooleanField(default=False)
    can_change_color = models.BooleanField(default=False)
    can_delete_color = models.BooleanField(default=False)
    can_view_color = models.BooleanField(default=False)

    # Image-related permissions
    can_add_image = models.BooleanField(default=False)
    can_change_image = models.BooleanField(default=False)
    can_delete_image = models.BooleanField(default=False)
    can_view_image = models.BooleanField(default=False)

    def __str__(self):
        return f"Policy for {self.seller_user.username}"

class SellerUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.OneToOneField(SellerPolicy, on_delete=models.CASCADE, null=True, blank=True)
    company = models.CharField(max_length=50, blank=True)
    image = models.BinaryField(null=True, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    street_address = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    second_phone_number = models.CharField(max_length=13, blank=True)
    building_number = models.CharField(max_length=50, blank=True)
    apartment_number = models.CharField(max_length=50, blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BuyerPolicy(models.Model):
    buyer_user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100)

    # Permissions
    can_add_group = models.BooleanField(default=False)
    can_change_group = models.BooleanField(default=False)
    can_delete_group = models.BooleanField(default=False)
    can_view_group = models.BooleanField(default=False)

    can_add_policy = models.BooleanField(default=False)
    can_change_policy = models.BooleanField(default=False)
    can_delete_policy = models.BooleanField(default=False)

    can_add_seller_user = models.BooleanField(default=False)
    can_change_seller_user = models.BooleanField(default=False)
    can_delete_seller_user = models.BooleanField(default=False)

    def __str__(self):
        return f"Policy for {self.buyer_user.first_name}"

class BuyerUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.OneToOneField(BuyerPolicy, on_delete=models.CASCADE, null=True, blank=True)
    image = models.BinaryField(null=True, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    street_address = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    second_phone_number = models.CharField(max_length=13, blank=True)
    building_number = models.CharField(max_length=50, blank=True)
    apartment_number = models.CharField(max_length=50, blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)