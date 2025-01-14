from django.db import models

class MarineSpecies(models.Model):
    # Unique identifier for each image
    image_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    
    # Classification result fields
    class_name = models.CharField(max_length=255, null=True, blank=True)  # Predicted class name
    confidence = models.CharField(max_length=50, null=True, blank=True)  # Store classification confidence as a string
    
    # Uploaded image
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)  # Path to the image file
    
    # Additional metadata
    summary = models.TextField(null=True, blank=True)  # Summary information about the species
    url = models.URLField(null=True, blank=True)  # URL for additional information
    model_used = models.CharField(max_length=100, null=True, blank=True)  # Model used for classification
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the record is created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the record is updated

    def __str__(self):
        return f"{self.image_id} - {self.class_name} ({self.model_used})"
