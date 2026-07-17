"""
URL configuration for backendauth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from backendauthapp import views
from django_rest_passwordreset.views import ResetPasswordConfirm       
from django_altcha import AltchaChallengeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api/user/register/", views.CreateUserView.as_view(), name="register"),
    path('api/practices/create/', views.PracticeCreateView.as_view(), name='practice-create'),
    path("api/logout/", views.LogoutAndBlacklistJWTTokens.as_view(), name='logout'),
    path("api/user/display_name/", views.DisplayUsernameView.as_view(), name="display_name"), 
    path('api/users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),     
    path('api/users/', views.UserListView.as_view(), name='user-list'),                          
    path('api/practices/', views.PracticeListView.as_view(), name='practice-list'),
    path('api/password_reset/confirm/', ResetPasswordConfirm.as_view(), name='password_reset_confirm'),     
    path("api/validate-reset-token/", views.ValidateResetTokenView.as_view(), name="validate-reset-token"), 
    path('api/password_reset/', views.CustomPasswordResetRequestView.as_view(), name='password_reset'),
    path("api/altcha/challenge/", AltchaChallengeView.as_view(), name="altcha_challenge")                    
]
