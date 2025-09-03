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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatar", blank=True, null=True)
    followers = models.ManyToManyField("self", symmetrical=False, related_name="following_set", blank=True)
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers_set", blank=True)
    def __str__(self):
        return self.user.username
    @property
    def following(self):
        # users this profile follows
        return Profile.objects.filter(followers=self)
    def is_following(self, profile):
        return self.following.filter(id=profile.id).exists()
    def is_followed_by(self, profile):
        return self.followers.filter(id=profile.id).exists()
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)  # ✅ Cloudinary for post images
    caption = models.TextField(blank=True)
    content = models.TextField(blank=True)   # ✅ Added content field
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    @property
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"Post by {self.author.username} - {self.caption[:20]}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on Post {self.post.id}"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()