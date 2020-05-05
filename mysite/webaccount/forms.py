import unicodedata

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model,
                                 password_validation)
from django.contrib.auth.hashers import (UNUSABLE_PASSWORD_PREFIX,
                                         identify_hasher)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.forms import BaseModelFormSet
from django.shortcuts import redirect, render
from django.template import loader
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import capfirst
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from accounts.models import *

from .models import *

# UserModel = get_user_model()



ADMIN_RIGHTS=[
    ("True", 'Admin'),
    ("False",'Relational Manager'),
    ("Consultant", "Consultant")
]

ACCOUNT_STATUS = [
    (True, 'Active'),
    (False, 'Disabled')
]

# RELATIONAL_MANAGER_CHOICES = [(str(r), str(r)) for r in User.objects.filter(is_superuser = False, is_active  = True)]

class ReadOnlyPasswordHashWidget(forms.Widget):
    template_name = 'auth/widgets/read_only_password_hash.html'
    read_only = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        summary = []
        if not value or value.startswith(UNUSABLE_PASSWORD_PREFIX):
            summary.append({'label': gettext("No password set.")})
        else:
            try:
                hasher = identify_hasher(value)
            except ValueError:
                summary.append({'label': gettext("Invalid password format or unknown hashing algorithm.")})
            else:
                for key, value_ in hasher.safe_summary(value).items():
                    summary.append({'label': gettext(key), 'value': value_})
        context['summary'] = summary
        return context


class ReadOnlyPasswordHashField(forms.Field):
    widget = ReadOnlyPasswordHashWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        # Always return initial because the widget doesn't
        # render an input field.
        return initial

    def has_changed(self, initial, data):
        return False




class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super().to_python(value))


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    email = forms.CharField(
        label=_("Email"),
        # strip=False,
        widget=forms.EmailInput,
        # help_text=password_validation.password_validators_help_text_html(),
    )
    # password2 = forms.CharField(
    #     label=_("Password confirmation"),
    #     widget=forms.PasswordInput,
    #     strip=False,
    #     help_text=_("Enter the same password as before, for verification."),
    # )

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def _post_clean(self):
        try:
            # clean_data = self.cleaned_data
            # if clean_data.get("username") == '':
            #     raise forms.ValidationError("Error")
            super()._post_clean()
        except:
            return redirect("/auth/user/add/")
        # Validate the password after self.instance is updated with form data
        # by super().
        # if self.cleaned_data.get("passw")
        mail_subject = "Password Set Link"
        to_email = self.cleaned_data.get("email")
        message = self.cleaned_data.get("username")
        # print("***********************")
        # print(self.cleaned_data.get("username"))
        # print("***********************")

        if self.cleaned_data.get("username") is None and self.cleaned_data.get("email") is None:
            # raise forms.ValidationError("saldkaslkdnaslkdnalksdn")
            self.add_error("username", "Username is empty\n")
            # self.username.error_messages("hkhbhjbjhbjhbjhbjhbjh")
            self.add_error("email", "Email is empty  ")
            return redirect("/auth/user/add/")


        if self.cleaned_data.get("username") is None:
            # raise forms.ValidationError("saldkaslkdnaslkdnalksdn")
            self.add_error("username", "Username is empty")
            return redirect("/auth/user/add/")

        if self.cleaned_data.get("email") is None:
            # raise forms.ValidationError("saldkaslkdnaslkdnalksdn")
            self.add_error("email", "Email is empty")
            return redirect("/auth/user/add/")
        

        
        # clean_data = self.cleaned_data
        # if clean_data.get("username") == '':
        #     raise forms.ValidationError("Error")
        user=super().save()
        # print("*********" , user.username, "**********")
        # print("****************", user.pk,  "******************")
        # print(self.request)
        # print(self)
        # print( User.objects.get( username = self._meta.model.USERNAME_FIELD))
        uid= urlsafe_base64_encode(force_bytes(user.pk))
        # user: user,
        token= default_token_generator.make_token(user)
        # print("**************", uid, token, "**************")
        if len(settings.ALLOWED_HOSTS) != 0:
            if len(settings.PORT) !=0:
                domain = str(settings.ALLOWED_HOSTS[0]) + ":" + str(settings.PORT[0])
            else:
                domain = str(settings.ALLOWED_HOSTS[0]) + ":" + str("8000")
        else:
            domain = "127.0.0.1:8000"
        if len(settings.PROTOCOL) != 0:
            if len(settings.ALLOWED_HOSTS) != 0:
                protocol = settings.PROTOCOL
            else:
                protocol = "http"
        else:
            protocol = "http"
        message = render_to_string('webaccount/password_set_user.html', {
            'user':user, 
            'domain':domain,
            'uid': uid,
            'token': token,
            'protocol' : protocol
        })
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        password = self.cleaned_data.get('password2')

        # if self.cleaned_data.get("username") == "":
        #     forms.ValidationError("sdkfsdknfsdnf")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        # if self.clean_data.get("username"):
        #     raise forms.ValidationError("aslldknaslkdnaslkd")

        user = super().save(commit=False)
        # global RELATIONAL_MANAGER_CHOICES
        # RELATIONAL_MANAGER_CHOICES += [str(user), str(user)]
        # print(self.cleaned_data)
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        # if self.cleaned_data.get("username") == "":
        #     forms.ValidationError("sdkfsdknfsdnf")
        
        if commit:
            # mail_subject = "Password Set Link"
            # to_email = self.user.email
            # message = "Tetsirt"
            # # print(self.request)
            # # print(self)
            # # print( User.objects.get( username = self._meta.model.USERNAME_FIELD))
            # email = EmailMessage(mail_subject, message, to=[to_email])
            # email.send()
            try:
                user.save()
            except:
                return redirect("/auth/user/add/")
        return user



