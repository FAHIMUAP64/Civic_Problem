from django.db import models
from django.utils import timezone
from accounts.models import User
from locations.models import UnionWard


class Complaint(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )

    CATEGORY = (
        ('broken_roads',    'Broken Roads'),
        ('street_lights',   'Street Lights'),
        ('water_supply',    'Water Supply'),
        ('garbage',         'Garbage Disposal'),
        ('public_safety',   'Public Safety'),
        ('other',           'Other Problems'),
    )

    title       = models.CharField(max_length=255)
    description = models.TextField()
    category    = models.CharField(max_length=30, choices=CATEGORY, default='other')
    media       = models.FileField(upload_to='complaints/', null=True, blank=True)

    location   = models.ForeignKey(UnionWard, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    status     = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline   = models.DateField(null=True, blank=True, help_text="Expected resolution date")

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """True if deadline has passed and complaint is still not resolved."""
        if self.deadline and self.status != 'resolved':
            return timezone.now().date() > self.deadline
        return False

    @property
    def days_remaining(self):
        if self.deadline and self.status != 'resolved':
            delta = self.deadline - timezone.now().date()
            return delta.days
        return None


class Notification(models.Model):
    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    complaint  = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='notifications')
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username} — {self.complaint.title}"
