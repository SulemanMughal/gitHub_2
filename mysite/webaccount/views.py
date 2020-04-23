from django.shortcuts import render,redirect
# from django.contrib.auth.decorators import lo
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site


# Create your views here.
from .forms import EditProfileForm, ConsultantRequestUpdateForm, FeedbackForm
from .models import *


def printObjects(x):
    print("*****************************************")
    print("*****************************************")
    print(x)
    print("*****************************************")
    print("*****************************************")

@login_required
def profile_view(request):
    return render(request, 'webaccount/profile.html', {})

def index_view(request):
    # if request.user.is_authenticated and request.user.is_superuser:
    if request.user.is_authenticated:
        return redirect(reverse('profile_url'))
    else:
        if request.method != "POST":
            return render(request, 'webaccount/login.html', {})
        # elif request.method == "GET":
        else:
        # if authenticate
            try:
                user = authenticate(username=request.POST['username'], password = request.POST['password'])
            except:
                messages.error(request, "Incorrect username or password.")
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('profile_url'))
                else:
                    messages.error(request, "User account has been deactivate")
            else:
                if request.POST['username'] == '' and request.POST['password'] == '':
                    messages.error(request, "Both username and password are empty.")
                elif request.POST['username'] == '':
                    messages.error(request, "Username is empty.")
                elif request.POST['password'] == '':
                    messages.error(request, "Password is empty.")
                else:
                    messages.error(request, "Incorrect username or password.")
        return render(request, 'webaccount/login.html', {})

# @login_required
# def logout_view(request):
#     logout()

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "User has been logout successfully.")
    return redirect(reverse("index_url"))

# # Password Set View By The User...
# def password_set_user(request):
#     return render(request, 'webaccount/password_set_user.html', {})


@login_required()
def change_password(request):
    if request.method != 'POST':
        form = PasswordChangeForm(user=request.user)
    else:
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password has been updated.')
            if request.user.is_superuser:
                logout(request)
                return redirect(reverse('admin:login'))
            else:
                logout(request)
                return redirect(reverse('index_url'))
    return render(request, 'webaccount/change_password.html', {'form': form, 'section': "editProfile"})




@login_required()
def edit_profile(request):
    if request.method!='POST':
        form = EditProfileForm(instance = request.user)
    else:
        form = EditProfileForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            # return redirect('profile', username = request.user.username)
            # return HttpResponseRedirect(reverse('profile', args=[request.user.username]))
            return redirect(reverse('index_url'))
    return render(request, 'webaccount/edit_profile.html',{'form' : form})

@login_required()
@staff_member_required
def send_quote_view(request, num):
    try:
        client = Client_Personal_Info.objects.get(id = num)
        d = client.clientrequireddocuments_set.all()
        e = Required_Documents.objects.all()
        # print(d)
        # print("--------")
        # print(e)
        # print(client)
    except Client_Personal_Info.DoesNotExist:
        return redirect(reverse('admin:index'))
    context={
        'client': client,
        'title_site' : "Send Quote",
        'title' : "Client '" + str(client.Name) + "' Details",
        'documents': e,
        'd' : d
    }
    return render(request, "webaccount/send_quote_clinet.html",context)


