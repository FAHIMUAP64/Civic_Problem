from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('authority', 'Authority'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    nid_document = models.FileField(upload_to='nid_docs/', null=True, blank=True)


class AuthorityProfile(models.Model):
    LEVELS = (
        ('member', 'Member'),
        ('chairman', 'Chairman'),
        ('mayor', 'Mayor'),
        ('dc', 'DC'),
        ('mp', 'MP'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVELS)