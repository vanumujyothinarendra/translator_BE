from django.db import models
from django.conf import settings


class Message(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    original_text = models.TextField()

    translated_text = models.TextField()

    language = models.CharField(
        max_length=10
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.original_text[:50]}"