"""
Models: Organization, User (custom auth), SignupRequest.

User serves as the unified authentication model for:
  - super_admin  (organization_id = NULL)
  - admin        (organization_id = <org>)
  - employee     (organization_id = <org>)

Customers authenticate via the Contact model (separate JWT flow).
"""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models



# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class Organization(models.Model):
    """Multi-tenant root. Stores industry_type and per-org terminology."""

    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'
    STATUS_SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DISABLED, 'Disabled'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    allowed_modules = models.JSONField(default=list)
    allowed_settings_tabs = models.JSONField(default=list)
    industry_type = models.CharField(max_length=50, default='general')
    terminology = models.JSONField(default=dict)
    subscription_start = models.DateField()
    subscription_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# User Manager
# ---------------------------------------------------------------------------

class UserManager(BaseUserManager):
    """Manager for the custom User model."""

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        print(user)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('status', 'active')
        extra_fields['organization'] = None
        return self.create_user(username, password, **extra_fields)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(AbstractBaseUser):
    """
    Unified auth model: super_admin | admin | employee.
    organization is NULL for super_admin.
    password is stored in password_hash column.
    """

    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_ADMIN = 'admin'
    ROLE_EMPLOYEE = 'employee'
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_EMPLOYEE, 'Employee'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        db_column='organization_id',
    )
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255, db_column='password_hash')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    allowed_modules = models.JSONField(default=list)
    branch_id = models.IntegerField(null=True, blank=True)
    allowed_permissions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    # Required by AbstractBaseUser
    last_login = None
    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['username', 'name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'role']),
        ]

    def __str__(self):
        return f'{self.username} ({self.role})'

    # AbstractBaseUser requires is_active
    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def is_staff(self):
        return self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_superuser(self):
        return self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_customer(self):
        return False

    def has_perm(self, perm, obj=None):
        return self.role == self.ROLE_SUPER_ADMIN

    def has_module_perms(self, app_label):
        return self.role == self.ROLE_SUPER_ADMIN


# ---------------------------------------------------------------------------
# SignupRequest
# ---------------------------------------------------------------------------

class SignupRequest(models.Model):
    """Public signup form submission (processed by super admin)."""

    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    business_type = models.CharField(max_length=100)
    business_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signup_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.business_name} — {self.name}'
