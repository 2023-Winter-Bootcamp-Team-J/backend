from django.db import models

class Story(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    content = models.CharField(max_length=200, null=False, blank=True)
    image_url = models.CharField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

