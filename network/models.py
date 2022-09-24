from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    follower = models.ManyToManyField("User", name="follower")

    def serialize(self):
        return {
            "follower": [follower['username'] for follower in self.follower.filter(user=self).values()],
            "following": [following['username'] for following in  User.objects.filter(follower__id=self.id).values()]
        }

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="post")
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=False)
    like = models.ManyToManyField("User", related_name="like")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%B %d %Y, %I:%M %p"),
            "like": [like['username'] for like in self.like.filter(like=self.id).values()],
        }