from django import forms
from decimal import Decimal, ROUND_HALF_UP
from .models import VisitsAchieved, OrderQuotation, PaymentCollected, NewLead

SOFT_INPUT_CLASS = 'form-control soft-ui-input'

# --- Helper validator for Tanzanian phone numbers ---
from django.core.exceptions import ValidationError
import re

def validate_tz_phone(value):
    if not re.match(r'^\+255\d{9}$', value):
        raise ValidationError("Enter a valid Tanzanian phone number, e.g. +255712345678.")

# --- Visits Achieved ---
class VisitsAchievedForm(forms.ModelForm):
    class Meta:
        model = VisitsAchieved
        exclude = ['submission', 'added_by', 'created_at', 'updated_at', 'status']
        widgets = {
            'new': forms.NumberInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'e.g. 5'
            }),
            'old': forms.NumberInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'e.g. 3'
            }),
        }

# --- Order Quotation ---
class OrderQuotationForm(forms.ModelForm):
    class Meta:
        model = OrderQuotation
        exclude = ['submission', 'created_by', 'created_at', 'updated_at', 'status']
        widgets = {
            'production_line': forms.Select(attrs={'class': SOFT_INPUT_CLASS}),
            'client_name': forms.TextInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'Client Name'
            }),
            'contact': forms.TextInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'e.g. +255712345678'
            }),
            'quotation': forms.NumberInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'Amount in TZS'
            }),
        }

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        validate_tz_phone(contact)
        return contact

# --- Payment Collected ---
class PaymentCollectedForm(forms.ModelForm):
    class Meta:
        model = PaymentCollected
        exclude = ['submission', 'created_by', 'created_at', 'updated_at', 'status']
        widgets = {
            'production_line': forms.Select(attrs={'class': SOFT_INPUT_CLASS}),
            'client_name': forms.TextInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'Client Name'
            }),
            'contact': forms.TextInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'e.g. +255712345678'
            }),
            'payment_amount': forms.NumberInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'Amount in TZS'
            }),
        }

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        validate_tz_phone(contact)
        return contact

# --- New Lead ---
class NewLeadForm(forms.ModelForm):
    class Meta:
        model = NewLead
        exclude = ['submission', 'added_by', 'created_at', 'updated_at', 'status']
        widgets = {
            'production_line': forms.Select(attrs={'class': SOFT_INPUT_CLASS}),
            'client_name': forms.TextInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'Client Name'
            }),
            'contact': forms.TextInput(attrs={
                'class': SOFT_INPUT_CLASS,
                'placeholder': 'e.g. +255712345678'
            }),
            'designation': forms.Select(attrs={'class': SOFT_INPUT_CLASS}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'data' in kwargs:
            data = self.data.copy()
            lat = data.get(self.add_prefix('latitude'))
            lon = data.get(self.add_prefix('longitude'))
            try:
                if lat:
                    lat_clean = Decimal(lat).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
                    data[self.add_prefix('latitude')] = str(lat_clean)
                if lon:
                    lon_clean = Decimal(lon).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
                    data[self.add_prefix('longitude')] = str(lon_clean)
            except Exception as e:
                print(">>> Error cleaning coordinates in __init__:", e)
            self.data = data

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        validate_tz_phone(contact)
        return contact

# --- Manager Review ---
from .models import STATUS_CHOICES

class ManagerReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Select Status",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    comment = forms.CharField(
        label="Comment",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your comment here...'
        })
    )

# forms.py

from django import forms
from .models import FormSubmission

class DispatchTimeForm(forms.ModelForm):
    class Meta:
        model = FormSubmission
        fields = ['dispatch_time']
        widgets = {
            'dispatch_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }


