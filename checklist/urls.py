from django.urls import path
from . import views

urlpatterns = [
    path('manager-dashbord', views.index, name='index'),
    path('', views.login_user, name='login'),
    path('auth/register/', views.register, name='register'),
    path('users/dashboard/', views.dashboard, name='dashboard'),
    path('my-submissions/', views.my_submitted_forms, name='my_submitted_forms'),
    path('logout/', views.logout_user, name='logout'),
    path('submissions/', views.user_submission_list, name='user_submission_list'),
    path('submit-all/', views.submit_all_forms, name='submit_all_forms'),
     path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('production-lines/', views.manager_view_production_lines, name='manager_view_production_lines'),
    path('production-lines/<int:id>/', views.manager_view_production_line_detail, name='manager_view_production_line_detail'),
    path('users/', views.user_list_view, name='manager_view_users'),
    path('users/<int:user_id>/', views.user_detail_view, name='manager_view_user_detail'),
    path('profile/', views.user_profile, name='manager_user_profile'),
     path('change-password/', views.change_password, name='change_password'),
     path('manager/submissions/', views.manager_submissions_list, name='manager_submissions_list'),
      path('manager/submissions/<int:submission_id>/', views.manager_submission_detail, name='manager_submission_detail'),
      path('manager-review/<int:form_id>/', views.manager_review, name='manager_review'),


]
