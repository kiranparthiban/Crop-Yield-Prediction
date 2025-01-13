from django.urls import path
from . import views
from .views import check_auth

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('check-auth/', check_auth, name='check_auth'),
]
