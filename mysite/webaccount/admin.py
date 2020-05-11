# from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import  Group

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
)
from django.core.paginator import InvalidPage
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import logout
from django.shortcuts import render,redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin import helpers, widgets
from django.contrib.admin.utils import (
    NestedObjects, construct_change_message, flatten_fieldsets,
    get_deleted_objects, lookup_needs_distinct, model_format_dict,
    model_ngettext, quote, unquote,
)
from .forms import *
from django.utils.translation import gettext as _, ngettext
from django.contrib.admin.views.main import ChangeList, SEARCH_VAR, IGNORED_PARAMS
from django.contrib.admin.exceptions import (
    DisallowedModelAdminLookup, DisallowedModelAdminToField,
)
from django.contrib.admin import FieldListFilter
from django.contrib.admin.utils import (
    get_fields_from_path, lookup_needs_distinct, prepare_lookup_value, quote,
)
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.core.exceptions import (
    FieldDoesNotExist, ImproperlyConfigured, SuspiciousOperation,
)
from django.conf import settings
from .models import *
from accounts.models import *
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

class reportChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by, num):
        super().__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by)
        
        client = Client_Personal_Info.objects.get(id = num)
        self.root_queryset = clientReport.objects.filter(client=client)
        self.title = str(client.Name) + " Reports"
        self.search_fields = search_fields
        self.query = request.GET.get(SEARCH_VAR, '')
        self.queryset = self.get_queryset(request)
        self.get_results(request)

class invoiceChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by, num):
        super().__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by)
        
        client = Client_Personal_Info.objects.get(id = num)
        self.root_queryset = clientInvoice.objects.filter(client=client)
        self.title = str(client.Name) + " Invoices"
        self.search_fields = search_fields
        self.query = request.GET.get(SEARCH_VAR, '')
        self.queryset = self.get_queryset(request)
        self.get_results(request)

# Inline Models Admin...
class ClientRequiredDocumentInline(admin.TabularInline):
    model = ClientRequiredDocuments
    form = BaseDocumentFormSet
    # fk_name = "client"
    # fields = '__all__'
    # extra = 0
    max_num = Required_Documents.objects.all().count()
    min_num = 0
    # fields = (
    #             (
    #                 'client',
    #                 'document', 
    #                 'uploadFile', 
    #                 'status',
    #             ),
    #     )
    fieldsets = (
        ("Client Documents", {
            'fields': (('client', 'document', 'uploadFile','status'),)
        }),
    )

    can_delete = True

    def get_extra(self, request, obj=None, **kwargs):
        extra = self.max_num+1
        if obj:
            return extra - obj.clientrequireddocuments_set.count()
        return extra



class MyAdminSite(admin.AdminSite):
    site_header = 'Account Administration'
    site_title = "Accounting"
    index_title = "Admin Dashboard"
    AdminSite.logout_template = "admin/login.html"
    AdminSite.password_change_template = "admin/auth/user/change_password.html"
    AdminSite.add_form_template = 'admin/auth/user/add_form.html'

class UserAdmin(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', "email")}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','contactNumber')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', "email" ),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_display = [
            'username', 
            'getSuperuser', 
            'getActiveStatus'
    ]
    list_filter = ( 'is_superuser','is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ( '-is_superuser', '-is_active' ,'-is_staff' , 'username')
    # filter_horizontal = ('groups', 'user_permissions',)
    list_per_page = 10
    sortable_by = [
        '-is_superuser'
    ]

    def getSuperuser(self, obj):
        if obj.is_superuser == "True":
            return "Admin"
        elif obj.is_superuser == "False":
            return "Relational Manager"
        else:
            return "Consultant"

    def getActiveStatus(self, obj):
        if obj.is_active:
            return "Active"
        return "Disabled"

    getSuperuser.short_description = "Role"
    getActiveStatus.short_description = "Status"

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super().get_urls()

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith('password') and super().lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url='', extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                # logout(request)
                # return HttpResponseRedirect(
                #     reverse(
                #         '%s:%s_%s_change' % (
                #             self.admin_site.name,
                #             user._meta.app_label,
                #             user._meta.model_name,
                #         ),
                #         args=(user.pk,),
                #     )
                # )
                return redirect(reverse('admin:logout'))
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)

