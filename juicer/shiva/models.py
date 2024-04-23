from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
import uuid


class ManushyaManager(BaseUserManager):
    def create_user(self, useremail, **extra_fields):
        if not useremail:
            raise ValueError('The useremail must be set')
        user = self.model(useremail=useremail, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, useremail, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(useremail, **extra_fields)


class Manushya(AbstractBaseUser):
    useremail = models.CharField(max_length=255, unique=True)
    oauth_provider = models.CharField(max_length=100, null=True)
    oauth_uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    access_token = models.CharField(max_length=255, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    token_expiry = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = ManushyaManager()

    USERNAME_FIELD = 'useremail'
    EMAIL_FIELD = 'useremail'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.useremail
