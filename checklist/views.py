
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
from .models import *
from django.contrib.auth import authenticate, login, logout
from .models import VisitsAchieved
from django.contrib.auth.decorators import login_required
# views.py
from django.shortcuts import get_object_or_404


# Create your views here.
def index(request):
    return render(request, 'manager/index.html')




def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate with email as username (because USERNAME_FIELD = 'email')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            

            # Redirect based on user_type
            if user.position == 'MANAGER':
                return redirect('index')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'auth/login.html')


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

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')



def visits_achieved_list(request):
    visits = VisitsAchieved.objects.select_related('added_by').order_by('-created_at')
    return render(request, 'users/visits_achieved.html', {'visits': visits})





@login_required
def add_visit(request):
    if request.method == 'POST':
        new = request.POST.get('new')
        old = request.POST.get('old')
        VisitsAchieved.objects.create(new=new, old=old, added_by=request.user)
    return redirect('visits_achieved_list')  # replace with your actual visits listing URL name



@login_required
def edit_visit(request, visit_id):
    visit = get_object_or_404(VisitsAchieved, id=visit_id)

    if request.method == 'POST':
        visit.new = request.POST.get('new')
        visit.old = request.POST.get('old')
        visit.save()
        return redirect('visits_achieved_list')

    return redirect('visits_achieved_list')

@login_required
def visit_detail(request, visit_id):
    visit = get_object_or_404(VisitsAchieved, id=visit_id)
    return render(request, 'users/visit_detail.html', {'visit': visit})

@login_required
def delete_visit(request, visit_id):
    visit = get_object_or_404(VisitsAchieved, id=visit_id)

    if request.method == 'POST':
        visit.delete()
        return redirect('visits_achieved_list')

    return redirect('visits_achieved_list')






from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import OrderQuotation, ProductionLine  # ✅ FIXED THIS LINE

@login_required
def quotations_list(request):
    quotations = OrderQuotation.objects.all().order_by('-created_at')  # latest first
    production_lines = ProductionLine.objects.all()
    return render(request, 'users/quotations_list.html', {
        'quotations': quotations,
        'production_lines': production_lines
    })



@login_required
def add_quotation(request):
    if request.method == 'POST':
        production_line_id = request.POST.get('production_line')
        client_name = request.POST.get('client_name')
        contact = request.POST.get('contact')
        quotation = request.POST.get('quotation')

        production_line = get_object_or_404(ProductionLine, id=production_line_id)

        OrderQuotation.objects.create(
            production_line=production_line,
            client_name=client_name,
            contact=contact,
            quotation=quotation,
            created_by=request.user
        )

    return redirect('quotations_list')


@login_required
def edit_quotation(request, quotation_id):
    quotation = get_object_or_404(OrderQuotation, id=quotation_id)  # ✅ FIXED MODEL NAME

    if request.method == 'POST':
        production_line_id = request.POST.get('production_line')
        client_name = request.POST.get('client_name')
        contact = request.POST.get('contact')
        quotation_value = request.POST.get('quotation')

        quotation.production_line = get_object_or_404(ProductionLine, id=production_line_id)
        quotation.client_name = client_name
        quotation.contact = contact
        quotation.quotation = quotation_value
        quotation.save()

    return redirect('quotations_list')


@login_required
def delete_quotation(request, quotation_id):
    quotation = get_object_or_404(OrderQuotation, id=quotation_id)
    quotation.delete()
    return redirect('quotations_list')

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import OrderQuotation

@login_required
def view_quotation(request, quotation_id):
    quotation = get_object_or_404(OrderQuotation, id=quotation_id)
    return render(request, 'users/view_quotation.html', {'quotation': quotation})


# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PaymentCollected, ProductionLine

from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required

@login_required
def payment_list(request):
    payments = PaymentCollected.objects.all().order_by('-created_at')
    production_lines = ProductionLine.objects.all()

    # Add safe formatted amount to each payment to avoid Decimal errors in template
    for payment in payments:
        try:
            # Assuming payment_amount is the field that causes the error
            payment.safe_payment_amount = f"{Decimal(payment.payment_amount):.2f}"
        except (InvalidOperation, TypeError, ValueError):
            # If value is invalid, set it to None or 0 or some default
            payment.safe_payment_amount = None

    return render(request, 'users/payment_list.html', {
        'payments': payments,
        'production_lines': production_lines,
    })


@login_required
def add_payment(request):
    if request.method == 'POST':
        PaymentCollected.objects.create(
            production_line_id=request.POST.get('production_line'),
            client_name=request.POST.get('client_name'),
            contact=request.POST.get('contact'),
            payment_amount=request.POST.get('payment_amount'),
            created_by=request.user
        )
    return redirect('payment_list')

@login_required
def edit_payment(request, pk):
    payment = get_object_or_404(PaymentCollected, pk=pk)
    if request.method == 'POST':
        payment.production_line_id = request.POST.get('production_line')
        payment.client_name = request.POST.get('client_name')
        payment.contact = request.POST.get('contact')
        payment.payment_amount = request.POST.get('payment_amount')
        payment.save()
    return redirect('payment_list')