class Required_DocumentsAdmin(admin.ModelAdmin):
 
    fieldsets = (
        (None, {'fields': ('Name', "file_type",)}),
    )
    search_fields = [
        'Name',
        'file_type'
    ]
    list_display  = [
        # 'client',
        'Name',
        'file_type',
        # 'uploadFile'
        # 'fileUploadType',
        # 'status'
    ]

    list_filter = [
        # 'client__Name',
        'file_type',
        # 'status'
        
    ]

    search_fields =[
        'Name',
        # 'client__Name'
    ]

    ordering = [
        'Name'
    ]
    sortable_by = [
        'file_type'
    ]
    list_per_page = 10

    form = Required_DocumentsForm

    # def fileUploadType(self, obj):
    #     if obj.uploadFile:
    #         link = '<a href="{0}{1}">{2}</a>'.format(settings.MEDIA_URL, obj.uploadFile ,str(obj.Name) + "." + str(obj.file_type))
    #         return mark_safe(link)
    #     return "None"
    
    # fileUploadType.short_description = "Uploaded Document"
    # fileUploadType.empty_value_display = "empty"

class Client_Personal_InfoAdmin(admin.ModelAdmin):
    readonly_fields = [
        'last_update'
    ]
    form = Client_Personal_Info_Form
    inlines = [
        ClientRequiredDocumentInline,
    ]
    fieldsets = (
        ("Client Information", {
            'fields': ('Name', 'Email', 'Phone_Number')
        }),
        ("Company Information", {
            'fields': ('company_name','CR','location','contact_number','sector','Number_of_branches','Number_of_employees','QR_code')
        }),
        ("Subscription Information", {
            'fields': ('Services','Number_of_subaccounts','package_price','paymenStatus')
        }),
        ("Relationship Manager", {
            'fields': ('managerRelational',)
        }),
        ("Client Status" , {
            'fields': ('status','last_update')
        }),
        # ("Account Status" , {
        #     'fields': ('activeStatus',)
        # }),
        # ("Account Status" , {
        #     'fields': ('quoteStatus',),
        #     'description': "Whether quote has been sent to the client or not."
        # }),
        
    )
    
    
    list_display = [
        'clientID',
        'Name',
        'Email',
        'companyName',
        # 'Client_Company_Info__location',
        # 'Phone_Number'
        'companyLocation',
        'companySector',
        'status',
        'formatLastUpdate'
    ]

    search_fields = (
        'Name',
    )

    list_filter = [
        "status",
        # "activeStatus",
        # 'quoteStatus'
    ]

    list_display_links = [
        'Name'
    ]

    ordering = [
        'Name',
        # 'Email',
        # 'Phone_Number'
    ]
    # filter_horizontal = [
    #     'Name'
    # ]
    list_per_page = 10

    # save_as = True

    def companyName(self, obj):
        # url = reverse("admin:webaccount_client_company_info_change", args=[obj.company.id])
        # link = '<a href="%s">%s</a>' % (url, obj.company.company_name)
        # return mark_safe(link)
        return obj.company_name

    def companyLocation(self, obj):
        return obj.location
    
    def clientID(self, obj):
        url = reverse("send_quote_specific", args=[obj.id])
        link = '<a href="%s" title = "%s">%s</a>' % (url,"Send Quote", obj.id)
        return mark_safe(link)
        # return obj.pk

    def companySector(self, obj):
        return obj.sector

    
    def formatLastUpdate(self, obj):
        return obj.last_update.strftime("%Y-%m-%d %H:%M")

    companyName.short_description = "Company Name"
    companyLocation.short_description = "Location"
    clientID.short_description = "ID"
    companySector.short_description = "Sector"
    formatLastUpdate.short_description = "Last Update"

class SectorAdmin(admin.ModelAdmin):
    list_display = [
        'Name'
    ]
    search_fields = [
        'Name'
    ]
    ordering = [
        'Name'
    ]
    sortable_by = [

    ]
    list_per_page = 10

    list_filter = [
        # 'Name'
    ]

