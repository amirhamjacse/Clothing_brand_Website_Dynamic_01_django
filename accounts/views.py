from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Order
from accounts.models import UserProfile

def user_register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        full_name = request.POST.get('full_name', '').strip()

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'accounts/register.html')

        first_name = full_name.split()[0] if full_name else username
        last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.save()

        login(request, user)
        messages.success(request, f'Welcome to AHMZ Lifestyle, {user.first_name}!')
        return redirect('accounts:profile')

    return render(request, 'accounts/register.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        username_or_phone = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Check by username or email
        user = authenticate(request, username=username_or_phone, password=password)
        if not user:
            # Try to match by email
            try:
                user_obj = User.objects.get(email=username_or_phone)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next') or 'store:home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        division = request.POST.get('division', 'Dhaka').strip()
        district = request.POST.get('district', 'Dhaka').strip()
        address = request.POST.get('address', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        profile.phone = phone
        profile.division = division
        profile.district = district
        profile.address = address
        profile.save()

        messages.success(request, 'Profile details updated.')
        return redirect('accounts:profile')

    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)
