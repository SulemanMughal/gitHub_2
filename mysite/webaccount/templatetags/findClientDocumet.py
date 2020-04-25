# findClientDocumet

from django import template
from webaccount.models import *
# from django.contrib.auth.models import User



import inspect



register = template.Library()


def findClientDocumet(user_value, client_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        # profile = profilePicture.objects.get(user = user_value)
        d = ClientRequiredDocuments.objects.filter(document__id = user_value, client = client)
        # frame = inspect.currentframe()
        # print("***************************************************")
        # print("File Name : ",frame.f_code.co_filename,"Current Line Number : ", frame.f_lineno, d, sep="\n")
        # # print(d)
        # print("*********************************************")
        # print(d[0].id)
        if len(d) != 0:
            return d
        else:
            return False
    except:
        return False

register.filter(findClientDocumet)