class clientInvoiceAdmin(admin.ModelAdmin):
    list_display=[
        'objID',
        'clientID',
        'clientInvoices',
        'fortmatSubmittingDate',
        'statusType',
        'formatLastUpdate'
    ]
    search_fields = [
        'client__Name'
    ]
    list_filter=[
        'statusType'
    ]
    list_display_links=[
        'objID'
    ]
    ordering=[
        # 'objID'
        'client'
    ]
    sortable_by= [

    ]
    list_per_page = 10

    def objID(self, obj):
        return obj.pk

    def clientID(self, obj):
        url = reverse("admin:webaccount_client_personal_info_change", args=[obj.client.id])
        link = '<a href="%s">%s</a>' % (url, obj.client.Name)
        return mark_safe(link)

    def fortmatSubmittingDate(self, obj):
        return str(obj.submittingDate)

    def formatLastUpdate(self, obj):
        # print(obj.lastUpdate)
        return obj.lastUpdate.strftime("%Y-%m-%d %H:%M")

        
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('client_invoices/<int:num>/', self.admin_site.admin_view(self.specific_client_invoice, cacheable=True), name="webaccount_client_invoice_url"),
        ]
        return my_urls + urls

    
    def clientInvoices(self, obj):
        url= reverse("admin:webaccount_client_invoice_url", args = [obj.client.pk])
        clinet_id_numer = "View Client # " + str(obj.client.pk) + " Invoices"
        link = '<a href="%s">%s</a>' % (url,clinet_id_numer )
        return mark_safe(link)

    formatLastUpdate.short_description = "Last Update"
    fortmatSubmittingDate.short_description = "Submitting Date"
    clientID.short_description = "Client"
    objID.short_description = "Invoice ID"
    clientInvoices.short_description = "Client Invoices"

    def get_changelist_view_invoice(self, request ,num):
        # Change "list_display"
        list_display = [
            'objID',
            'fortmatSubmittingDate',
            'statusType',
            'formatLastUpdate'
        ]
        list_filter=[
            'statusType'
        ]
        # list_display = self.list_display
        list_display_links = self.list_display_links
        if super().get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.sortable_by
        self.search_fields=[
            'id'
        ]
        obj= invoiceChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            # self.list_filter,
            list_filter,
            super().date_hierarchy,
            self.search_fields,
            super().get_list_select_related(request),
            self.list_per_page,
            super().list_max_show_all,
            super().list_editable,
            self,
            sortable_by,
            num
        )
        return obj

    # @csrf_protect_m
    # def specific_client_invoice(self, request, num, extra_context=None):
    #     return super().changelist_view(
    #         request,extra_context=extra_context,
    #     )

    @csrf_protect_m
    def specific_client_invoice(self, request,num, extra_context=None):
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not super().has_view_or_change_permission(request):
            raise PermissionDenied
        try:
            cl = self.get_changelist_view_invoice(request, num)
            # print(cl.change_look_filter)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET:
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
        actions = super().get_actions(request)
        # Actions with no confirmation
        if (actions and request.method == 'POST' and 'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = super().response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                super().message_user(request, msg, messages.WARNING)
                action_failed = True

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = super().response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True

        if action_failed:
            # Redirect back to the changelist page to avoid resubmitting the
            # form if the user refreshes the browser or uses the "No, take
            # me back" button on the action confirmation page.
            return HttpResponseRedirect(request.get_full_path())

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == 'POST' and cl.list_editable and '_save' in request.POST:
            if not super().has_change_permission(request):
                raise PermissionDenied
            FormSet = super().get_changelist_formset(request)
            modified_objects = super()._get_list_editable_queryset(request, FormSet.get_default_prefix())
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=modified_objects)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = super().save_form(request, form, change=True)
                        super().save_model(request, obj, form, change=True)
                        super().save_related(request, form, formsets=[], change=True)
                        change_msg = self.construct_change_message(request, form, None)
                        super().log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    msg = ngettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        changecount
                    ) % {
                        'count': changecount,
                        'name': model_ngettext(opts, changecount),
                    }
                    super().message_user(request, msg, messages.SUCCESS)
                return HttpResponseRedirect(request.get_full_path())
        # Handle GET -- construct a formset for display.
        elif cl.list_editable and super().has_change_permission(request):
            FormSet = super().get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)
        # Build the list of media to be used by the formset.
        if formset:
            media = super().media + formset.media
        else:
            media = super().media
        # Build the action form and populate it with available actions.
        if actions:
            action_form = super().action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None
        selection_note_all = ngettext(
            '%(total_count)s selected',
            'All %(total_count)s selected',
            cl.result_count
        )
        context = {
            **self.admin_site.each_context(request),
            'module_name': str(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': cl.title,
            'is_popup': cl.is_popup,
            'to_field': cl.to_field,
            'cl': cl,
            'media': media,
            'has_add_permission': super().has_add_permission(request),
            'opts': cl.opts,
            'action_form': action_form,
            'actions_on_top': super().actions_on_top,
            'actions_on_bottom': super().actions_on_bottom,
            'actions_selection_counter': super().actions_selection_counter,
            'preserved_filters': super().get_preserved_filters(request),
            **(extra_context or {}),
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, super().change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.model_name),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context)

