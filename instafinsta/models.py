
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Socialnetwork(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        pass
        
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} by {self.user.username}"