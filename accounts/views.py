from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm

def home(request):
    return render(request, 'home.html')


def register(request):
    form = RegisterForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')


def dashboard(request):
    if request.user.role == 'citizen':
        return render(request, 'citizen_dashboard.html')
    else:
        return render(request, 'authority_dashboard.html')