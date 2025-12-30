from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import random
import string


# Create your views here.
def register(request):
    title = "Registration"
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)  # Add request.FILES

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0] + ''.join(random.choices(string.ascii_uppercase + string.digits, k=len(email.split('@')[0])))  # create username from email address

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.image = form.cleaned_data['image']  # Save the uploaded image
            user.save()

            # USER ACTIVATION EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            return redirect('/accounts/login/?command=verification&email='+email)     

    else:
        form = RegistrationForm() # render registration form

    context = {
        'form': form,
        'title': title,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    title = "Login"
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Your now logged in.')
            return redirect('client_dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    context = {
        'title': title,
    }
    return render(request, 'accounts/login.html', context)

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'you are logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

@login_required(login_url = 'login')
def client_dashboard(request):
    title = "Client Dashboard"
    user = get_object_or_404(Account, id=request.user.id)
    form = RegistrationForm(request.POST or None, instance=user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('client_dashboard')

    context = {
        'title': title,
        'form': form,
    }

    return render(request, 'accounts/client_dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists(): # True or False
            user = Account.objects.get(email__iexact=email)

            # reset password EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please set your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Invalid reset password link!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


def admin_register(request):
    title = "Admin Registration"
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)  # Handle image upload

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0] + ''.join(random.choices(string.ascii_uppercase + string.digits, k=len(email.split('@')[0])))  # Create username from email address

            # Create an admin user
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.image = form.cleaned_data['image']  # Save the uploaded image
            user.is_admin = True  # Set the user as an admin
            user.save()

            # USER ACTIVATION EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Please activate your admin account'
            message = render_to_string('accounts/admin/admin_account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            return redirect('/accounts/@Dm1nL0g1n@ccess/?command=verification&email=' + email)

    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'title': title,
    }
    return render(request, 'accounts/admin/admin_register.html', context)

    
def admin_login(request):
    title = "Admin Login"
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None and user.is_admin:
            auth.login(request, user)
            messages.success(request, 'Admin login successful.')
            return redirect('company_dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('admin_login')

    context = {
        'title': title,
    }
    return render(request, 'accounts/admin/admin_login.html', context)

@login_required(login_url = 'admin_login')
def admin_logout(request):
    auth.logout(request)
    messages.success(request, 'Admin logout successful.')
    return redirect('admin_login')

def admin_activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        if user.is_admin:
            messages.success(request, 'Congratulations Admin account activated.')
            return redirect('admin_login') 
        else:
            messages.success(request, 'Your account is activated.')
            return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('admin_register')
    
def admin_forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email, is_admin=True).exists():
            user = Account.objects.get(email__iexact=email, is_admin=True)
            current_site = get_current_site(request)
            mail_subject = 'Admin Reset Your Password'
            message = render_to_string('accounts/admin/admin_reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Admin password reset email has been sent to your email address.')
            return redirect('admin_login')
        else:
            messages.error(request, 'Admin account does not exist')
            return redirect('admin_forgot_password')
    return render(request, 'accounts/admin/admin_forgot_password.html')

def admin_resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid, is_admin=True)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please set your admin password')
        return redirect('admin_reset_password')
    else:
        messages.error(request, 'Invalid admin reset password link!')
        return redirect('admin_login')
    
def admin_reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid, is_admin=True)
            user.set_password(password)
            user.save()
            messages.success(request, 'Admin password reset successful')
            return redirect('admin_login')
        else:
            messages.error(request, 'Admin password does not match!')
            return redirect('admin_reset_password')
    else:
        return render(request, 'accounts/admin/admin_reset_password.html')
    
    