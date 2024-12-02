from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ArticleFile(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='')

    def __str__(self):
        return f"File for article: {self.article.title}"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"