class relationManagerAdmin(admin.ModelAdmin):
    list_display = [
        'RM'
    ]
    search_fields=[
        'manager__username'
    ]

    list_per_page = 10

    def RM(self, obj):
        return obj.manager

    form = RelationalManagerForm
    
    RM.short_description = "Relational Manager"

class clientReportAdmin(admin.ModelAdmin):
    list_display=[
        'objID',
        'clientID',
        'clientReports',
        'reportType',
        'formatFinalreportIssueDate'
    ]
    search_fields =[
        'client__Name'
    ]
    list_display_links = [
        'objID'
    ]
    ordering = [
        'client'
    ]
    sortable_by= [

    ]
    list_filter = [
        'reportType'
    ]
    list_per_page= 10

    def objID(self, obj):
        return obj.pk
    
    def clientID(self, obj):
        url = reverse("admin:webaccount_client_personal_info_change", args=[obj.client.id])
        link = '<a href="%s">%s</a>' % (url, obj.client.Name)
        return mark_safe(link)
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('client_reports/<int:num>/', self.admin_site.admin_view(self.my_view, cacheable=True), name="webaccount_client_reports_url"),
        ]
        return my_urls + urls

    def clientReports(self, obj):
        url= reverse("admin:webaccount_client_reports_url", args = [obj.client.pk])
        clinet_id_numer = "View Client # " + str(obj.client.pk) + " Reports"
        link = '<a href="%s">%s</a>' % (url,clinet_id_numer )
        return mark_safe(link)
    
    # Calculate report time period/duration
    def reportDurationTime(self, obj):
        return str(obj.dateYear) + "-" + str(obj.month_quarterType)

    # Format for Final Report Issue Date
    def formatFinalreportIssueDate(self, obj):
        return str(obj.finalReportIssueDate)
     
    objID.short_description = "Report ID"
    clientID.short_description = "Client"
    clientReports.short_description="View Client Reports"
    reportDurationTime.short_description = "Period"
    formatFinalreportIssueDate.short_description="Final Report Issue Date"

    def get_changelist_view_report(self, request ,num):
        # Change "list_display"
        list_display = [
            'objID',
            'reportType',
            'reportDurationTime',
            'formatFinalreportIssueDate'
        ]
        list_filter=[
            'reportType',
            'dateYear',
            'month_quarterType'
        ]
        # list_display = self.list_display
        list_display_links = self.list_display_links
        if super().get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.sortable_by
        self.search_fields=[
            'id'
        ]
        obj= reportChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            # self.list_filter,
            list_filter,
            super().date_hierarchy,
            self.search_fields,
            super().get_list_select_related(request),
            self.list_per_page,
            super().list_max_show_all,
            super().list_editable,
            self,
            sortable_by,
            num
        )
        return obj

    @csrf_protect_m
    def my_view(self, request,num, extra_context=None):
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not super().has_view_or_change_permission(request):
            raise PermissionDenied
        try:
            cl = self.get_changelist_view_report(request, num)
            # print(cl.change_look_filter)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET:
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
        actions = super().get_actions(request)
        # Actions with no confirmation
        if (actions and request.method == 'POST' and 'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = super().response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                super().message_user(request, msg, messages.WARNING)
                action_failed = True

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = super().response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True

        if action_failed:
            # Redirect back to the changelist page to avoid resubmitting the
            # form if the user refreshes the browser or uses the "No, take
            # me back" button on the action confirmation page.
            return HttpResponseRedirect(request.get_full_path())

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == 'POST' and cl.list_editable and '_save' in request.POST:
            if not super().has_change_permission(request):
                raise PermissionDenied
            FormSet = super().get_changelist_formset(request)
            modified_objects = super()._get_list_editable_queryset(request, FormSet.get_default_prefix())
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=modified_objects)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = super().save_form(request, form, change=True)
                        super().save_model(request, obj, form, change=True)
                        super().save_related(request, form, formsets=[], change=True)
                        change_msg = self.construct_change_message(request, form, None)
                        super().log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    msg = ngettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        changecount
                    ) % {
                        'count': changecount,
                        'name': model_ngettext(opts, changecount),
                    }
                    super().message_user(request, msg, messages.SUCCESS)
                return HttpResponseRedirect(request.get_full_path())
        # Handle GET -- construct a formset for display.
        elif cl.list_editable and super().has_change_permission(request):
            FormSet = super().get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)
        # Build the list of media to be used by the formset.
        if formset:
            media = super().media + formset.media
        else:
            media = super().media
        # Build the action form and populate it with available actions.
        if actions:
            action_form = super().action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None
        selection_note_all = ngettext(
            '%(total_count)s selected',
            'All %(total_count)s selected',
            cl.result_count
        )
        context = {
            **self.admin_site.each_context(request),
            'module_name': str(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': cl.title,
            'is_popup': cl.is_popup,
            'to_field': cl.to_field,
            'cl': cl,
            'media': media,
            'has_add_permission': super().has_add_permission(request),
            'opts': cl.opts,
            'action_form': action_form,
            'actions_on_top': super().actions_on_top,
            'actions_on_bottom': super().actions_on_bottom,
            'actions_selection_counter': super().actions_selection_counter,
            'preserved_filters': super().get_preserved_filters(request),
            **(extra_context or {}),
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, super().change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.model_name),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context)

