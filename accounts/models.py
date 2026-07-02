from django.contrib.auth.models import AbstractUser
from django.db import models
from locations.models import UnionWard  # 🆕 Imported to establish localized authority jurisdictions


class User(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('authority', 'Authority'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    # Core identification & photo assets
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # 🆕 Enhanced Security: Explicit National ID text entry to cross-verify documents
    nid_number = models.CharField(max_length=20, unique=True, null=True, blank=True,
                                  help_text="10 or 17-digit National Identity Card Number")
    nid_document = models.FileField(upload_to='nid_docs/', null=True, blank=True,
                                    help_text="PDF scan or clear photo image of the physical NID card")

    # Custom property to get the exact unread notification count
    @property
    def unread_notif_count(self):
        """Returns the count of unread notifications for this user."""
        return self.notifications.filter(is_read=False).count()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class AuthorityProfile(models.Model):
    LEVELS = (
        ('member', 'Member'),
        ('chairman', 'Chairman'),
        ('mayor', 'Mayor'),
        ('dc', 'DC'),
        ('mp', 'MP'),
    )

    # 🆕 Added related_name to allow easy backwards querying via auth_user.authority_profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='authority_profile')
    level = models.CharField(max_length=20, choices=LEVELS)

    # 🆕 Geographic Jurisdiction Binding: Restricts complaints routing to this localized ward assignment
    assigned_ward = models.ForeignKey(
        UnionWard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_authorities',
        help_text="The localized area/ward this official governs and receives targeted complaint notifications for."
    )

    # 🆕 Verifiable Proof of Administrative Authority Designation
    official_id_card = models.ImageField(upload_to='authority_proofs/', null=True, blank=True,
                                         help_text="Upload Government Badge, ID, or Employee Card")
    appointment_letter = models.FileField(upload_to='authority_docs/', null=True, blank=True,
                                          help_text="Official Gazette notice or appointment letter copy")

    def __str__(self):
        ward_name = self.assigned_ward.name if self.assigned_ward else "Unassigned Location"
        return f"{self.user.username} - {self.get_level_display()} ({ward_name})"