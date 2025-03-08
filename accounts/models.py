from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.

class AdditionalUserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = CloudinaryField('image', default="https://res.cloudinary.com/dmpxni4ku/image/upload/v1713334275/user-avatar-placeholder_dfzivc.png")
    # profile_picture = models.ImageField(upload_to="articles", default="default")
    timestamp = models.DateTimeField(auto_now_add=True)
    