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

# Create your views here.
from .forms import EditProfileForm
from .models import *

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
