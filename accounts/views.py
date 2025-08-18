from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomRegisterForm, CustomLoginForm


def register_view(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("product_list")  # or wherever you want
    else:
        form = CustomRegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("product_list")
    else:
        form = CustomLoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')