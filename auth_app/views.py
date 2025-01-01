from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm

from django.contrib.auth import login, logout
from .middlewares import auth,guest
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from .forms import CustomPasswordChangeForm,SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

# Create your views here.


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the user data
            user = form.save()
            # Log the user in immediately after successful signup
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
       
    else:
        form = SignUpForm()

    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('dashboard')
    else:
        initial_data = {'username':'', 'password':''}
        form = AuthenticationForm(initial=initial_data)
    return render(request, 'auth/login.html',{'form':form})
  
def forgot_password_view(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "auth/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': 'example.com',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_email = EmailMessage(subject, email, to=[user.email])
                        send_email.send()
                    except:
                        return redirect('password_reset_done')
    else:

        password_reset_form = PasswordResetForm()
    return render(request, 'auth/forgot_password.html', {'password_reset_form': password_reset_form})

@login_required
def change_password_view(request):
    fm=PasswordChangeForm(user=request.user)
    return render(request,'auth/change_password.html',{'fm':fm})



@login_required
def dashboard_view(request):
    return render(request, 'auth/dashboard.html')

@login_required
def profile_view(request):
    return render(request, 'auth/profile.html', {'user': request.user})
    

def logout_view(request):
    logout(request)
    return redirect('login')