from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

from django.contrib import admin

admin.site.site_header = "Welcome to Admin"
admin.site.site_title = "Welcome to Admin"
admin.site.index_title = "Welcome to ANDO Admin Dashboard"


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'username', 'user_type', 'is_staff', 'is_active', 'display_profile_picture', 'date_joined',)
    list_filter = ('is_staff', 'is_active', 'user_type')
    search_fields = ('email', 'username')
    ordering = ('email',)

    readonly_fields = ('date_joined', 'display_profile_picture')

    fieldsets = (
        ('Login Info', {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('username', 'user_type', 'profile_picture', 'display_profile_picture')
        }),
        ('Permissions & Groups', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'user_type', 'profile_picture', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.profile_picture.url)
        return "No Image"
    display_profile_picture.short_description = 'Profile Picture'

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import admin
from .models import ProductionLine, VisitsAchieved

@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')  # Columns in the list view
    search_fields = ('name',)  # Add search by name
    ordering = ('-created_at',)  # Newest first
    list_filter = ('created_at', 'updated_at')  # Filters on the sidebar
    readonly_fields = ('created_at', 'updated_at')  # Prevent editing these in the form


from django.contrib import admin
from .models import VisitsAchieved

@admin.register(VisitsAchieved)
class VisitsAchievedAdmin(admin.ModelAdmin):
    list_display = ('id', 'new', 'old', 'added_by', 'created_at', 'updated_at')
    search_fields = ('new', 'old')
    ordering = ('-created_at',)
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'added_by')  # added_by is not editable

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user  # Automatically set to the logged-in admin
        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import OrderQuotation

@admin.register(OrderQuotation)
class OrderQuotationAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'production_line', 'contact', 'quotation', 'created_by', 'created_at')
    list_filter = ('production_line', 'created_by', 'created_at')
    search_fields = ('client_name', 'contact', 'production_line__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'created_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


from django.contrib import admin
from .models import PaymentCollected

@admin.register(PaymentCollected)
class PaymentCollectedAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'production_line',
        'client_name',
        'contact',
        'payment_amount',
        'created_by',
        'created_at',
        'updated_at'
    )
    list_filter = ('production_line', 'created_by', 'created_at')
    search_fields = ('client_name', 'contact', 'created_by__username', 'production_line__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


# admin.py
from django.contrib import admin
from .models import NewLead

@admin.register(NewLead)
class NewLeadAdmin(admin.ModelAdmin):
    list_display = (
        'client_name',
        'contact',
        'designation',
        'production_line',
        'location',
        'added_by',
        'created_at',
        'updated_at',
    )
    list_filter = ('designation', 'production_line', 'created_at')
    search_fields = ('client_name', 'contact', 'location', 'added_by__username')
    autocomplete_fields = ['production_line', 'added_by']
    readonly_fields = ('created_at', 'updated_at')



from django.contrib import admin
from .models import RouteClient

@admin.register(RouteClient)
class RouteClientAdmin(admin.ModelAdmin):
    list_display = (
        'client_name',
        'production_line',
        'contact',
        'purpose',
        'priority',
        'next_step_short',
        'added_by',
        'created_at',
    )
    list_filter = ('purpose', 'priority', 'production_line', 'added_by', 'created_at')
    search_fields = ('client_name', 'contact', 'next_step', 'production_line__name', 'added_by__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Client Info', {
            'fields': ('production_line', 'client_name', 'contact')
        }),
        ('Visit Details', {
            'fields': ('purpose', 'priority', 'next_step')
        }),
        ('Meta', {
            'fields': ('added_by', 'created_at', 'updated_at')
        }),
    )

    def next_step_short(self, obj):
        return (obj.next_step[:40] + '...') if len(obj.next_step) > 40 else obj.next_step
    next_step_short.short_description = 'Next Step'




