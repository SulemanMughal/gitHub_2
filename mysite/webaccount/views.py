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

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "User has been logout successfully.")
    return redirect(reverse("index_url"))


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
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_consulatationrequest_changelist"))
    
# Save and Send
@login_required
@staff_member_required
def save_send_quote_consultant_mail_view(request, client_id, consultant_request_id):
    try:
        client = Client_Personal_Info.objects.get(id =client_id)
        consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
        if consultant_request.clientPaidAllAmount == True:
            messages.success(request, "Client already payed for this consultation quote, please confirm it.")
            return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
        form = ConsultantRequestUpdateForm(request.POST, instance=consultant_request)
        try:
            if form.is_valid():
                data_1, data_2  = form.cleaned_data['price'], form.cleaned_data['clientPaidAllAmount']
                obj = form.save(commit=False)
                obj.update_timestamp =  timezone.now()
                obj.save()
            else:
                messages.success(request, (form.errors))
                return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))                    
        except Exception as e:
            messages.success(request, str(e))
            return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
        domain = current_site = get_current_site(request)
        url =  reverse("sendConsultantRequestQuote_URL", args=[client.id, consultant_request.id])
        build_link = str(request.scheme) + str("://") + str(domain) + str(url)
        mail_subject = "Consultation Quote Email [{status}]".format(status = obj.status)
        message_title = "An email has been recieved from the Django Admin Group of Companies\n\n"
        message_subject = "Consultant Quote"
        message = message_title + "Please visit the following link to get updates about your consultation request\n\n\n"
        message += build_link
        to_email = str(client.Email)
        email = EmailMessage(mail_subject, message, to=[to_email])
        if obj.status != "New":
            messages.success(request, 'A resend email has been send to the client to inform him about his status regarding consultant request.')
        else:
            messages.success(request, 'An email has been send to the client to inform him about his status regarding consultant request and client consultation quote status has been changed from "New" to "Pending."')
        if obj.status == "New":
            obj.status = "Pending"
            obj.save()
        email.send()
        return redirect(reverse("sendConsultantRequestQuote_URL", args=[client_id,consultant_request_id ]))
    except Exception as e:
        print(e)
        messages.error(request, 'Client Does Not Exist.')
        return redirect(reverse("admin:index"))




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
            if consultant_request.clientPaidAllAmount:
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
        
        
@login_required
@staff_member_required
def declineVIew(request, client_id, consultant_request_id):
    A = [
        'Price is High',
        "I don't need the consultation",
        'The time is not suitable for me',
        'Other',
    ]
    if request.method != "POST":
        messages.success(request, 'Invalid Request.')
        return redirect(reverse(
            "sendConsultantRequestQuote_URL", args=[
            client_id,
            consultant_request_id
        ]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            consultant_request.status = "Declined"
            if int(request.POST['customRadio']) != 4:
                consultant_request.decline_explanation = A[int(request.POST['customRadio'])]
            else:
                consultant_request.decline_explanation = request.POST['customRadio1']
            consultant_request.save()
            print(request.POST)
            messages.success(request, 'Consultation has been declined')
            return redirect(reverse(
                "sendConsultantRequestQuote_URL", args=[
                client_id,
                consultant_request_id
            ]))
        except Exception as e:
            messages.success(request, 'Invalid Request')
            return redirect(reverse(
                "sendConsultantRequestQuote_URL", args=[
            client_id,
            consultant_request_id
            ]))
            
@login_required
@staff_member_required
def ratingsView(request, client_id, consultant_request_id):
    if request.method != "POST":
        messages.success(request, 'Invalid Request.')
        return redirect(reverse(
            "sendConsultantRequestQuote_URL", args=[
            client_id,
            consultant_request_id
        ]))
    else:
        try:
            client = Client_Personal_Info.objects.get(id =client_id)
            consultant_request = ConsulatationRequest.objects.get(client=client, id=consultant_request_id)
            consultant_request.rating = int(request.POST['whatever1'])
            consultant_request.save()
            messages.success(request, 'Ratings has been submitted.')
            return redirect(reverse(
                "sendConsultantRequestQuote_URL", args=[
                client_id,
                consultant_request_id
            ]))
        except Exception as e:
            messages.success(request, 'Invalid Request')
            return redirect(reverse(
                "sendConsultantRequestQuote_URL", args=[
            client_id,
            consultant_request_id
            ]))
 
#  --------------------------------------------------------------
#  Pickup Order requests

@login_required
@staff_member_required
def viewPickUpRequest(request, client_id, pickup_order_id):

    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        order_Request = PickUpRequestOrders.objects.get(id=pickup_order_id)
        template_name = "webaccount/pickup_order_requests_list.html"
        context = {
            'client' : client,
            'order_Request' : order_Request,
            'title_site' : "Pick Up Order Details",
            'title' : "Client '" + str(client.Name) + "'s Pickup Order Details"
        }
        return render(request, template_name, context)
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_pickuprequestorders_changelist"))
    

@login_required
@staff_member_required
def viewPickUpRequestAccept(request, client_id, pickup_order_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        order_Request = PickUpRequestOrders.objects.get(id=pickup_order_id)
        if order_Request.shippingMethod is None:
            messages.success(request,"Shipping method field is required")
            return redirect(reverse("viewPickUpRequest_URL", args= [
                client_id ,
                pickup_order_id
            ]))
        else:
            order_Request.status="ACCEPT"
            order_Request.updated_timestamp = timezone.now()
            order_Request.save()
            domain = current_site = get_current_site(request)
            url =  reverse("viewPickUpRequest_URL", args=[client.id, order_Request.id])
            build_link = str(request.scheme) + str("://") + str(domain) + str(url)
            # -------------
            mail_subject = "Pickup Order Request Email [Accepted]"
            message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
            message_subject = "Pickup Order Request"
            message =  message_title + "Please visit the following link to get updates about your Pickup Order Request\n\n\n"
            message += build_link
            messages.success(request, 'An email has been send to the client to inform him about his status regarding Pickup Order Request.')
            to_email = str(client.Email)
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return redirect(reverse("viewPickUpRequest_URL", args= [
                client_id ,
                pickup_order_id
            ]))
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_pickuprequestorders_changelist"))
    
    

@login_required
@staff_member_required
def viewPickUpRequestReject(request, client_id, pickup_order_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        order_Request = PickUpRequestOrders.objects.get(id=pickup_order_id)
        order_Request.status="REJECT"
        order_Request.updated_timestamp = timezone.now()
        order_Request.save()
        domain = current_site = get_current_site(request)
        url =  reverse("viewPickUpRequest_URL", args=[client.id, order_Request.id])
        build_link = str(request.scheme) + str("://") + str(domain) + str(url)
        # -------------
        mail_subject = "Pickup Order Request Email [Rejected]"
        message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
        message_subject = "Pickup Order Request"
        message =  message_title + "Please visit the following link to get updates about your Pickup Order Request\n\n\n"
        message += build_link
        messages.success(request, 'An email has been send to the client to inform him about his status regarding Pickup Order Request.')
        to_email = str(client.Email)
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("viewPickUpRequest_URL", args= [
            client_id ,
            pickup_order_id
        ]))
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_pickuprequestorders_changelist"))
    
    

@login_required
@staff_member_required
def viewPickUpRequestOnDelivery(request, client_id, pickup_order_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        order_Request = PickUpRequestOrders.objects.get(id=pickup_order_id)
        order_Request.status="ON DELIVERY"
        order_Request.updated_timestamp = timezone.now()
        order_Request.save()
        domain = current_site = get_current_site(request)
        url =  reverse("viewPickUpRequest_URL", args=[client.id, order_Request.id])
        build_link = str(request.scheme) + str("://") + str(domain) + str(url)
        # -------------
        mail_subject = "Pickup Order Request Email [On Delivery]"
        message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
        message_subject = "Pickup Order Request"
        message =  message_title + "Please visit the following link to get updates about your Pickup Order Request\n\n\n"
        message += build_link
        messages.success(request, 'An email has been send to the client to inform him about his status regarding Pickup Order Request.')
        to_email = str(client.Email)
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("viewPickUpRequest_URL", args= [
            client_id ,
            pickup_order_id
        ]))
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_pickuprequestorders_changelist"))
    
    

@login_required
@staff_member_required
def viewPickUpRequestRecieved(request, client_id, pickup_order_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        order_Request = PickUpRequestOrders.objects.get(id=pickup_order_id)
        order_Request.status="RECEIVED"
        order_Request.updated_timestamp = timezone.now()
        order_Request.save()
        domain = current_site = get_current_site(request)
        url =  reverse("viewPickUpRequest_URL", args=[client.id, order_Request.id])
        build_link = str(request.scheme) + str("://") + str(domain) + str(url)
        # -------------
        mail_subject = "Pickup Order Request Email [Received]"
        message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
        message_subject = "Pickup Order Request"
        message =  message_title + "Please visit the following link to get updates about your Pickup Order Request\n\n\n"
        message += build_link
        messages.success(request, 'An email has been send to the client to inform him about his status regarding Pickup Order Request.')
        to_email = str(client.Email)
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("viewPickUpRequest_URL", args= [
            client_id ,
            pickup_order_id
        ]))
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_pickuprequestorders_changelist"))
    
    
    

@login_required
@staff_member_required
def viewPickUpRequestOnFailed(request, client_id, pickup_order_id):
    try:
        client = Client_Personal_Info.objects.get(id = client_id)
        order_Request = PickUpRequestOrders.objects.get(id=pickup_order_id)
        order_Request.status="FAILED"
        order_Request.updated_timestamp = timezone.now()
        order_Request.save()
        domain = current_site = get_current_site(request)
        url =  reverse("viewPickUpRequest_URL", args=[client.id, order_Request.id])
        build_link = str(request.scheme) + str("://") + str(domain) + str(url)
        # -------------
        mail_subject = "Pickup Order Request Email [Failed to Pickup]"
        message_title = "An email has been recieved from the Django Admin Group of Companies\n\n\n"
        message_subject = "Pickup Order Request"
        message =  message_title + "Please visit the following link to get updates about your Pickup Order Request\n\n\n"
        message += build_link
        messages.success(request, 'An email has been send to the client to inform him about his status regarding Pickup Order Request.')
        to_email = str(client.Email)
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return redirect(reverse("viewPickUpRequest_URL", args= [
            client_id ,
            pickup_order_id
        ]))
    except Exception as e:
        print(e)
        messages.success(request,"Invlid Request")
        return redirect(reverse("admin:webaccount_pickuprequestorders_changelist"))
    