# # Consultation Admin
# class ConsulatationRequestAdmin(admin.ModelAdmin):
#     list_display=[
#         'client',
#         'explanation',
#     ]
    
#     search_fields = [
#         'client__Name',
#         'explanation'
#     ]


# Consultation Requests
class ConsulatationRequestAdmin(admin.ModelAdmin):
    change_form_template = "consulation_change_form.html"
    form=ConsultantRequestAddForm
    # prepopulated_fields  = {"consultant": ("parentField",)}
    autocomplete_fields = [
        
        "consultant"
        
    ]
    # readonly_fields =[
    #     'status'
    # ]
    fieldsets = (
        ("Client Consultation Request Information", {
            'fields': ('client' ,'consultant','explanation' , 'created_timestamp', 'status','rating')
            }
        ),
    )
    search_fields = [
        'id',
        'client__Name',
        'client__id'
    ]

    list_display = [
        'id',
        'client_name',
        'clientCompany',
        'consultant',
        'sendQuote',
        'status',
        'update_timestamp',
    ]
    sortable_by=[
        'id'
    ]
    list_filter = [
        'status'
    ]
    list_per_page = 10
    
    def sendQuote(self, obj):
        url= reverse("sendConsultantRequestQuote_URL",args = [obj.client.pk, obj.pk])
        display_title = str(obj.client.Name)
        link = '<a href="%s">%s</a>'%(url, display_title)
        return mark_safe(link)
    
    
    def client_name(self, obj):
        url = reverse("admin:webaccount_client_personal_info_change",args = [obj.client.pk])
        display_title = str(obj.client.Name)
        link = '<a href="%s">%s</a>'%(url, display_title)
        return mark_safe(link)
    client_name.short_description = "Client Details"
    # ****************************************************************
    # Client Company Name
    # ****************************************************************
    def clientCompany(self,obj):
        return str(obj.client.company_name)
    
    clientCompany.short_description = "Company Name"
    sendQuote.short_description = "Consultant Quotes"