@login_required
def delete_payment(request, pk):
    payment = get_object_or_404(PaymentCollected, pk=pk)
    if request.method == 'POST':
        payment.delete()
    return redirect('payment_list')

@login_required
def view_payment(request, pk):
    payment = get_object_or_404(PaymentCollected, pk=pk)
    return render(request, 'users/payment_detail.html', {'payment': payment})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import NewLead, ProductionLine

@login_required
def lead_list(request):
    leads = NewLead.objects.select_related('production_line', 'added_by').order_by('-created_at')
    production_lines = ProductionLine.objects.all()
    return render(request, 'users/leads.html', {
        'leads': leads,
        'production_lines': production_lines
    })

@login_required
def add_lead(request):
    if request.method == 'POST':
        production_line_id = request.POST.get('production_line')
        client_name = request.POST.get('client_name')
        contact = request.POST.get('contact')
        designation = request.POST.get('designation')
        location = request.POST.get('location')

        production_line = get_object_or_404(ProductionLine, id=production_line_id)

        NewLead.objects.create(
            production_line=production_line,
            client_name=client_name,
            contact=contact,
            designation=designation,
            location=location,
            added_by=request.user
        )
    return redirect('lead_list')

@login_required
def edit_lead(request, pk):
    lead = get_object_or_404(NewLead, pk=pk)
    if request.method == 'POST':
        production_line_id = request.POST.get('production_line')
        client_name = request.POST.get('client_name')
        contact = request.POST.get('contact')
        designation = request.POST.get('designation')
        location = request.POST.get('location')

        lead.production_line = get_object_or_404(ProductionLine, id=production_line_id)
        lead.client_name = client_name
        lead.contact = contact
        lead.designation = designation
        lead.location = location
        lead.save()

    return redirect('lead_list')

@login_required
def delete_lead(request, pk):
    lead = get_object_or_404(NewLead, pk=pk)
    lead.delete()
    return redirect('lead_list')



@login_required
def lead_detail_view(request, pk):
    lead = get_object_or_404(NewLead.objects.select_related("production_line", "added_by"), pk=pk)
    return render(request, "users/lead_detail.html", {"lead": lead})



from django.utils import timezone
from .models import RouteClient, ProductionLine

@login_required
def route_clients(request):
    route_clients = RouteClient.objects.select_related('production_line', 'added_by').order_by('-created_at')
    production_lines = ProductionLine.objects.all()

    if request.method == 'POST':
        RouteClient.objects.create(
            production_line_id=request.POST.get('production_line'),
            client_name=request.POST.get('client_name'),
            contact=request.POST.get('contact'),
            purpose=request.POST.get('purpose'),
            priority=request.POST.get('priority'),
            next_step=request.POST.get('next_step'),
            added_by=request.user,
        )
        return redirect('route_clients')

    return render(request, 'users/route_clients.html', {
        'route_clients': route_clients,
        'production_lines': production_lines,
        'PURPOSE_CHOICES': RouteClient.PURPOSE_CHOICES,
        'PRIORITY_CHOICES': RouteClient.PRIORITY_CHOICES,
    })

@login_required
def edit_route_client(request, pk):
    route = get_object_or_404(RouteClient, pk=pk)
    if request.method == 'POST':
        route.production_line_id = request.POST.get('production_line')
        route.client_name = request.POST.get('client_name')
        route.contact = request.POST.get('contact')
        route.purpose = request.POST.get('purpose')
        route.priority = request.POST.get('priority')
        route.next_step = request.POST.get('next_step')
        route.updated_at = timezone.now()
        route.save()
    return redirect('route_clients')

@login_required
def delete_route_client(request, pk):
    route = get_object_or_404(RouteClient, pk=pk)
    if request.method == 'POST':
        route.delete()
    return redirect('route_clients')


@login_required
def view_route_client(request, pk):
    route = get_object_or_404(RouteClient.objects.select_related('production_line', 'added_by'), pk=pk)
    return render(request, 'users/view_route_client.html', {
        'route': route
    })
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import VisitsAchieved

def manager_visits_achieved(request):
    visits_list = VisitsAchieved.objects.select_related('added_by').order_by('-created_at')
    paginator = Paginator(visits_list, 5)  # 10 items per page

    page = request.GET.get('page')
    try:
        visits = paginator.page(page)
    except PageNotAnInteger:
        visits = paginator.page(1)
    except EmptyPage:
        visits = paginator.page(paginator.num_pages)

    return render(request, 'manager/visits_achieved.html', {
        'visits': visits,
        'is_paginated': visits.has_other_pages(),


    })


def manager_view_visit_achieved(request, id):
    visit = get_object_or_404(VisitsAchieved, id=id)
    return render(request, 'manager/visit_detail.html', {'visit': visit})


# views.py
from django.core.paginator import Paginator
from .models import OrderQuotation

