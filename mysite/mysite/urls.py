"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from webaccount.admin import admin_site
from django.contrib.auth import views as auth_views

# from django.conf.urls import url

from webaccount.views import *

from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin_site.urls),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='admin_password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('profile/',  profile_view , name="profile_url"),
    path('', index_view , name="index_url"),
    path('logout/', logout_view , name="logout_url"),
    # path('password_set/', password_set_user, name="password_set_user")
    path('change_password/', change_password, name = "change_password"),
    path('edit_profile/', edit_profile, name = "edit_profile"),
    # path('admin/password_change/', change_password, name='password_change'),
    path('send_quote/<int:num>',send_quote_view, name="send_quote_specific"),
    path('send_quote_send_mail/<int:client_id>', send_quote_mail_view, name="send_mail_quote_view"),
    path('update_status_approved/<int:client_id>/<int:document_id>/', change_document_submitted_status_aaproved, name="document_approved"),
    path('update_status_rejected/<int:client_id>/<int:document_id>/', change_document_submitted_status_rejected, name="document_rejected")

]

if settings.DEBUG:
    urlpatterns+= static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    
