from django.contrib.auth.models import AbstractUser
from django.db import models



# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    social_links = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

