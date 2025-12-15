from django.db import models


class Anonce(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now=True)
    update_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
