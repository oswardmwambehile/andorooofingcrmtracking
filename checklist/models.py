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
        extra_fields.setdefault('user_type', 'user')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=30, default='user')
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email




class ProductionLine(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Set once on creation
    updated_at = models.DateTimeField(auto_now=True)      # Updated on each save

    def __str__(self):
        return self.name





class VisitsAchieved(models.Model):
    new = models.IntegerField()
    old = models.IntegerField()
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # This supports custom user models
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits_added',
        help_text="User who added this record (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"New: {self.new}, Old: {self.old}"




class OrderQuotation(models.Model):
    production_line = models.ForeignKey('ProductionLine', on_delete=models.CASCADE, related_name='quotations')
    client_name = models.CharField(max_length=150)
    contact = models.CharField(max_length=100)
    quotation = models.DecimalField(max_digits=10, decimal_places=2)

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
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='payments')
    client_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)  # e.g., phone or email
    payment_amount = models.DecimalField(max_digits=16, decimal_places=2)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments_collected')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.payment_amount}"


from django.db import models
from django.conf import settings

class NewLead(models.Model):
    DESIGNATION_CHOICES = [
        ('Owner', 'Owner'),
        ('Engineer', 'Engineer'),
        ('Contractor', 'Contractor'),
    ]

    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='leads')
    client_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.designation}"



from django.db import models
from django.conf import settings

# Assuming you already have this model elsewhere:
# class ProductionLine(models.Model):
#     name = models.CharField(max_length=100)

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
        ProductionLine,  # Replace 'yourapp' with your actual app name
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

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # or use 'yourapp.Customer' if not the default user model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_route_clients'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} ({self.production_line})"
    



