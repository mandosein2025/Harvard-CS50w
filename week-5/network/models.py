from django.contrib.auth.models import AbstractUser
from django.db import models

POST_MAX_LENGTH = 240


class User(AbstractUser):
    pass


class Post(models.Model):

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    message = models.TextField(max_length=POST_MAX_LENGTH, blank=False)
    likes = models.ManyToManyField("User", blank=True, related_name="likes")

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.message} - {self.likes.count()} likes"

    @property
    def like_count(self):

        return self.likes.count()


class Following(models.Model):

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="followed_user"
    )
    followers = models.ManyToManyField("User", blank=True, related_name="following")

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateField(auto_now=True)

    @property
    def follower_count(self):

        return self.followers.count()

    def __str__(self):
        return f"{self.user.username} with {self.follower_count} followers"
