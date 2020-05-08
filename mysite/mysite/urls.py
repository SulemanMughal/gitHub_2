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
from django.urls import include
# from django.conf.urls import url

from webaccount.views import *

from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin_site.urls),
    path('select2/', include('django_select2.urls')),
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
    path('update_status_rejected/<int:client_id>/<int:document_id>/', change_document_submitted_status_rejected, name="document_rejected"),
    path("send-consultant-requets-quote/<int:client_id>/<int:consultant_request_id>/", sendConsultantRequestQuote, name="sendConsultantRequestQuote_URL"),
    path('send_quote_send_mail_consultant/<int:client_id>/<int:consultant_request_id>/', save_send_quote_consultant_mail_view, name="send_mail_consultant_quote_URL"),
    path('reject_quote_consultant_send_mail/<int:client_id>/<int:consultant_request_id>/', reject_quote_consultant_mail_view, name="reject_mail_consultant_quote_URL"),
    path('confirm_quote_consultant_send_mail/<int:client_id>/<int:consultant_request_id>/', confirm_quote_consultant_mail_view, name="confirm_mail_consultant_quote_URL"),
    path('close_quo-te_consultant_send_mail/<int:client_id>/<int:consultant_request_id>/', close_quote_consultant_mail_view, name="close_mail_consultant_quote_URL"),
    path('complete_quo-te_consultant_send_mail/<int:client_id>/<int:consultant_request_id>/', complete_quote_consultant_mail_view, name="complete_mail_consultant_quote_URL"),
    path('sendFile/<int:client_id>/<int:consultant_request_id>/', sendFile, name="send-file"),
    path('declined/<int:client_id>/<int:consultant_request_id>/', declineVIew, name="declineVIew_URL"),
    path('ratings/<int:client_id>/<int:consultant_request_id>/', ratingsView, name="ratingsView_URL"),
    path("see-details-consultations-fields", SeeDetails, name="SeeDetails"),
    
    # --------------------------------------------------------------------------------------
    # Pick Up Order Request URLS
    path('pickup-client-order-request-list/<int:client_id>/<int:pickup_order_id>/', viewPickUpRequest, name="viewPickUpRequest_URL"),
    
    # Accetp Pick Up Order
    
    path('pickup-client-order-request-accept/<int:client_id>/<int:pickup_order_id>/', viewPickUpRequestAccept, name="viewPickUpRequestAccept_URL"),
    
    # Reject Pick up Order
    path('pickup-client-order-request-reject/<int:client_id>/<int:pickup_order_id>/', viewPickUpRequestReject, name="viewPickUpRequestReject_URL"),
    
    # On Delivery
    path('pickup-client-order-request-delivery/<int:client_id>/<int:pickup_order_id>/', viewPickUpRequestOnDelivery, name="viewPickUpRequestOnDelivery_URL"),
    
    
    path('pickup-client-order-request-received/<int:client_id>/<int:pickup_order_id>/', viewPickUpRequestRecieved, name="viewPickUpRequestReceived_URL"),
    
    
    path('pickup-client-order-request-failed/<int:client_id>/<int:pickup_order_id>/', viewPickUpRequestOnFailed, name="viewPickUpRequestFailed_URL"),
    # --------------------------------------------------------------------------------------
]



if settings.DEBUG:
    urlpatterns+= static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    
