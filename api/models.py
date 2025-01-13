from django.db import models

class MarineSpecies(models.Model):
    image_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    class_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
