# models.py
from django.db import models

class Upload(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    images = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