class ConsultantModelAdmin(admin.ModelAdmin):
    search_fields = [
        'Name'
    ]
    form = ConsultantModelForm
    # delete_confirmation_template = "delete_confirmation.html"
    # delete_selected_confirmation_template = "delete_selected_confirmation.html"
    change_list_template = "change_list.html"
    
class parentAmdin(admin.ModelAdmin):
    change_list_template = "change_list.html"
    delete_confirmation_template = "delete_confirmation.html"
    delete_selected_confirmation_template = "delete_selected_confirmation.html"
    
    list_display=[
        'connectToConsultationField'
    ]
    search_fields = [
        'parentName'
    ]
    
    def connectToConsultationField(self, obj):
        url= reverse("SeeDetails")
        link = '<a href="%s">%s</a>'%(url,"Details" )
        return mark_safe(link)

    connectToConsultationField.short_description = "Details"
    
    
    def changelist_view(request, extra_context=None):
        return redirect(reverse("admin:webaccount_consultantmodel_changelist"))
    
    def delete_view(self, request, object_id, extra_context=None):
        try:
            if ParentModel.objects.get(id = object_id).parentName == 'Accounting':
                messages.error(request, "Accounting Field can not be changed or deleted.")
                return redirect("SeeDetails")
            else:
                return super().delete_view( 
                    request, object_id, extra_context=None)
        except:
            return super().delete_view( 
                    request, object_id, extra_context=None)
            
    def change_view(self,request, object_id, form_url='', extra_context=None):
        try:
            if ParentModel.objects.get(id = object_id).parentName == 'Accounting':
                messages.error(request, "Accounting Field can not be changed or deleted.")
                return redirect("SeeDetails")
            else:
                return super().change_view( 
                    request, object_id, extra_context=None)
        except:
            return super().change_view( 
                    request, object_id, extra_context=None)
            

admin_site = MyAdminSite()
admin_site.register(ParentModel,parentAmdin)
admin_site.register(Sector, SectorAdmin)
admin_site.register(Client_Personal_Info, Client_Personal_InfoAdmin)
admin_site.register(Required_Documents,Required_DocumentsAdmin)
admin_site.register(clientInvoice, clientInvoiceAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(clientReport, clientReportAdmin)
admin_site.register(ConsulatationRequest, ConsulatationRequestAdmin)
admin_site.register(ConsultantModel, ConsultantModelAdmin)


# pickup order
admin_site.register(Shipping)

class PickUpOrderRequestsAdmin(admin.ModelAdmin):
    form = PickUpRequestOrdersForm
    search_fields = [
        'client__Name',
        'client__id',
        'id'
    ]
    list_display = [
        'id',
        'client_name',
        "client_company",
        "client_location",
        'status',
        'updated_timestamp'
        
    ]
    
    ordering = [
        'client',
        'status',
        'shippingMethod'
    ]
    sortable_by = [
        'status',
        'shippingMethod'
    ]
    list_filter = [
        'status'
    ]
    list_per_page = 10


   
    
    
    def client_name(self, obj):
        url = reverse("admin:webaccount_client_personal_info_change",args = [obj.client.pk])
        display_title =  str(obj.client.Name)
        link = '<a href="%s">%s</a>'%(url, display_title)
        return mark_safe(link)
    client_name.short_description = "Client"
    
    def client_location(self, obj):
        return obj.client.location
    
    def client_company(self, obj):
        return obj.client.company_name
    
    client_location.short_description = "Location"
    client_company.short_description = "Company"

admin_site.register(PickUpRequestOrders, PickUpOrderRequestsAdmin)