from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
import re
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."

    return True, "Password is strong!"
    

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "accounts/register.html")
    
    def post(self, request, *args, **kwargs):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exist")
            return redirect("accounts:register_view")
        
        res, msg = is_valid_password(password)
        print(res, msg)
        if not res:
            messages.error(request, msg)
            return redirect("accounts:register_view")


        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        messages.success(request, "Account created successfuly!")
        return redirect("accounts:login_view")
    

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "accounts/login.html")
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("dashboard:dashboard_my_articles_view")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("accounts:login_view")
        


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Logout Successful!!!")
        return redirect("accounts:login_view")