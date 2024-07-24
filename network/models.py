from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="user")    
    post = models.CharField(max_length=250, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True) 
    is_edited = models.BooleanField(default=False) 

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,            
            "post": self.post,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
        }
    
class Followers(models.Model):
    followings = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="followings") 
    followers = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="followers") 

    def __str__(self):
        return f"{self.followings} folowed by {self.followers}"
    
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")

    def __str__(self):
        return f"{self.user} liked {self.post}"
