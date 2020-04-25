from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.shortcuts import render,redirect
import datetime
from django.urls import path
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
now = timezone.now()

# Create your models here.

IMAGE_FILE_EXTENSION = [
    "BMP",
    "bmp",
    "JPG",
    "jpg",
    "GIF",
    "gif",
    "PNG",
    "png"
]


# Consultations Choices
CONSULTATION_CHOICES = (
    ('New', 'New'),
    ('Confirmed', 'Confirmed'),
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
    ('Close', 'Close'),
    ('Rejected', 'Rejected'),
    ('Declined', 'Declined')
)

def integerValidatorAccounts(value):
    if value < 0:
        raise ValidationError(
                _('The number should be equal to or greater than "0"'),
            )
    else:
        value


def phoneNumberValidator(value):
    try:
        if value[0:2] != "05" or len(value)!= 10 :
            raise ValidationError(
                _('The phone number format should be "05xxxxxxxx"'),
            )
        else:
            int(value)
            return value
    except ValueError:
        raise ValidationError(
            _('The phone number format should be "05xxxxxxxx"'),
        )

def integerValidator(value):
    if value <= 0:
        raise ValidationError(
                _('The number should be greater than "0"'),
            )
    else:
        value


def convertToInteger(value):
    try:
        if len(value)!= 10:
            # print(len(value))
            # print("11111111")
            raise ValidationError(
                _('The number should be of 10 digits.'),
            )
        else:
            # print("2222222222222")
            int(value)
            return value
    except ValueError:
        # print("33333333333333333")
        raise ValidationError(
                _('The number should be of 10 digits.'),
            )

# IntegrityError For Client Sector Field
def checkIntegrityError(value):
    try:
        if value is None:
            raise ValidationError(
                _('Sector field is empty.'),
            )
    except:
        raise ValidationError(
            _('Sector field is empty.'),
        )

service=(
('BookKeeping','BookKeeping'),
('VAT','VAT')
)