class UserChangeForm(forms.ModelForm):
    is_superuser = forms.ChoiceField(choices = ADMIN_RIGHTS, label="Role")
    is_active = forms.ChoiceField(choices = ACCOUNT_STATUS, label="Satus")

    class Meta:
        model = User
        # fields = '__all__'
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff', 
            # 'is_superuser', 
            # 'is_active'
        ]
        field_classes = {'username': UsernameField}

    def __init__(self,  *args, **kwargs):
        # self.request=request
        # print(self.request)
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')

        # if password:
        #     password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')

    
#User Can Edit his profile using this Form..........................
class EditProfileForm(UserChangeForm):
    password = forms.CharField(label='', widget = forms.TextInput(attrs = {'type' : 'hidden'}))
    class Meta:
        model = User
        fields = ['username',
                  'first_name',
                  'last_name',
                  'password',
                  'email'
                  ]


class Required_DocumentsForm(forms.ModelForm):
    # Name= forms.CharField(label="Name", widget = forms.TextInput())
    # file_type = forms.CharField(label="File Type", widget=forms.Select( choices = types))

    class Meta:
        model = Required_Documents
        fields = [
            'Name',
            'file_type'
        ]

    def clean(self):
        data = super().clean()
        # if self.cleaned_data.get("uploadFile") is None:
        #     self.instance.status = "Rejected"
        obj = Required_Documents.objects.filter(Name = self.cleaned_data.get("Name"), file_type= self.cleaned_data.get("file_type"))
        if len(obj) != 0:
            if not obj[0].id == self.instance.id:
                A = ""+self.cleaned_data.get("Name") + "." + self.cleaned_data.get("file_type") + " already exists."
                raise forms.ValidationError(A)
        return self.cleaned_data


class Client_Personal_Info_Form(forms.ModelForm):
    Services = forms.MultipleChoiceField(
            choices= service, 
            initial =  [ str(i[0]) for i in service ])
    Name    =   forms.CharField(
            max_length  =   300, 
            min_length  =   0, 
            label       =   "Name", 
            widget      =   forms.widgets.TextInput(
                        attrs={
                            'autocomplete' : "off"
                        })
            # error_messages  =   {
            #     'required' : "Please enter your name."
            # }
        )
    Email   =   forms.EmailField(
        label       =   "Email",
        max_length  =   300,
        min_length  =   0,
        widget      =   forms.EmailInput(
            attrs={
                'autocomplete' : "off"
            })   
    )
    Phone_Number    =   forms.CharField(
        label       =   "Phone Number",
        max_length  =   10,
        min_length  =   0,
        widget      =   forms.TextInput(
            attrs={
                'autocomplete' : "off"
            }
        )
    )
    CR              =   forms.CharField(
        label       =   "CR",
        max_length  =   10,
        min_length  =   0,
        widget      =   forms.TextInput(
            attrs   =   {
                'autocomplete'  :   "off"
            }
        )
    )
    company_name    =   forms.CharField(
        label       =   "Company Name",
        max_length  =   300,
        min_length  =   0,
        widget      =   forms.TextInput(
            attrs   =   {
                'autocomplete'  :   "off"
            }
        )
    )
    location    =   forms.CharField(
        label       =   "Location",
        max_length  =   300,
        min_length  =   0,
        widget      =   forms.TextInput(
            attrs   =   {
                'autocomplete'  :   "off"
            }
        )
    )
    contact_number    =   forms.CharField(
        label       =   "Contact Number",
        max_length  =   10,
        min_length  =   0,
        widget      =   forms.TextInput(
            attrs   =   {
                'autocomplete'  :   "off"
            }
        )
    )
    Number_of_branches = forms.IntegerField(
        min_value = 0,
        max_value = 100000,
        label = "Number of branches",
        widget = forms.NumberInput(
            attrs={
                'autocomplete' : "off"
            }
        )
    )
    Number_of_employees = forms.IntegerField(
        min_value = 0,
        max_value = 100000,
        label = "Number of employees",
        widget = forms.NumberInput(
            attrs={
                'autocomplete' : "off"
            }
        )
    )
    # sector = forms.ChoiceField(
    #         label = "Sector", 
    #         choices = [  ( i, (str(i) ) ) for i in Sector.objects.all()   ]   ,
    #         required = True,
    #         widget = forms.Select(choices = [   (i, (str(i) ) ) for i in Sector.objects.all()   ]
    #         )
    #     )
    class Meta:
        model = Client_Personal_Info
        fields = [
                # "Name",
                # "Email",
                # "Phone_Number",
                # "company_name",
                # "CR",
                # "location",
                # "contact_number",
                "sector",
                # "Number_of_branches",
                # "Number_of_employees",
                "QR_code",
                # "Services",
                "Number_of_subaccounts",
                "package_price",
                "paymenStatus",
                "status",
                # "last_update",
                "managerRelational"
        ]

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['managerRelational'].queryset = User.objects.filter(is_superuser = False, is_active = True)
        self.fields['sector'].queryset = Sector.objects.all()
        if self.instance.id is not None:
            if len(self.initial['Services']) != 0:
                self.initial['Services'] = [B[0] for B in [(((i.split("[")[-1]).split("]")[0]).split("'")[1]).split("'") for i in self.instance.Services.split(",")]]
            else:
                self.initial['Services'] = ''
        elif self.instance.id is None:
            self.initial['Services'] = [ str(i[0]) for i in service ]

    # def clean(self):
    #     data = self.cleaned_data.get("Name", None)
    #     if data is not None:
    #         if len(data) == 0:
    #             raise ValidationError("Name field is empty.")
    #         else:
    #             return self.cleaned_data
    #     else:
    #         raise ValidationError("Name field is empty.P")

    def clean_CR(self):
        data = self.cleaned_data.get("CR", "None")
        # print(self.__dict__)
        # return data
        if self.instance.id is None:
            try:
                obj = Client_Personal_Info.objects.get(CR = data)
                raise ValidationError("CR Field already exists.")
            except:
                return data
        else:
            try:
                obj = Client_Personal_Info.objects.get(CR = data)
                if obj.id != self.instance.id:
                    raise ValidationError("CR Field already exists.")
                else:
                    return data
            except:
                return data

