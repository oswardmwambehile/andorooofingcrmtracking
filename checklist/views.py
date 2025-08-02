
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
from .models import *
from django.contrib.auth import authenticate, login, logout
from .models import VisitsAchieved
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import VisitsAchieved
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderQuotation, ProductionLine  # ✅ FIXED THIS LINE


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PaymentCollected, ProductionLine



# Create your views here.
def index(request):
    return render(request, 'manager/index.html')




from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages

# The POSITION_CHOICES tuple
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

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate with email as username (because USERNAME_FIELD = 'email')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Check user's position and redirect accordingly
            if user.position in ['Head of Sales', 'Facilitator', 'Product Brand Manager', 'Zonal Sales Executive']:
                return redirect('index')  # Redirect to 'index' for these positions
            elif user.position in ['Corporate Officer', 'Mobile Sales Officer', 'Desk Sales Officer']:
                return redirect('dashboard')  # Redirect to 'dashboard' for these positions
            else:
                return redirect('home')  # Default redirect for all other positions
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    # Handle GET request: Render the login page/form
    return render(request, 'auth/login.html')  # Ensure you have a 'login.html' template



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name= request.POST.get('last_name')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        profile_picture = request.FILES.get('profile_picture')
        position = request.POST.get('position')
        zone = request.POST.get('zone')
        branch = request.POST.get('branch')
        contact = request.POST.get('contact')

        if password != password1:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
             last_name=last_name,
            profile_picture=profile_picture,
            position=position,
            zone=zone,
            branch=branch,
            contact=contact
        )

        messages.success(request, "Account created successfully.")
        return redirect('login')

    return render(request, 'auth/register.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from django.forms import modelformset_factory
from django.contrib import messages

from .models import FormSubmission, OrderQuotation, PaymentCollected, NewLead
from .forms import VisitsAchievedForm, OrderQuotationForm, PaymentCollectedForm, NewLeadForm



def submit_all_forms(request):
    OrderQuotationFormSet = modelformset_factory(OrderQuotation, form=OrderQuotationForm, extra=1, can_delete=True)
    PaymentFormSet = modelformset_factory(PaymentCollected, form=PaymentCollectedForm, extra=1, can_delete=True)
    LeadFormSet = modelformset_factory(NewLead, form=NewLeadForm, extra=1, can_delete=True)

    if request.method == 'POST':
        visit_form = VisitsAchievedForm(request.POST, prefix='visit')
        quotation_formset = OrderQuotationFormSet(request.POST, prefix='quote')
        payment_formset = PaymentFormSet(request.POST, prefix='payment')
        lead_formset = LeadFormSet(request.POST, prefix='lead')

        # Debug validity status
        print("Visit form valid:", visit_form.is_valid())
        print("Quotation formset valid:", quotation_formset.is_valid())
        print("Payment formset valid:", payment_formset.is_valid())
        print("Lead formset valid:", lead_formset.is_valid())

        # Print errors if any
        if not visit_form.is_valid():
            print("Visit form errors:", visit_form.errors)

        if not quotation_formset.is_valid():
            for form in quotation_formset:
                print("Quotation form errors:", form.errors)

        if not payment_formset.is_valid():
            for form in payment_formset:
                print("Payment form errors:", form.errors)

        if not lead_formset.is_valid():
            for form in lead_formset:
                print("Lead form errors:", form.errors)

        # Save if all valid
        if visit_form.is_valid() and quotation_formset.is_valid() and payment_formset.is_valid() and lead_formset.is_valid():
            with transaction.atomic():
                submission = FormSubmission.objects.create(user=request.user)

                visit = visit_form.save(commit=False)
                visit.added_by = request.user
                visit.submission = submission
                visit.save()
                print("✅ Visit saved.")

                for form in quotation_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        obj = form.save(commit=False)
                        obj.created_by = request.user
                        obj.submission = submission
                        obj.save()
                        print("✅ Quotation saved:", obj)

                for form in payment_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        obj = form.save(commit=False)
                        obj.created_by = request.user
                        obj.submission = submission
                        obj.save()
                        print("✅ Payment saved:", obj)

                for form in lead_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        obj = form.save(commit=False)
                        obj.added_by = request.user
                        obj.submission = submission
                        obj.save()
                        print("✅ Lead saved:", obj)

            
            return redirect('user_submission_list')  # <-- Make sure 'dashboard' exists in your urls.py
        else:
            messages.error(request, "There was an error in one or more forms. Please correct and resubmit.")
    else:
        visit_form = VisitsAchievedForm(prefix='visit')
        quotation_formset = OrderQuotationFormSet(queryset=OrderQuotation.objects.none(), prefix='quote')
        payment_formset = PaymentFormSet(queryset=PaymentCollected.objects.none(), prefix='payment')
        lead_formset = LeadFormSet(queryset=NewLead.objects.none(), prefix='lead')

    return render(request, 'users/submit_all.html', {
        'visit_form': visit_form,
        'quotation_formset': quotation_formset,
        'payment_formset': payment_formset,
        'lead_formset': lead_formset,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import FormSubmission
from django.core.paginator import Paginator

def user_submission_list(request):
    submissions = FormSubmission.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(submissions, 25)  # Show 3 submissions per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/my_submitted_forms.html', {
        'page_obj': page_obj
    })




from django.core.paginator import Paginator
from django.shortcuts import render
from .models import FormSubmission  # Adjust based on your app structure

def manager_submissions_list(request):
    status = request.GET.get('final_status')

    if status:
        # Show all with the selected status
        submissions = FormSubmission.objects.filter(final_status=status)
    else:
        # Default behavior: exclude approved ones
        submissions = FormSubmission.objects.exclude(final_status='approved')

    submissions = submissions.order_by('-created_at')

    paginator = Paginator(submissions, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/manager_submitted_forms.html', {
        'page_obj': page_obj,
    })



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from geopy.geocoders import Nominatim
from django.db.models import Sum  # ✅ Add this


