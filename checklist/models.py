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
        ('Head of Sales', 'Head of Sales'),
        ('Facilitator', 'Facilitator'),
        ('Product Brand Manager', 'Product Brand Manager'),
        ('Corporate Manager', 'Corporate Manager'),
        ('Corporate Officer', 'Corporate Officer'),
        ('Zonal Sales Executive', 'Zonal Sales Executive'),
        ('Mobile Sales Officer', 'Mobile Sales Officer'),
        ('Desk Sales Officer', 'Desk Sales Officer'),
        ('Admin', 'Admin'),
    ]

    ZONE_CHOICES = [
        ('Coast Zone', 'Coast Zone'),
        ('Corporate', 'Corporate'),
        ('Central Zone', 'Central Zone'),
        ('Southern Zone', 'Southern Zone'),
        ('Northern Zone', 'Northern Zone'),
        ('Lake Zone', 'Lake Zone'),
    ]

    BRANCH_CHOICES = [
        ('Chanika', 'Chanika'),
        ('Mikocheni', 'Mikocheni'),
        ('Morogoro', 'Morogoro'),
        ('Zanzibar', 'Zanzibar'),
        ('ANDO HQ', 'ANDO HQ'),
        ('Dodoma', 'Dodoma'),
        ('Singida', 'Singida'),
        ('Tabora', 'Tabora'),
        ('Mbeya', 'Mbeya'),
        ('Tunduma', 'Tunduma'),
        ('Arusha', 'Arusha'),
        ('Moshi', 'Moshi'),
        ('Mwanza', 'Mwanza'),
        ('Geita', 'Geita'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    position = models.CharField(max_length=100, choices=POSITION_CHOICES, null=True, blank=True)
    zone = models.CharField(max_length=100, choices=ZONE_CHOICES, null=True, blank=True)
    branch = models.CharField(max_length=100, choices=BRANCH_CHOICES, null=True, blank=True)
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

from django.conf import settings
from django.db import models
from django.utils.timezone import now

from django.conf import settings
from django.db import models
from django.utils.timezone import now

STATUS_CHOICES = [
    ('opened', 'Opened'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('resubmite', 'Resubmite'),
]

class FormSubmission(models.Model):
    POSITION_CHOICES = [
        ('Head of Sales', 'Head of Sales'),
        ('Facilitator', 'Facilitator'),
        ('Product Brand Manager', 'Product Brand Manager'),
        ('Corporate Manager', 'Corporate Manager'),
        ('Corporate Officer', 'Corporate Officer'),
        ('Zonal Sales Executive', 'Zonal Sales Executive'),
        ('Mobile Sales Officer', 'Mobile Sales Officer'),
        ('Desk Sales Officer', 'Desk Sales Officer'),
        ('Admin', 'Admin'),
    ]

    # Define constants to avoid hardcoding strings
    POSITION_ZONAL = 'Zonal Sales Executive'
    POSITION_PRODUCT_MANAGER = 'Product Brand Manager'
    POSITION_FACILITATOR = 'Facilitator'
    POSITION_CORPORATE_OFFICER = 'Corporate Officer'
    POSITION_MOBILE_SALES_OFFICER = 'Mobile Sales Officer'
    POSITION_DESK_SALES_OFFICER = 'Desk Sales Officer'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    final_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='opened')

    # Reviewers and their statuses/comments/timestamps
    zonal_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='zonal_reviews'
    )
    zonal_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    zonal_comment = models.TextField(null=True, blank=True)
    zonal_reviewed_at = models.DateTimeField(null=True, blank=True)

    product_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='product_manager_reviews'
    )
    product_manager_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    product_manager_comment = models.TextField(null=True, blank=True)
    product_manager_reviewed_at = models.DateTimeField(null=True, blank=True)

    facilitator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='facilitator_reviews'
    )
    facilitator_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    facilitator_comment = models.TextField(null=True, blank=True)
    facilitator_reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    dispatch_time = models.TimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.final_status = 'opened'
        super().save(*args, **kwargs)

    def zonal_reviewed(self):
        return self.zonal_status is not None

    def can_review(self, user):
        # Allow Zonal Sales Executive to review anytime (first)
        if user.position == self.POSITION_ZONAL:
            return True

        # Other two can review only after zonal review is done
        if user.position in [self.POSITION_PRODUCT_MANAGER, self.POSITION_FACILITATOR]:
            return self.zonal_reviewed()

        # You can expand logic for other roles if needed here
        # For example, allow Corporate Officer, Mobile Sales Officer, Desk Sales Officer etc.

        return False

    def is_reviewed_by(self, user):
        return user == self.zonal_reviewer or user == self.product_manager or user == self.facilitator

    def all_reviewed(self):
        # True if all three have reviewed
        return all([
            self.zonal_status is not None,
            self.product_manager_status is not None,
            self.facilitator_status is not None,
        ])

    def save_review(self, user, status, comment):
        if self.is_reviewed_by(user):
            raise ValueError("You have already reviewed this form.")

        if user.position == self.POSITION_ZONAL:
            self.zonal_reviewer = user
            self.zonal_status = status
            self.zonal_comment = comment
            self.zonal_reviewed_at = now()

        elif user.position == self.POSITION_PRODUCT_MANAGER:
            if not self.zonal_reviewed():
                raise ValueError("Zonal Sales Executive must review first.")
            self.product_manager = user
            self.product_manager_status = status
            self.product_manager_comment = comment
            self.product_manager_reviewed_at = now()

        elif user.position == self.POSITION_FACILITATOR:
            if not self.zonal_reviewed():
                raise ValueError("Zonal Sales Executive must review first.")
            self.facilitator = user
            self.facilitator_status = status
            self.facilitator_comment = comment
            self.facilitator_reviewed_at = now()

        else:
            raise ValueError("You are not authorized to review this form.")

        # If all have reviewed, finalize final_status
        if self.all_reviewed():
            self._finalize_status()

        self.save()

    def _finalize_status(self):
        statuses = [
            self.zonal_status,
            self.product_manager_status,
            self.facilitator_status,
        ]
        if all(s == 'approved' for s in statuses):
            self.final_status = 'approved'
        elif 'rejected' in statuses:
            self.final_status = 'rejected'
        elif 'resubmite' in statuses:
            self.final_status = 'resubmite'
        else:
            self.final_status = 'opened'

    def get_review_summary(self):
        return {
            "zonal": {
                "user": self.zonal_reviewer.email if self.zonal_reviewer else None,
                "status": self.zonal_status,
                "comment": self.zonal_comment,
                "reviewed_at": self.zonal_reviewed_at,
            },
            "product_manager": {
                "user": self.product_manager.email if self.product_manager else None,
                "status": self.product_manager_status,
                "comment": self.product_manager_comment,
                "reviewed_at": self.product_manager_reviewed_at,
            },
            "facilitator": {
                "user": self.facilitator.email if self.facilitator else None,
                "status": self.facilitator_status,
                "comment": self.facilitator_comment,
                "reviewed_at": self.facilitator_reviewed_at,
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
    