REQUIRED_DOCUMENTS_STATUS = (
    ('None', 'None'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected')
)

types=(
('pdf','pdf'),
('docs','docs'),('image','image')
)

STATE_CHOICES=(
    ('New', 'New'),
    ('Active', 'Active'),
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
    ('Disabled', 'Disabled')
)

REPORT_TYPE_CHOICES = (
    ('Income Statement', 'Income Statement'),
    ('Balance Sheet','Balance Sheet' ),
    ('VAT Report', 'VAT Report'),
    ('Ratio Analysis Report', 'Ratio Analysis Report')
)



YEAR_CHOICES = [(r,r) for r in range( datetime.date.today().year+5, 1980, -1)]

MONTH_QUARTER_CHOICES = [
    ('JANUARY', 'JANUARY'),
    ('FEBRUARY', 'FEBRUARY'),
    ('MARCH', 'MARCH'),
    ('APRIL', 'APRIL'),
    ('MAY', 'MAY'),
    ('JUNE', 'JUNE'),
    ('JULY', 'JULY'),
    ('AUGUST', 'AUGUST'),
    ('SEPTEMBER', 'SEPTEMBER'),
    ('OCTOBER', 'OCTOBER'),
    ('NOVEMBER', 'NOVEMBER'),
    ('DECEMBER', 'DECEMBER'),
    ('Q1', 'Q1'),
    ('Q2', 'Q2')
]


INVOICE_TYPE_CHOICES = [
    ('New', 'New'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
    ('Processing', 'Processing'),
    ('Pending', 'Pending')
]

PAYMENT_TYPE_CHOICE = [
    ('Pending', 'Pending'),
    ('Overdue', 'Overdue'),
    ('Declined', 'Declined'),
    ('Paid', 'Paid')
]

class relationManager(models.Model):
    manager = models.ForeignKey(get_user_model(), on_delete = models.CASCADE)

    def __str__(self):
        return self.manager.username

class Sector(models.Model):
    Name = models.CharField(max_length = 100, default = '', unique = True)

    def __str__(self):
        return self.Name

class Client_Personal_Info(models.Model):
    Name    =   models.CharField(
                max_length      =   300, 
                blank           =   False, 
                unique          =   False,
                null            =   False,
                error_messages  =   {
                    'blank'     :   "Name field is empty.",
                    'null'      :   "Name field is empty."
                },
                verbose_name = "Name"
            )
    Email   =   models.EmailField(
                    max_length=300, 
                    blank=False, 
                    unique = True,
                    null = False,
                    verbose_name = "Email",
                    error_messages  =   {
                    'blank'     :   "Email field is empty.",
                    'null'      :   "Email field is empty.",
                    'unique'    :   "Already exists."
                },
            )
    Phone_Number    =   models.CharField(
        max_length=10, 
        verbose_name="Phone Number", 
        validators = [ phoneNumberValidator ],  
        blank=False, 
        unique = True,
        null = False,
        error_messages  =   {
            'blank'     :   "Phone Number is required.",
            'null'      :   "Phone Number is required.",
            'unique'    :   "Already exists."
        }
        )
    company_name    =   models.CharField(
        max_length=300, 
        verbose_name="Company Name",
        blank = False,
        unique = False,
        null = False,
        error_messages  =   {
            'blank'     :   "Company name is required.",
            'null'      :   "Company name is required."
        }
        )
    CR  =   models.CharField(
        max_length      =   10, 
        verbose_name    =   "CR", 
        validators      =   [
                        convertToInteger
                        ], 
        blank           =   False,
        unique          =   True,
        null = False,
        error_messages  =   {
            'blank'     :   "CR is required.",
            'null'      :   "CR is required.",
            'unique'    :   "Already exists."
        }
    )
    location        =   models.CharField(
        max_length=300,
        verbose_name = "Location",
        unique = False,
        blank=False,
        null = False,
        error_messages  =   {
            'blank'     :   "locationlocation is required.",
            'null'      :   "location is required."
        }
        )
    contact_number  =   models.CharField(
        max_length=10, 
        validators = [ 
                phoneNumberValidator 
            ], 
        verbose_name="Contact Number",
        blank=False,
        null = False,
        unique = False,
        error_messages  =   {
            'blank'     :   "location is required.",
            'null'      :   "location is required."
        }
        )
    sector  =   models.ForeignKey(
        Sector, 
        on_delete   =   models.CASCADE,
        null = False,
        blank = False,
        error_messages = {
            "null":"Sector Field is not selected",
            "blank":"Sector can not be left as blank."
        },
        verbose_name = "Sector",
        validators = [
            checkIntegrityError
        ]
    )
    Number_of_branches =   models.IntegerField(
        validators = [ 
                integerValidator 
            ], 
        verbose_name="Number of Branches", 
        default=1,
        blank = False,
        null = False,
        unique = False,
        error_messages = {
            "null":"Number of Branches Field is not entered",
            "blank":"Number of Branches can not be left as blank."
        },
        )
    Number_of_employees =   models.IntegerField(
        validators = [ 
                integerValidator 
            ], 
        verbose_name = "Number of Employees", 
        default =1,
        blank = False,
        null = False,
        unique = False,
        error_messages = {
            "null":"Number of Employees Field is not entered",
            "blank":"Number of Employees can not be left as blank."
        },
        )
    QR_code         =   models.FileField()
    Services                    =   models.CharField(
        max_length=300,
        verbose_name = "Services",
        unique = False,
        blank = False,
        null = False,
        error_messages = {
            "null":"Services Field is not entered",
            "blank":"Services can not be left as blank."
        },
        ) 
    Number_of_subaccounts       =   models.IntegerField(
        verbose_name="Number of Sub-Accounts", 
        validators = [ 
                integerValidatorAccounts 
            ], 
        default = 0, 
        blank=False,
        null = False,
        unique = False,
        error_messages = {
            "null":"Number of Sub-Accounts Field is not entered",
            "blank":"Number of Sub-Accounts can not be left as blank."
        },
        )
    package_price               =   models.IntegerField(
        verbose_name = "Package Price", 
        validators = [ 
            integerValidatorAccounts 
        ], 
        default = 0, 
        blank=False,
        null = False,
        unique = False,
        error_messages = {
            "null":"Package Price Field is not entered",
            "blank":"Package Price can not be left as blank."
        },
        )
    paymenStatus  = models.CharField(
        max_length = 15, 
        choices = PAYMENT_TYPE_CHOICE, 
        default= "Pending", 
        verbose_name = "Subscription Status",
        blank = False,
        null = False,
        unique = False,
        error_messages = {
            "null":"Subscription Status Field is not entered",
            "blank":"Subscription Status can not be left as blank."   
        }
        )
    status = models.CharField(max_length=10, default = "New", choices = STATE_CHOICES, verbose_name="Status")
    last_update = models.DateTimeField(auto_now_add=True, verbose_name="Last Update")
    managerRelational = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="RM", blank = True, null=True)

    class Meta:
        verbose_name = "Client Personal Information"
        verbose_name_plural = "Client Personal Information"

    def __str__(self):
        return self.Name

    def clean(self, *args, **kwargs):
        self.last_update = timezone.now()
        # print(self.Services)
        self.Services = self.Services
        if self.status == "Active":
            if self.paymenStatus == "Paid":
                self.status = "Active"
            else:
                self.status = "Pending"
                raise ValidationError(_('Client Account can not be activated  until the payment is completed.'))    
        if self.paymenStatus != "Paid" or self.status != "Active":
            if self.managerRelational is not None:
                raise ValidationError(_('You cannot assign a relationship manager until the payment is completed and the account is active.'))
        try:
            if self.sector is None:
                raise ValidationError(_('Sector field is empty.'))
        except :
            raise ValidationError(_('Sector field is empty.'))
        # print("*************************************************")
        # print(Client_Personal_Info.objects.all())
        try:
            # self.CR = self.CR
            # print(self.__dict__)
            objs = Client_Personal_Info.objects.filter(CR = self.CR)
            if len(objs) != 0:
                # print(objs[0])
                if objs[0].id == self.id:
                    pass
                else:
                    raise ValidationError(_('CR field already.'))
        except:
            raise ValidationError(_('CR field already.'))
        # print("*************************************************")
        # super().save(*args, **kwargs)  
        
    
class clientReport(models.Model):
    client = models.ForeignKey(Client_Personal_Info, on_delete = models.CASCADE)
    reportType = models.CharField(max_length = 25, choices = REPORT_TYPE_CHOICES, default = "Income Statement")
    dateYear = models.IntegerField(default=now.year, verbose_name="Year",choices=YEAR_CHOICES , validators=[MinValueValidator(1980), MaxValueValidator(now.year+5)])
    month_quarterType = models.CharField(max_length = 20, default=now.month, verbose_name="Month or Quarter", choices=MONTH_QUARTER_CHOICES)
    finalReportIssueDate = models.DateField(default=timezone.now, verbose_name = "Final Report Issue Date")

    class Meta:
        verbose_name = "Client Report"
        verbose_name_plural = "Client Reports"

    def __str__(self):
        return self.client.Name

class clientInvoice(models.Model):
    client = models.ForeignKey(Client_Personal_Info, on_delete = models.CASCADE)
    submittingDate = models.DateField(default = timezone.now, verbose_name = "Submitting Date")
    statusType = models.CharField(max_length=15, choices = INVOICE_TYPE_CHOICES, default = "New", verbose_name = "Status")
    lastUpdate = models.DateTimeField(default = timezone.now, verbose_name = "Last Update")

    class Meta:
        verbose_name = "Client Invoice"
        verbose_name_plural = "Client Invoices"
    
    def __str__(self):
        return self.client.Name

class Required_Documents(models.Model):
    Name    =   models.CharField(max_length=300 )
    file_type =   models.CharField(max_length=300,choices=types, verbose_name = "File Type")

    class Meta:
        verbose_name = "Required Document"
        verbose_name_plural = "Required Documents"

    def __str__(self):
        return str(self.Name) + "." + str(self.file_type)

class ClientRequiredDocuments(models.Model):
    client = models.ForeignKey(Client_Personal_Info, on_delete = models.CASCADE)
    document = models.ForeignKey(Required_Documents, on_delete=models.CASCADE, verbose_name = "Submit Document")
    uploadFile = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name = "Upload Document", blank=True)
    status = models.CharField(max_length = 10, verbose_name = "Status",  choices = REQUIRED_DOCUMENTS_STATUS, default = "None")

    class Meta:
        verbose_name = "Client Document"
        verbose_name_plural = "Client Documents"

    def __str__(self):
        try:
            return str(self.client.Name) + "'s " + str(self.document)
        except:
            return str(self.client.Name) 

    def clean(self):
        try:
            self.document = self.document
        except :
            raise ValidationError(_('Upload Document Name should be selected.'))
        if self.document.file_type:
            # print(self.uploadFile.__dict__)
            if len(self.uploadFile.name) == 0:
                raise ValidationError(_('Document has not been uploaded.'))
            elif self.document.file_type == "image":
                    if self.uploadFile.name.split(".")[-1] not in IMAGE_FILE_EXTENSION:
                        raise ValidationError(_('Uploded document type and the selected document type must be same.'))
            else:
                if self.document.file_type != self.uploadFile.name.split(".")[-1]:
                    raise ValidationError(_('Uploded document type and the selected document type must be same.'))