from django.utils.timezone import now
from django import forms
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from .models import FormSubmission
from geopy.geocoders import Nominatim

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.utils.timezone import now
import pytz
from geopy.geocoders import Nominatim

from .models import FormSubmission


from django.shortcuts import render, get_object_or_404
from .models import FormSubmission
from django.db.models import Sum
from geopy.geocoders import Nominatim

def submission_detail(request, submission_id):
    submission = get_object_or_404(FormSubmission, id=submission_id, user=request.user)

    leads = submission.leads.all()
    quotations = submission.quotations.all()
    payments = submission.payments.all()

    total_payment = payments.aggregate(total=Sum('payment_amount'))['total'] or 0
    total_quotation = quotations.aggregate(total=Sum('quotation'))['total'] or 0

    geolocator = Nominatim(user_agent="your_app_name")

    def get_place_name(lat, lon):
        try:
            location = geolocator.reverse((lat, lon), timeout=10)
            return location.address if location else "Unknown Location"
        except:
            return "Unknown Location"

    for lead in leads:
        if lead.latitude and lead.longitude:
            lead.place_name = get_place_name(lead.latitude, lead.longitude)
        else:
            lead.place_name = "Location not available"

    # Prepare reviewers' info to pass to the template
    reviewers_info = []
    for reviewer, status_field, comment_field, reviewed_at_field in [
        ('zonal_reviewer', 'zonal_status', 'zonal_comment', 'zonal_reviewed_at'),
        ('product_manager', 'product_manager_status', 'product_manager_comment', 'product_manager_reviewed_at'),
        ('facilitator', 'facilitator_status', 'facilitator_comment', 'facilitator_reviewed_at'),
    ]:
        reviewer_obj = getattr(submission, reviewer)
        if reviewer_obj:
            reviewers_info.append({
                "reviewer": reviewer_obj,
                "status": getattr(submission, status_field),
                "comment": getattr(submission, comment_field),
                "reviewed_at": getattr(submission, reviewed_at_field),
            })

    return render(request, 'users/submission_detail.html', {
        'submission': submission,
        'visits': submission.visits.all(),
        'quotations': quotations,
        'payments': payments,
        'leads': leads,
        'total_payment': total_payment,
        'total_quotation': total_quotation,
        'reviewers_info': reviewers_info,  # Pass the reviewer details to the template
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import DispatchTimeForm
from .models import FormSubmission

# views.py
from django.shortcuts import get_object_or_404, render, redirect
from .models import FormSubmission
from .forms import DispatchTimeForm

def dispatch_time_view(request, submission_id):
    # Get the FormSubmission object by ID
    submission = get_object_or_404(FormSubmission, id=submission_id)

    # If the dispatch time is already set, redirect to the submission detail page
    if submission.dispatch_time:
        return redirect('submission_detail', submission_id=submission.id)

    # Handle the form submission
    if request.method == 'POST':
        form = DispatchTimeForm(request.POST)
        if form.is_valid():
            # Update the form submission with the dispatch time
            submission.dispatch_time = form.cleaned_data['dispatch_time']
            submission.save()
            return redirect('submission_detail', submission_id=submission.id)
    else:
        # Initialize the form (no need to pass 'instance' as it's not a ModelForm)
        form = DispatchTimeForm()

    # Pass the form and submission object to the template
    return render(request, 'users/dispatch_time_form.html', {'form': form, 'form_submission': submission})



def manager_submission_detail(request, submission_id):
    # Removed user=request.user filter
    submission = get_object_or_404(FormSubmission, id=submission_id)

    leads = submission.leads.all()
    quotations = submission.quotations.all()
    payments = submission.payments.all()

    # Sum payments and quotations
    total_payment = payments.aggregate(total=Sum('payment_amount'))['total'] or 0
    total_quotation = quotations.aggregate(total=Sum('quotation'))['total'] or 0

    # Initialize geolocator
    geolocator = Nominatim(user_agent="your_app_name")

    def get_place_name(lat, lon):
        try:
            location = geolocator.reverse((lat, lon), timeout=10)
            return location.address if location else "Unknown Location"
        except:
            return "Unknown Location"

    for lead in leads:
        if lead.latitude and lead.longitude:
            lead.place_name = get_place_name(lead.latitude, lead.longitude)
        else:
            lead.place_name = "Location not available"

    return render(request, 'manager/manager_submission_detail.html', {
        'submission': submission,
        'visits': submission.visits.all(),
        'quotations': quotations,
        'payments': payments,
        'leads': leads,
        'total_payment': total_payment,
        'total_quotation': total_quotation,
    })



# views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from itertools import chain
from operator import attrgetter

from .models import VisitsAchieved, OrderQuotation, PaymentCollected, NewLead


def my_submitted_forms(request):
    user = request.user

    # Add metadata to each object so we can display them uniformly
    visits = VisitsAchieved.objects.filter(added_by=user)
    for v in visits:
        v.form_type = 'visit'
        v.user_email = user.email
        v.form_id = v.id

    quotations = OrderQuotation.objects.filter(created_by=user)
    for q in quotations:
        q.form_type = 'quotation'
        q.user_email = user.email
        q.form_id = q.id

    payments = PaymentCollected.objects.filter(created_by=user)
    for p in payments:
        p.form_type = 'payment'
        p.user_email = user.email
        p.form_id = p.id

    leads = NewLead.objects.filter(added_by=user)
    for l in leads:
        l.form_type = 'lead'
        l.user_email = user.email
        l.form_id = l.id

    # Combine all objects into one list and sort by creation date
    all_forms = list(chain(visits, quotations, payments, leads))
    all_forms.sort(key=attrgetter('created_at'), reverse=True)

    return render(request, 'users/my_submitted_forms.html', {'forms': all_forms})


# views.py



def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now
from .models import FormSubmission
from .forms import ManagerReviewForm




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import FormSubmission
from .forms import ManagerReviewForm  # Your form with 'status' and 'comment'

def manager_review(request, form_id):
    submission = get_object_or_404(FormSubmission, pk=form_id)

    # Prevent duplicate reviews by the same user
    if submission.is_reviewed_by(request.user):
        messages.warning(request, "You have already reviewed this submission.")
        return redirect('manager_submissions_list')

    if request.method == 'POST':
        form = ManagerReviewForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            comment = form.cleaned_data['comment']
            try:
                submission.save_review(request.user, status, comment)
                messages.success(request, "Your review has been submitted.")
                return redirect('manager_submissions_list')
            except ValueError as ve:
                messages.error(request, str(ve))
    else:
        form = ManagerReviewForm()

    return render(request, 'manager/manager_review.html', {
        'form': form,
        'submission': submission,
    })




def manager_view_production_lines(request):
    lines = ProductionLine.objects.order_by('-created_at')
    search_query = request.GET.get('q', '')
    if search_query:
        lines = lines.filter(name__icontains=search_query)
    paginator = Paginator(lines, 5)  # 5 per page
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'manager/production_lines_list.html', {
        'lines': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query
    })

def manager_view_production_line_detail(request, id):
    production_line = get_object_or_404(ProductionLine, id=id)
    return render(request, 'manager/production_line_detail.html', {
        'production_line': production_line
    })

from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404

User = get_user_model()

def user_list_view(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'manager/user_list.html', {'users': users})

def user_detail_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    return render(request, 'manager/user_detail.html', {'user_obj': user_obj})


def user_profile(request):
    user = request.user
    return render(request, 'manager/user_profile.html', {'user_obj': user})


from django.contrib.auth import authenticate, update_session_auth_hash



def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)  # keep user logged in
            messages.success(request, 'Password changed successfully.')
            return redirect('change_password')

    return render(request, 'manager/change_password.html')




def dashboard(request):
    return render(request, 'users/dashboard.html')


