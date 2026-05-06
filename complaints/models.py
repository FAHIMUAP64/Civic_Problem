from django.db import models
from accounts.models import User
from locations.models import UnionWard

class Complaint(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    media = models.FileField(upload_to='complaints/', null=True, blank=True)

    location = models.ForeignKey(UnionWard, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS, default='pending')