class ConsultantModel(models.Model):
    Name = models.CharField(max_length = 100,
                            verbose_name = "Field",
                            unique = True,
                            default = None,
                            blank = False,
                            error_messages = {
                                'blank' : "Name is required",
                                'unique' : "Name Already Exists."
                            }
                            )
    
    parentField = models.CharField(max_length = 100,
                                   verbose_name = "Parent Field",
                                   unique = True,
                                   default = None,
                                   blank = True,
                                   null = True,
                                   error_messages = {
                                'unique' : "Parent Field Already Exists."
                            }
                                   )
    
    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        ordering = [
            '-id'
        ]
    
    def __str__(self):
        return self.Name


# Consultation Model Created By Client
class ConsulatationRequest(models.Model):
    client = models.ForeignKey(Client_Personal_Info, on_delete=models.CASCADE, null=False)
    consultant = models.ForeignKey(ConsultantModel, 
                                on_delete=models.CASCADE, 
                                null=False, 
                                blank = False,
                                verbose_name = "Consultation Field")
    
    explanation =models.TextField(verbose_name="Explanation",
                                  max_length=200,
                                  blank=False,
                                  default = None,
                                  error_messages={
                                      'blank' : "Explanation is Rquired."
                                  })
    
    created_timestamp = models.DateTimeField(auto_now_add=False, 
                                            auto_now = False, 
                                            verbose_name = "Consultation Date & Time",
                                            default = timezone.now
                        )
    status = models.CharField(max_length = 100, verbose_name="Status", choices =CONSULTATION_CHOICES, default="New", blank=False)
    Name = models.CharField(max_length = 100,
                            verbose_name = "Consultation Name",
                            unique = False,
                            default = None,
                            blank = True,
                            null = True,
                            error_messages = {
                                'blank' : "Name is required",
                                'unique' : "Name Already Exists."
                            }
                            )
    price = models.DecimalField(verbose_name="Price", default = None, blank = True, max_digits = 10, decimal_places=2, null=True)
    update_timestamp = models.DateTimeField(auto_now_add=True)
    clientPaid = models.DecimalField(max_length = 100,
                   verbose_name="Client Paid Amound",
                   default = None,
                   max_digits = 10, 
                   decimal_places=2, 
                   null=True,
                   blank=True
                   )
    clientPaidAllAmount = models.BooleanField(verbose_name="Client Paid All Amount",
                                                 default = False,
                                                 )
    decline_explanation = models.TextField(max_length = 200,
                                           verbose_name="Decline Reaons",
                                           blank = True,
                                           null = True,
                                           default=''
                                           )
    
    rating = models.IntegerField(verbose_name="Rating", default=0, blank=True, null = True)
    feedbackFile = models.FileField(upload_to='uploads/feedback/%Y/%m/%d/', verbose_name = "Feedback Document", blank=True)
    
    class Meta:
        verbose_name = "Consultation Request"
        verbose_name_plural = "Consultation Requests"
        ordering = [
            '-id'
        ]

    def __str__(self):
        return "{name}'s Consultatoin".format(name=self.client.Name)
    
    
    
    
