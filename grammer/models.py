from django.db import models
import datetime
# Create your models here.
from django.db import models

class Notes(models.Model):
    title = models.CharField(max_length=255, blank=True, default='Untitled Note')
    content = models.TextField("Note")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.content[:30]