@login_required()
@staff_member_required
def send_quote_mail_view(request, client_id):
    # print(request.method)
    # # print(request.POST)
    # A = []
    # # d = dict(request.POST)
    # # print(d)
    # # print(list(d.keys())[2:])
    # if request.POST:
    #     if len(list(dict(request.POST).keys())) > 2:
    #         A = list(dict(request.POST).keys())
    #     else:
    #         A = []
    A = list(dict(request.POST).keys())
    if "csrfmiddlewaretoken" in  A:
        A.pop(A.index("csrfmiddlewaretoken"))
    if "documents" in A:
        A.pop(A.index("documents"))
    try:
        client = Client_Personal_Info.objects.get(id =client_id)
        if client.status == "Pending" :
            mail_subject = "Resend Quote Email"
            message_title = "An email has been recieved from the Django Admin Group of Companies"
            message_subject = "The documents need to be re-submitted"
            if len(A) != 0:
                message = "{title}\n{subject}\n{list}\n".format(title = message_title, subject = message_subject, list=A)
            else:
                message = "A resend email has been recieved from the Django Admin Group of Companies. You account has been activated."
            messages.success(request, 'A resend email has been send to the client to inform him about his status regarding account')
        else:
            mail_subject = "Quote Email"
            message_title = "An email has been recieved from the Django Admin Group of Companies"
            message_subject = "The documents need to be submitted"
            if len(A) != 0:
                message = "{title}\n{subject}\n{list}\n".format(title = message_title, subject = message_subject, list=A)
            else:
                message = "An email has been recieved from the Django Admin Group of Companies.You account has been activated."
            messages.success(request, 'An email has been send to the client to inform him about his status regarding account')
        client.status = "Pending"
        client.save()
        to_email = str(client.Email)
    except:
        messages.error(request, 'Client Does Not Exist.')
        return redirect(reverse("admin:index"))
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    return redirect(reverse("send_quote_specific", args=[client_id]))


@login_required
@staff_member_required
def change_document_submitted_status_aaproved(request, client_id, document_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        document = ClientRequiredDocuments.objects.get(client = client, id =document_id)
        document.status = "Approved"
        document.save()
        messages.success("Status has been set to Approved.")
        return redirect(reverse("send_quote_specific", args=[client_id]))
    except:
        messages.error(request, 'Invalid Document.')
        return redirect(reverse("send_quote_specific", args=[client_id]))

@login_required
@staff_member_required
def change_document_submitted_status_rejected(request, client_id, document_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        document = ClientRequiredDocuments.objects.get(client = client, id =document_id)
        document.status = "Rejected"
        document.delete()
        messages.success("Status has been set to Rejected.")
        return redirect(reverse("send_quote_specific", args=[client_id]))
    except:
        messages.error(request, 'Invalid Document.')
        return redirect(reverse("send_quote_specific", args=[client_id]))

@login_required
@staff_member_required
def sendConsultantRequestQuote(request, client_id, consultant_request_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        consultant_request = ConsulatationRequest.objects.get(client= client, id=consultant_request_id)
        # return redirect(reverse("admin:webaccount_consulatationrequest_changelist"))
        template_name="webaccount/send_consultant_quote_clinet.html"
        context={
            'client': client,
            'title_site' : "Send Consultant Quote",
            'title' : "Client '" + str(client.Name) + "' Consultant",
            'consultant_request': consultant_request,
            'form' : ConsultantRequestUpdateForm(instance = consultant_request),
            'form_2' : FeedbackForm()
        }
        return render(request,
                    template_name,
                    context
                )
        
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_consulatationrequest_changelist"))
    
    
    
# Check the Current status of the consultation
# def consultationStatus(x):
#     try:
        
#     except:
#         return False
    
    
# Save and Send
@login_required
@staff_member_required
def save_send_quote_consultant_mail_view(request, client_id, consultant_request_id):
    if request.method != "POST":
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            if consultant_request.status == "Pending":
                if consultant_request.client_paid_all_amount == True:
                    messages.success(request, "Client already payed for this consultation quote, please confirm it.")
                    return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
                else:
                    domain = current_site = get_current_site(request)
                    url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
                    build_link = str(request.scheme) + str("://") + str(domain) + str(url)
                    # -------------
                    mail_subject = "Consultation Quote Email [{status}]".format(status = consultant_request.status)
                    message_title = "An email has been recieved from the Django Admin Group of Companies\n\n"
                    message_subject = "Consultant Quote"
                    message = message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
                    message += build_link
                    messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request.')
                    to_email = str(client.Email)
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()
                    return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
        except Exception as e:
            # print(e)
            messages.success(request, str(e))
            return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            form = ConsultantRequestUpdateForm(request.POST, instance=consultant_request)
            try:
                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.update_timestamp =  timezone.now()
                    obj.save()
                else:
                    messages.success(request, (form.errors))
                    return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))                    
            except Exception as e:
                messages.success(request, str(e))
                return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
            # ----------------------
            if obj.status == "New" or obj.status == "Rejected":
                domain = current_site = get_current_site(request)
                url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
                build_link = str(request.scheme) + str("://") + str(domain) + str(url)
                # -------------
                mail_subject = "Consultation Quote Email [{status}]".format(status = obj.status)
                message_title = "An email has been recieved from the Django Admin Group of Companies\n\n"
                message_subject = "Consultant Quote"
                message = message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
                message += build_link
                messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request.')
                to_email = str(client.Email)
            if obj.status == "New" or obj.status == "Rejected":
                obj.status = "Pending"
                obj.save()
        except:
            messages.error(request, 'Client Does Not Exist.')
            return redirect(reverse("admin:index"))
        if obj.status == "New" or obj.status == "Rejected":
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))




