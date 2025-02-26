from django.shortcuts import render
import requests
from django.shortcuts import render, get_object_or_404, redirect
from app.forms import UserForm, ProfileForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests
from .models import User, Profile, WeatherData
from django.contrib import messages
from app.forms import ChangePasswordForm
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings
import logging
# Create your views here.



def home(request):
    username = request.session.get('username')
    city_names = WeatherData.objects.values_list('city', flat=True).distinct()

    # Fetch user profile safely
    user_profile = None
    if request.user.is_authenticated:
        user_profile = Profile.objects.filter(user=request.user).first()  # Use 'user' instead of 'profile_user'

    return render(request, 'home.html', {
        'username': username,
        'city_names': city_names,
        'user_profile': user_profile
    })

# Set up logging
logger = logging.getLogger(__name__)

def registration(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])  # Hash password
            user.save()

            # Ensure profile is created
            profile, created = Profile.objects.get_or_create(user=user)
            profile.address = profile_form.cleaned_data.get("address")
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()

            # Send registration email
            try:
                send_mail(
                    'Registration Successful',
                    'Thanks for registering!',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False
                )
                messages.success(request, "Registration successful! A confirmation email has been sent.")
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                messages.error(request, "Registration successful, but email could not be sent.")

            return redirect("user_login")  # Redirect to login page

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    return render(request, "registration.html", {"user_form": user_form, "profile_form": profile_form})

from django.contrib.auth import update_session_auth_hash
@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep the user logged in

                # Send email with the new password
                send_mail(
                    'Password Changed Successfully',
                    f'Hello {request.user.username},\n\n'
                    f'Your password has been changed successfully.\n\n'
                    f'Here is your new password: {new_password}\n\n'
                    f'If you did not request this change, please reset your password immediately or contact support.\n\n'
                    f'Best Regards,\nYour Website Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Your password has been changed successfully.')
                return redirect('user_logout')  # Redirect to home page instead of logout
            else:
                messages.error(request, 'Old password is incorrect.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangePasswordForm()

    return render(request, 'change_password.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('un', '').strip()
        password = request.POST.get('pw', '').strip()
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(request, user)
            request.session['username'] = username
            return redirect('home')  # Redirect to home if login is successful
        else:
            messages.error(request, 'Invalid username or password')  # Send error message

    return render(request, 'user_login.html')
    

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib.auth.models import User

@login_required
def profile_display(request):
    un = request.session.get("username") or request.user.username  # Get username
    UO = get_object_or_404(User, username=un)
    
    # Get or create the profile if it does not exist
    PO, created = Profile.objects.get_or_create(user=UO)

    d = {"UO": UO, "PO": PO}
    return render(request, "profile_display.html", d)





@login_required
def search(request):
    weather_data = None
    error_message = None

    if request.method == 'POST':
        city_name = request.POST.get('city')
        if city_name:
            api_key = '30d4741c779ba94c470ca1f63045390a'  # Consider moving this to a settings file
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'

            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()

                # Extract relevant data
                temperature = round(data['main']['temp'] - 273.15, 2)
                humidity = data['main']['humidity']
                weather = data['weather'][0]['description']
                speed = data['wind']['speed']

                # Save data to WeatherData model
                username = request.session.get('username')
                if username:
                    user = User.objects.get(username=username)
                    WeatherData.objects.update_or_create(
                        username=user,
                        city=city_name,
                        defaults={
                            'temperature': temperature,
                            'humidity': humidity,
                            'weather': weather,
                            'speed': speed
                        }
                    )

                # Store weather data in session
                request.session['search_weather_data'] = {
                    'city': city_name,
                    'temperature': temperature,
                    'humidity': humidity,
                    'weather': weather,
                    'speed': speed
                }

                # Render search page with updated data
                return render(request, 'search.html', {'weather_data': {
                    'city': city_name,
                    'temperature': temperature,
                    'humidity': humidity,
                    'weather': weather,
                    'speed': speed
                }, 'error_message': error_message})

            except requests.exceptions.RequestException as e:
                error_message = f'Error fetching weather data: {e}'

    return render(request, 'search.html', {'weather_data': weather_data, 'error_message': error_message})



from django.core.cache import cache
import random
import string
from django.views.decorators.csrf import csrf_exempt
import json

# Function to generate a 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Email should not be empty.")
            return render(request, 'reset_password.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return render(request, 'reset_password.html')

        messages.success(request, "OTP sent successfully to your email.")
        return render(request, 'reset_password.html')  # ✅ FIX: No redirect, just reload the same page

    return render(request, 'reset_password.html')

def send_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            print(f"Received email for OTP: {email}")  # ✅ Debugging

            if not email:
                return JsonResponse({'success': False, 'message': 'Email field is required!'})

            user = User.objects.filter(email=email).first()  # Use .filter().first() to avoid errors
            if not user:
                return JsonResponse({'success': False, 'message': 'Email not found! Please check and try again.'})

            otp = generate_otp()
            cache.set(email, otp, timeout=300)  # Store OTP for 5 minutes

            print(f"Generated OTP for {email}: {otp}")  # ✅ Debugging

            send_mail(
                'Password Reset OTP',
                f'Hello {user.username},\n\n'
                f'Your OTP for password reset is: {otp}.\n'
                f'This OTP is valid for 5 minutes.\n\n'
                f'If you did not request this, please ignore this email.\n\n'
                f'Best Regards,\nYour Website Team',
                settings.DEFAULT_FROM_EMAIL,  # ✅ Uses default sender email from settings
                [email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': 'OTP sent successfully to your email!'})

        except Exception as e:
            print(f"Error in send_otp: {e}")  # ✅ Print error in Django console for debugging
            return JsonResponse({'success': False, 'message': 'Failed to send OTP. Please try again later!'}, status=500)
        

# View to verify OTP and reset password
def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        otp_entered = data.get('otp')
        new_password = data.get('new_password')

        otp_stored = cache.get(email)  # Retrieve stored OTP

        if otp_stored and otp_entered == otp_stored:
            try:
                user = User.objects.get(email=email)  # Get user
                user.password = make_password(new_password)  # Hash new password
                user.save()

                cache.delete(email)  # Remove OTP from cache after successful reset

                # ✅ Send confirmation email to user
                send_mail(
                    'Password Changed Successfully',
                    f'Hello {user.username},\n\n'
                    f'Your password has been changed successfully.\n\n'
                    f'Here is your new password: {new_password}\n\n'
                    f'If you did not request this change, please reset your password immediately or contact support.\n\n'
                    f'Best Regards,\nYour Website Team',
                    settings.DEFAULT_FROM_EMAIL,  # ✅ Ensure this is set in settings.py
                    [user.email],
                    fail_silently=False,
                )

                return JsonResponse({'success': True, 'message': 'Password reset successful! Redirecting to login.', 'redirect_url': '/user_login/'})
            
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found!'})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid or expired OTP!'})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm  # You'll create this form next
@login_required
def profile_update(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_display")  # Redirect back to profile page

    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile_update.html", {"form": form})