from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import UserProfile
import json
from django.middleware.csrf import get_token

# Get CSRF Token
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})

# Signup View
@ensure_csrf_cookie
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            bio = data.get('bio', '')  # Optional bio field

            if not username or not password:
                return JsonResponse({'error': 'All fields are required'}, status=400)

            # Check if the user already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create a new user
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Create a profile for the user
            UserProfile.objects.create(user=user, bio=bio)
            return JsonResponse({'message': 'User registered successfully'}, status=201)
        except IntegrityError as e:
            return JsonResponse({'error': 'A user with this username already exists'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Login View
@ensure_csrf_cookie
@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Both username and password are required'}, status=400)

            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Log the user in
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Logout View
@ensure_csrf_cookie
@csrf_exempt
def logout(request):
    if request.method == 'POST':
        try:
            auth_logout(request)  # Log the user out
            return JsonResponse({'message': 'Logout successful'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Check Authenticated User
@login_required
def check_auth(request):
    """
    Check if the user is authenticated.
    """
    user_profile = UserProfile.objects.get(user=request.user)
    return JsonResponse({
        "message": "User is authenticated",
        "username": request.user.username,
        "bio": user_profile.bio,
        "profile_picture_url": request.build_absolute_uri(user_profile.profile_picture.url) if user_profile.profile_picture else None
    }, status=200)
