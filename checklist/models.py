from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings


def user_profile_picture_path(instance, filename):
    return f'profile_pics/{instance.email}/{filename}'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    POSITION_CHOICES = [
        ('SALE_OFFICER', 'Sale Officer'),
        ('MANAGER', 'Manager'),
        ('OPERATE_OFFICER', 'Operate Officer'),
    ]

    ZONE_CHOICES = [
        ('CENTRAL', 'Central Zone'),
        ('LAKE', 'Lake Zone'),
    ]

    BRANCH_CHOICES = [
        ('CHANIKA', 'Chanika'),
        ('MWANZA', 'Mwanza'),
        ('SINGIDA', 'Singida'),
        ('MIKOCHENI', 'Mikocheni'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    position = models.CharField(max_length=20, choices=POSITION_CHOICES, null=True, blank=True)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, null=True, blank=True)
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES, null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name




class ProductionLine(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Set once on creation
    updated_at = models.DateTimeField(auto_now=True)      # Updated on each save

    def __str__(self):
        return self.name
    



from django.conf import settings
from django.db import models

# Shared STATUS choices
STATUS_CHOICES = [
    ('opened', 'Opened'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
    ('resubmite', 'Resubmit'),
]

DESIGNATION_CHOICES = [
    ('Owner', 'Owner'),
    ('Engineer', 'Engineer'),
    ('Contractor', 'Contractor'),
]


from django.db import models
from django.conf import settings
from django.utils.timezone import now

STATUS_CHOICES = [
    ('opened', 'Opened'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
    ('resubmite', 'Resubmit'),
]

class FormSubmission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    # Final status saved after both managers review
    final_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    # Manager 1 review
    manager1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='first_reviews'
    )
    manager1_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    manager1_comment = models.TextField(null=True, blank=True)
    manager1_reviewed_at = models.DateTimeField(null=True, blank=True)

    # Manager 2 review
    manager2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='second_reviews'
    )
    manager2_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    manager2_comment = models.TextField(null=True, blank=True)
    manager2_reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    
    def save(self, *args, **kwargs):
        # Ensure new forms always start with "opened"
        if not self.pk:
            self.final_status = 'opened'
        super().save(*args, **kwargs)

    def is_reviewed_by(self, user):
        """Check if the given user has already submitted a review."""
        return user == self.manager1 or user == self.manager2

    def is_fully_reviewed(self):
        """True if both managers have reviewed."""
        return self.manager1 and self.manager2

    def save_review(self, user, status, comment):
        """Handles logic for saving a manager's review."""
        if self.is_reviewed_by(user):
            raise ValueError("You have already reviewed this form.")

        if self.manager1 is None:
            self.manager1 = user
            self.manager1_status = status
            self.manager1_comment = comment
            self.manager1_reviewed_at = now()
        elif self.manager2 is None:
            self.manager2 = user
            self.manager2_status = status
            self.manager2_comment = comment
            self.manager2_reviewed_at = now()
            self._finalize_status()
        else:
            raise ValueError("Both managers have already submitted their reviews.")

        self.save()

    def _finalize_status(self):
        """Determine the final status after both managers review."""
        statuses = [self.manager1_status, self.manager2_status]

        if all(s == 'approved' for s in statuses):
            self.final_status = 'approved'
        elif 'rejected' in statuses:
            self.final_status = 'rejected'
        elif 'resubmite' in statuses:
            self.final_status = 'resubmite'
        else:
            self.final_status = 'opened'  # fallback if mixed/undefined

    def get_review_summary(self):
        return {
            "manager1": {
                "user": self.manager1.email if self.manager1 else None,
                "status": self.manager1_status,
                "comment": self.manager1_comment,
                "reviewed_at": self.manager1_reviewed_at,
            },
            "manager2": {
                "user": self.manager2.email if self.manager2 else None,
                "status": self.manager2_status,
                "comment": self.manager2_comment,
                "reviewed_at": self.manager2_reviewed_at,
            },
            "final_status": self.final_status,
        }



class VisitsAchieved(models.Model):
    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name='visits',
        null=True,
        blank=True
    )
    new = models.IntegerField()
    old = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visits achieved"
        verbose_name_plural = "Visits achieved"

    def __str__(self):
        return f"New: {self.new}, Old: {self.old}"


class OrderQuotation(models.Model):
    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name='quotations',
        null=True,
        blank=True
    )
    production_line = models.ForeignKey(
        'ProductionLine',
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    client_name = models.CharField(max_length=150)
    contact = models.CharField(max_length=100)
    quotation = models.DecimalField(max_digits=17, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_quotations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.production_line.name}"


class PaymentCollected(models.Model):
    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    production_line = models.ForeignKey(
        'ProductionLine',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    client_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)
    payment_amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_collected'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment collected"
        verbose_name_plural = "Payment collected"

    def __str__(self):
        return f"{self.client_name} - {self.payment_amount}"


from django.db import models
from django.conf import settings

class NewLead(models.Model):
    submission = models.ForeignKey(
        'FormSubmission',
        on_delete=models.CASCADE,
        related_name='leads',
        null=True,
        blank=True
    )
    production_line = models.ForeignKey(
        'ProductionLine',
        on_delete=models.CASCADE,
        related_name='leads'
    )
    client_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.designation}"



class RouteClient(models.Model):
    PURPOSE_CHOICES = [
        ('NEW', 'New'),
        ('FU', 'Follow Up'),
        ('CLOSING', 'Closing'),
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MED', 'Medium'),
        ('LOW', 'Low'),
    ]

    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='route_clients'
    )
    client_name = models.CharField(max_length=255, verbose_name="Client / Company Name")
    contact = models.CharField(max_length=100)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    next_step = models.TextField(verbose_name="Your Next Step")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_route_clients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} ({self.production_line})"




    


class DailyTarget(models.Model):
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='daily_targets')
    assigned = models.PositiveIntegerField()
    to_be_achieved = models.PositiveIntegerField()
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='daily_targets_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Daily target"
        verbose_name_plural = "Daily targets"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.production_line} - {self.assigned}/{self.to_be_achieved}"
    



