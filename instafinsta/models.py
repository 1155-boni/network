import cloudinary
from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Socialnetwork(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"Socialnetwork {self.id}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_pic = CloudinaryField('image', blank=True, null=True)

    # ✅ followers field (many-to-many to User)
    followers = models.ManyToManyField(User, related_name="following", blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)  # Now stored in Cloudinary
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Post by {self.user.username}"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)   # 👈 Add this

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"
# Automatically create a profile when a new user registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
