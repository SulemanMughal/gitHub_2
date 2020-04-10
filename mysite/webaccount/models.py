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
    Name            =   models.CharField(max_length=300, blank=False, unique = True)
    Email           =   models.EmailField(max_length=300, blank=False, unique = True)
    Phone_Number    =   models.CharField(max_length=10, verbose_name="Phone Number", validators = [ phoneNumberValidator ],  blank=False, unique = True)
    company_name    =   models.CharField(max_length=300, verbose_name="Company Name")
    CR              =   models.CharField(max_length=10, verbose_name="CR", validators = [convertToInteger], blank=False)
    location        =   models.CharField(max_length=300)
    contact_number  =   models.CharField(max_length=10, validators = [ phoneNumberValidator ], verbose_name="Contact Number")
    sector          =   models.ForeignKey(Sector, on_delete=models.CASCADE)
    Number_of_branches =   models.IntegerField(validators = [ integerValidator ], verbose_name="Number of Branches", default=1)
    Number_of_employees =   models.IntegerField(validators = [ integerValidator ], verbose_name = "Number of Employees", default =1 )
    QR_code         =   models.FileField()
    Services                    =   models.CharField(max_length=300) 
    Number_of_subaccounts       =   models.IntegerField(verbose_name="Number of Sub-Accounts", validators = [ integerValidatorAccounts ], default = 0, blank=False)
    package_price               =   models.IntegerField(verbose_name = "Package Price", validators = [ integerValidatorAccounts ], default = 0, blank=False)
    paymenStatus  = models.CharField(max_length = 15, choices = PAYMENT_TYPE_CHOICE, default= "Pending", verbose_name = "Subscription Status")
    status = models.CharField(max_length=10, default = "New", choices = STATE_CHOICES, verbose_name="Status")
    last_update = models.DateTimeField(auto_now_add=True, verbose_name="Last Update")
    managerRelational = models.ForeignKey(relationManager, on_delete=models.CASCADE, verbose_name="RM", blank = True, null=True)

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
        super().save(*args, **kwargs)  # Call the "real" save() method.
        
    
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
        if self.document.file_type == "image":
            if self.uploadFile.name.split(".")[-1] not in IMAGE_FILE_EXTENSION:
                raise ValidationError(_('Uploded document type and the selected document type must be same.'))
        else:
            if self.document.file_type != self.uploadFile.name.split(".")[-1]:
                raise ValidationError(_('Uploded document type and the selected document type must be same.'))