def manager_view_order_quotations(request):
    # Fetch all OrderQuotation objects and order them by created_at (latest first)
    order_quotations = OrderQuotation.objects.all().order_by('-created_at')  # Order by 'created_at' descending

    # Search functionality (if applicable)
    search_query = request.GET.get('q', '')
    if search_query:
        order_quotations = order_quotations.filter(
            client_name__icontains=search_query
        )

    # Pagination
    paginator = Paginator(order_quotations,5)  # 10 quotations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the paginated object to the template
    return render(request, 'manager/order_quotations.html', {
        'order_quotations': page_obj,  # Pass the Page object
        'is_paginated': page_obj.has_other_pages(),  # Use Page object's has_other_pages()
        'search_query': search_query
    })





def view_order_quotation_detail(request, id):
    quotation = OrderQuotation.objects.get(id=id)
    return render(request, 'manager/order_quotation_detail.html', {
        'quotation': quotation
    })




def manager_view_payments_collected(request):
    # Fetch all PaymentCollected objects ordered by creation date (descending)
    payments = PaymentCollected.objects.all().order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        payments = payments.filter(
            client_name__icontains=search_query
        )

    # Pagination
    paginator = Paginator(payments, 5)  # 5 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/payments_collected.html', {
        'payments': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query
    })


def manager_view_payment_detail(request, id):
    payment = get_object_or_404(PaymentCollected, id=id)
    return render(request, 'manager/payment_detail.html', {
        'payment': payment
    })

def manager_view_leads(request):
    leads = NewLead.objects.select_related('production_line', 'added_by').order_by('-created_at')

    search_query = request.GET.get('q', '')
    if search_query:
        leads = leads.filter(client_name__icontains=search_query)

    paginator = Paginator(leads, 5)  # 5 leads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/new_leads.html', {
        'leads': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query
    })


def manager_view_lead_detail(request, id):
    lead = get_object_or_404(NewLead, id=id)
    return render(request, 'manager/lead_detail.html', {'lead': lead})


def manager_view_route_clients(request):
    routes = RouteClient.objects.select_related('production_line', 'added_by').order_by('-created_at')
    search_query = request.GET.get('q', '')
    if search_query:
        routes = routes.filter(client_name__icontains=search_query)
    paginator = Paginator(routes, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'manager/route_clients_list.html', {
        'routes': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query
    })

def manager_view_route_client_detail(request, id):
    route = get_object_or_404(RouteClient, id=id)
    return render(request, 'manager/route_client_detail.html', {'route': route})

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

@login_required
def user_profile(request):
    user = request.user
    return render(request, 'manager/user_profile.html', {'user_obj': user})


from django.contrib.auth import authenticate, update_session_auth_hash



@login_required
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


def checklist(request):
    clients = [
        {"name": "John Michael", "function": "Manager", "status": "Online", "status_class": "bg-gradient-success", "employed": "23/04/18"},
        {"name": "Alexa Liras", "function": "Developer", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "11/01/19"},
        {"name": "Michael Levi", "function": "Engineer", "status": "Online", "status_class": "bg-gradient-success", "employed": "24/12/08"},
        {"name": "Laurent Perrier", "function": "Executive", "status": "Online", "status_class": "bg-gradient-success", "employed": "19/09/17"},
        {"name": "Richard Gran", "function": "Consultant", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "01/05/20"},
        {"name": "Sarah Mills", "function": "HR", "status": "Online", "status_class": "bg-gradient-success", "employed": "14/03/21"},
        {"name": "James White", "function": "Designer", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "30/10/22"},
        {"name": "John Michael", "function": "Manager", "status": "Online", "status_class": "bg-gradient-success", "employed": "23/04/18"},
        {"name": "Alexa Liras", "function": "Developer", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "11/01/19"},
        {"name": "Michael Levi", "function": "Engineer", "status": "Online", "status_class": "bg-gradient-success", "employed": "24/12/08"},
        {"name": "Laurent Perrier", "function": "Executive", "status": "Online", "status_class": "bg-gradient-success", "employed": "19/09/17"},
        {"name": "Richard Gran", "function": "Consultant", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "01/05/20"},
        {"name": "Sarah Mills", "function": "HR", "status": "Online", "status_class": "bg-gradient-success", "employed": "14/03/21"},
        {"name": "James White", "function": "Designer", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "30/10/22"},
        {"name": "John Michael", "function": "Manager", "status": "Online", "status_class": "bg-gradient-success", "employed": "23/04/18"},
        {"name": "Alexa Liras", "function": "Developer", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "11/01/19"},
        {"name": "Michael Levi", "function": "Engineer", "status": "Online", "status_class": "bg-gradient-success", "employed": "24/12/08"},
        {"name": "Laurent Perrier", "function": "Executive", "status": "Online", "status_class": "bg-gradient-success", "employed": "19/09/17"},
        {"name": "Richard Gran", "function": "Consultant", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "01/05/20"},
        {"name": "Sarah Mills", "function": "HR", "status": "Online", "status_class": "bg-gradient-success", "employed": "14/03/21"},
        {"name": "James White", "function": "Designer", "status": "Offline", "status_class": "bg-gradient-secondary", "employed": "30/10/22"},
    ]
   

    return render(request, 'users/checklist.html', {"clients": clients})


