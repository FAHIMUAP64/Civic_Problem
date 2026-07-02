from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    return render(request, 'home.html')


def role_selection(request):
    action = request.GET.get('action', 'login')
    context = {'action': action}
    return render(request, 'role_selection.html', context)


# ─── Citizen Register ───────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        from .models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='citizen',
        )
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'register.html')


# ─── Citizen Login ───────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role != 'citizen':
                messages.error(request, 'Please use the Authority login page.')
                return render(request, 'login.html')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# ─── Authority Register ───────────────────────────────────────────────────────

def authority_register(request):
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        level     = request.POST.get('level', 'member')
        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
            return render(request, 'authority_register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authority_register.html')

        from .models import User, AuthorityProfile
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'authority_register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='authority',
        )
        AuthorityProfile.objects.create(user=user, level=level)
        messages.success(request, 'Authority account created! Awaiting admin verification.')
        return redirect('authority_login')

    return render(request, 'authority_register.html')


# ─── Authority Login ──────────────────────────────────────────────────────────

def authority_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role not in ('authority', 'admin'):
                messages.error(request, 'This login is for Authority users only.')
                return render(request, 'authority_login.html')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'authority_login.html')


# ─── Dashboard (role-based redirect) ─────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.role == 'citizen':
        return render(request, 'citizen_dashboard.html')
    elif request.user.role in ('authority', 'admin'):
        return render(request, 'authority_dashboard.html')
    else:
        messages.error(request, 'Unknown role. Please contact support.')
        return redirect('home')


# ─── Logout ───────────────────────────────────────────────────────────────────

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
