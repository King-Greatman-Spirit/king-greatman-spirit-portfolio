from django.urls import path, re_path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    path('', views.client_dashboard, name='client_dashboard'), # domain/account -> client_dashboard

    # Use a unique pattern for admin_register
    re_path(r'^@dm1nR3g1str@t10n/$', views.admin_register, name='admin_register'),
    # Use a unique pattern for admin_login with symbols
    re_path(r'^@Dm1nL0g1n@ccess/$', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    
    path('admin_activate/<uidb64>/<token>', views.admin_activate, name='admin_activate'),
    path('admin_forgot_password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('admin_resetpassword_validate/<uidb64>/<token>/', views.admin_resetpassword_validate, name='admin_resetpassword_validate'),
    path('admin_reset_password/', views.admin_reset_password, name='admin_reset_password'),
]