class RelationalManagerForm(forms.ModelForm):
    class Meta:
        model = relationManager
        fields = [
            'manager'
        ]


    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(is_superuser = False, is_active = True)
   

class consultantManagerForm(forms.ModelForm):
    class Meta:
        model = consultantManager
        fields = [
            'manager'
        ]


    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(is_superuser = "Consultant", is_active = True)
   


# CLient Documents Inline Forms

class BaseDocumentFormSet(forms.ModelForm):
    
    # Initialize Method
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

# -------------------------------------------------------------------------------------------
# CONSULTATION MODELS FORM HANDLERS



# Consultation Add New Entry Form
class ConsultantRequestAddForm(forms.ModelForm):
    class Meta:
        model = ConsulatationRequest
        fields = [
            'client',
            'explanation',
            'created_timestamp',
            'consultant',
            'clientPaidAllAmount',
        ]
        
       
from .models import CONSULTATION_CHOICES

# Consultant Request Form (STATUS == New)
class ConsultantRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = ConsulatationRequest
        fields = [
            'price',
            'clientPaidAllAmount',
            'status',
            'consultantManager'
        ]
        
        widgets= {
            'clientPaidAllAmount' : forms.Select(choices = (
                (False, "Pending"), 
                (True, "Completed")
                ) 
            ),
        }
        
        labels = {
            'consultantManager':"Consultant Manager"
        }

        
        # Initialize Method
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['consultantManager'].queryset = User.objects.filter(is_superuser = "Consultant", is_active = True)
        
    
    
    def clean_price(self):
        data = self.cleaned_data.get("price", None)
        if data is None:
            # print(self.cleaned_data)
            raise forms.ValidationError("Consultation Price is required.")
        elif float(data) < 0:
            raise forms.ValidationError("Consultation Price is should be greater than 0.")
        
        return float(data)
    
    def clean_consultantManager(self):
        c = self.cleaned_data.get("consultantManager")
        if c is None:
            raise forms.ValidationError("Assign Consultation")
        return c
        

    def clean_status(self):
        paid = self.cleaned_data.get("clientPaidAllAmount")
        s = self.cleaned_data.get("status")
        if s == "Completed" and paid == False:
            raise forms.ValidationError("The quote status cannot be completed until the payment status is completed")
        return s    
    

# CONSULTATION FEDBACK FORM
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = ConsulatationRequest
        fields = [
            'feedbackFile'
        ]
    
    def clean_feedbackFile(self):
        file = self.cleaned_data.get("feedbackFile")
        if self.__dict__['instance'].__dict__['status'] != "Completed":
            raise forms.ValidationError("Consultation should be completed before giving feedback document.")
        
        if file is None:
            raise forms.ValidationError("Feedback File should be uploaded first")
        
        elif file is not None:
            # print(file.__dict__)
            if file.__dict__['content_type'] != "application/pdf" :
                raise forms.ValidationError("Uploaded File should be pdf")
        return file
    
# -------------------------------------------------------------------------------------------


class ConsultantModelForm(forms.ModelForm):
    class Meta:
        model = ConsultantModel
        fields  = "__all__"
        
        widgets={
            'parentField': forms.Select(choices=([(str(i), str(i)) for i in ConsultantModel.objects.all()] + [(None, None)]))
        }


    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.fields['parentField'].queryset =[(str(i), str(i)) for i in ConsultantModel.objects.all()] + [(None, None)]
 