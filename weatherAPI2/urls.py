"""
URL configuration for weatherAPI2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from app import views
from app.views import *
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Redirect root URL to home view
    path('home/', home, name='home'),
    path('registration/', registration, name='registration'),
    path('user_login/', user_login, name='user_login'),
    path('user_logout/', user_logout, name='user_logout'),
    path('profile_display/', profile_display, name='profile_display'),
    path('change_password/', change_password, name='change_password'),
    path('search/', search, name='search'),
    path("reset_password/", reset_password, name="reset_password"),
    path('send_otp/', send_otp, name='send_otp'),  # Ensure this is here
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('profile_update/', views.profile_update, name='profile_update'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)