# --------------------------------------------------------
# SHIPPING METHOD

class Shipping(models.Model):
    Name = models.CharField(max_length = 50,
                            verbose_name="Shipping Method",
                            blank  =False,
                            unique = True,
                            null = False,
                            default = '')
    
    def __str__(self):
        return str(self.Name)    

# ---------------------------------------------------------------------------
# PICKUPREQUESTORDERS

PickUpRequestOrdersStatues = (
    ('ACCEPT', 'ACCEPT'),
    ('REJECT', 'REJECT'),
    ('ON DELIVERY', 'ON DELIVERY'),
    ('RECEIVED', 'RECEIVED'),
    ('FAILED', 'FAILED'),
    ('NONE','NONE')
)

# PICK UP ORDERS MODELS
class PickUpRequestOrders(models.Model):
    client = models.ForeignKey(Client_Personal_Info, 
                               null =  False, 
                               blank = False,
                               on_delete=models.CASCADE
                    )

    status = models.CharField(max_length = 15, 
                              choices = PickUpRequestOrdersStatues,
                              verbose_name = "Request Status",
                              blank = False,
                              null = False,
                              default = 'NONE'
                              )

    shippingMethod = models.ForeignKey(Shipping, on_delete=models.CASCADE, 
                                       blank = False,
                                       null = False,
                                       verbose_name = "Shipping Method",          
                                       error_messages = {
                                'blank' : "Shipping method is required",
                                'null' : "Shipping method is required"
                            })
    
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Created Timestamp")
    updated_timestamp = models.DateTimeField(default = timezone.now, verbose_name="Last Updated Timestamp")
    
    def __str__(self):
        return str(self.client.Name) + "'s" + " Pickup Order Request"
# -----------------------------------------------------------------------------------