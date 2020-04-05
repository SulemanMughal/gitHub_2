from django.apps import AppConfig


class WebaccountConfig(AppConfig):
    name = 'webaccount'


from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = 'webaccount.admin.MyAdminSite'