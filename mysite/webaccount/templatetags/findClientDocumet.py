# findClientDocumet

from django import template
from webaccount.models import *
# from django.contrib.auth.models import User

register = template.Library()


def findClientDocumet(user_value):
    try:
        # profile = profilePicture.objects.get(user = user_value)
        d = ClientRequiredDocuments.objects.filter(document__id = user_value)
        # print(d[0].id)
        if len(d) != 0:
            return d
        else:
            return False
    except:
        return False

register.filter(findClientDocumet)