# Rejected
@login_required
@staff_member_required
def reject_quote_consultant_mail_view(request, client_id, consultant_request_id):
    if request.method == "POST":
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id, consultant_request_id]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            consultant_request.status = "Rejected"
            consultant_request.save()
            domain = current_site = get_current_site(request)
            url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
            build_link = str(request.scheme) + str("://") + str(domain) + str(url)
            # -------------
            mail_subject = "Consultation Quote Email [Rejected]"
            message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
            message_subject = "Consultant Quote"
            message =  message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
            message += build_link
            messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request.')
            to_email = str(client.Email)
        except:
            messages.error(request, 'Client Does Not Exist.')
            return redirect(reverse("admin:index"))
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
    
@staff_member_required
@login_required
def confirm_quote_consultant_mail_view(request, client_id ,consultant_request_id):
    if request.method == "POST":
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id, consultant_request_id]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            if consultant_request.client_paid_all_amount:
                consultant_request.status = "Confirmed"
                consultant_request.save()
                domain = current_site = get_current_site(request)
                url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
                build_link = str(request.scheme) + str("://") + str(domain) + str(url)
                # -------------
                mail_subject = "Consultation Quote Email [Confirmed]"
                message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
                message_subject = "Consultant Quote"
                message =  message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
                message += build_link
                messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request.')
                to_email = str(client.Email)
            else:
                messages.success(request, "You can't confirm the consultation request because the client didn't pay yet.")
                return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
        except:
            messages.error(request, 'Client Does Not Exist.')
            return redirect(reverse("admin:index"))
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))


# CLose
@login_required
@staff_member_required
def  close_quote_consultant_mail_view(request, client_id , consultant_request_id):
    if request.method == "POST":
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id, consultant_request_id]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            consultant_request.status = "Close"
            consultant_request.save()
            domain = current_site = get_current_site(request)
            url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
            build_link = str(request.scheme) + str("://") + str(domain) + str(url)
            # -------------
            mail_subject = "Consultation Quote Email [Close]"
            message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
            message_subject = "Consultant Quote"
            message =  message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
            message += build_link
            messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request.')
            to_email = str(client.Email)
        except:
            messages.error(request, 'Client Does Not Exist.')
            return redirect(reverse("admin:index"))
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
    


# Complete
@login_required
@staff_member_required
def  complete_quote_consultant_mail_view(request, client_id , consultant_request_id):
    if request.method == "POST":
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id, consultant_request_id]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            consultant_request.status = "Completed"
            consultant_request.save()
            domain = current_site = get_current_site(request)
            url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
            build_link = str(request.scheme) + str("://") + str(domain) + str(url)
            # -------------
            mail_subject = "Consultation Quote Email [Close]"
            message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
            message_subject = "Consultant Quote"
            message =  message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
            message += build_link
            messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request.')
            to_email = str(client.Email)
        except:
            messages.error(request, 'Client Does Not Exist.')
            return redirect(reverse("admin:index"))
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
    
@login_required
@staff_member_required
def sendFile(request,client_id ,consultant_request_id):
    if request.method == "GET":
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            form = FeedbackForm(request.POST, request.FILES, instance=consultant_request)
            if form.is_valid():
                form.save()
                messages.success(request, "File has been send successffully")
                return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
            else:
                messages.success(request, str(form.errors))
                return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
        except Exception as e:
            print(e)
            messages.success(request, "There is an error while uploading documents")
            return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))