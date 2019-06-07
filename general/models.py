from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from sokohaliAdmin.models import CostCalcSettings, Batch, ExportObjCostCalcSettings
from modelfield_choices import *
from django.utils import timezone
from django.conf import settings
import datetime
import markdown
from django.utils import timezone
from django.template.defaultfilters import slugify
from modelfield_choices import ORDER_SOURCES, COUNTRY, TITLE, LOCAL_DELIVERY_CHOICES

from service_provider.models import MarketingMember,WarehouseMember
from general.image_helpers import convert_remote_image_to_base64

#Maximum package sync count
max_sync_pkg_count = 400


class PackageDimension(models.Model):
    box_length      = models.DecimalField(max_digits = 15, decimal_places = 1, null=True, blank=True)
    box_width       = models.DecimalField(max_digits = 15, decimal_places = 1, null=True, blank=True)
    box_height      = models.DecimalField(max_digits = 15, decimal_places = 1, null=True, blank=True)
    box_weight      = models.DecimalField(max_digits = 15, decimal_places = 1, default = 0, null=True, blank=True)
    box_weight_K      = models.DecimalField(max_digits = 15, decimal_places = 1, default = 0)

    class Meta():
        abstract = True


pkg_statuses = ['Received', 'Prepared for Shipping', 'Assigned to batch',
                        'Delivered to Carrier', 'Departed', 'Clearing Customs', 'Processing for Delivery',
                        'Prepared for Delivery', 'Enroute to Delivery', 'Ready for Collection', 'Delivered']


class BasePackage(PackageDimension):

    user                = models.ForeignKey(User, null = True)
    created_on          = models.DateTimeField(default = timezone.now)
    box_weight_Actual          = models.DecimalField(max_digits = 15, decimal_places = 1)
    box_weight_Actual_K        = models.DecimalField(max_digits = 15, decimal_places = 1)
    batch_assigned      = models.ForeignKey(Batch, null=True, blank=True)


    box_weight_Dim          = models.DecimalField(max_digits = 15, decimal_places = 1, default = 1.0)
    box_weight_Dim_K        = models.DecimalField(max_digits = 15, decimal_places = 1, default = 1.0)

    box_quantity        = models.IntegerField(default=1)

    number              = models.IntegerField(default = 0)

    status              = models.CharField(max_length=50, default = "New")# choices = PACKAGE_STATUS, null=True)

    approved            = models.BooleanField(default=False)

    deleted             = models.BooleanField(default=False)

    pkg_id              = models.CharField(max_length=20, null=True)

    updated_on          = models.DateTimeField(null=True)
    updated_by          = models.CharField(max_length=20, null=True)

    barcode_src         = models.CharField(max_length=80, null=True, blank=True)

    barcode_id          = models.CharField(max_length=80, null=True, blank=True)

    #True for Ordered Packages
    ordered             = models.BooleanField(default=False)

    #billing
    insure                  = models.BooleanField(default=False)

    insurance_fee_D         = models.FloatField(default = 0)
    insurance_fee_N         = models.FloatField(default = 0)

    VAT_charge_D            = models.FloatField(default = 0)#null=True)
    VAT_charge_N            = models.FloatField(default = 0)#null=True)

    pick_up_charge_D        = models.FloatField(default=0)
    pick_up_charge_N        = models.FloatField(default=0)

    service_charge_D        = models.FloatField(default = 0)#null=True)
    service_charge_N        = models.FloatField(default = 0)#null=True)

    #generated on booking confirmation
    user_total_payable_D       = models.FloatField(default = 0)
    user_total_payable_N       = models.FloatField(default = 0)

    #generated during processing
    admin_total_payable_D       = models.FloatField(default = 0)
    admin_total_payable_N       = models.FloatField(default = 0)

    balance_D                = models.FloatField(default = 0)
    balance_N                = models.FloatField(default = 0)

    balance_paid_D           = models.FloatField(default=0)
    balance_paid_N           = models.FloatField(default=0)

    #shipment_type           = models.CharField(max_length = 20,default="import")

    costcalc_instance       = models.ForeignKey(ExportObjCostCalcSettings, null=True)

    #freight costs
    courier_cost_D          = models.FloatField(default = 0)
    courier_cost_N          = models.FloatField(default = 0)

    intl_freight_D          = models.FloatField(default = 0)
    intl_freight_N          = models.FloatField(default = 0)

    local_freight_D         = models.FloatField(default = 0)
    local_freight_N         = models.FloatField(default = 0)

    coverage_amount_D       = models.FloatField(default = 0)
    coverage_amount_N       = models.FloatField(default = 0)

    tracking_number         = models.CharField(max_length = 50, null=True)

    delivery_speed          = models.CharField(max_length = 50)
    message_center          = models.ForeignKey('MessageCenter',null=True,blank=True)

    prepared_for_shipping   = models.BooleanField(default = False)
    assigned_to_batch       = models.BooleanField(default = False)


    syncedStatus            = models.BooleanField(default = False)
    barcode_base64          = models.TextField()

    pkg_image              = models.ImageField(upload_to = 'pkg_images/%Y/%m/%d', null=True, blank=True)

    shipping_method        = models.CharField(max_length = 50, choices = LOCAL_DELIVERY_CHOICES)

    is_estimate            = models.BooleanField(default = False)
    payment_method         = models.CharField(max_length =  30, null=True, blank=True)

    created_by_admin       = models.BooleanField(default = False)
    has_promo              = models.BooleanField(default = False)
    promo_rate_per_lb      = models.FloatField(default = 0.0)
    additional_charges_D     = models.FloatField(default = 0.0)
    additional_charges_N     = models.FloatField(default = 0.0)

    discount_D                  = models.FloatField(default = 0.0)
    discount_N                  = models.FloatField(default = 0.0)
    discount_percentage         = models.FloatField(default = 0.0)

    def lbkg_factor(self):
        return 0.45359

    def box_weight_higher(self):
        if self.box_weight_Actual > self.box_weight_Dim:
            return float(self.box_weight_Actual)
        return float(self.box_weight_Dim)

    def box_weight_higher_K(self):
        return round(float(self.box_weight_higher()) * self.lbkg_factor(), 2)

    def total_value_linked_items(self):
        items = self.orderproduct_set.all().aggregate(Sum('listed_price_D'))
        total_value_linked_items = items['listed_price_D__sum']
        if total_value_linked_items == None:
            return 0
        return total_value_linked_items

    def linked_items(self):
        if self.shipment_type == "import":
            return [item.item_info() for item in self.importitem_set.all()]
        else:
            return [item.item_info() for item in self.exportitem_set.all()]

        # try:
        #     return [item.item_info() for item in self.shipmentitem_set.all()]
        # except:
        #     return [item.item_info() for item in self.orderproduct_set.all()]

    def pkg_extra_info(self):
        #return {'pkg_no': self.number, 'linked_items': [item.item_info() for item in self.orderproduct_set.all()]}
        return {'pkg_no': self.number, 'linked_items': self.linked_items()}

    def dimension(self):
        return '%d" x %d" x %d"' %(self.box_length, self.box_width, self.box_height)

    def fedex_tracking_info(self):
        tracking_info = {}
        linked_items_count = len(self.linked_items())
        #print "linked_items_count: %s" %linked_items_count
        if linked_items_count > 0:
            tracking_info = {'pkg_no': self.number, 'pkg_id': self.id, "dimension": self.dimension(), "linked_items_count": linked_items_count,
                    "linked_items": self.linked_items(), "status": self.status,
                    "weight_lbs": self.box_weight_higher(), "weight_kg": self.box_weight_higher_K()}

            if self.expires_on:
                tracking_info.update({"expires_on": self.expires_on.strftime("%d-%m-%Y")})

        return tracking_info

    def linkedItems_totalValue_custom(self):
        # total_value = 0
        # if hasattr(self, "shipmentpackage"):
        #     linkedItems_totalValue_1 = self.shipmentitem_set.filter(Q(deleted = False)).aggregate(Sum('total_value'))
        #     if linkedItems_totalValue_1['total_value__sum'] == None or linkedItems_totalValue['total_value__sum'] <= 0:
        #         total_value += 0
        #     total_value += linkedItems_totalValue_1['total_value__sum']

        # if hasattr(self, "orderpackage"):
        #     linkedItems_totalValue_2 = self.orderproduct_set.filter(Q(deleted = False)).aggregate(Sum('listed_price_D'))
        #     if linkedItems_totalValue_2['listed_price_D__sum'] == None or linkedItems_totalValue['listed_price_D__sum'] <= 0:
        #         total_value += 0
        #     total_value += linkedItems_totalValue_2['listed_price_D__sum']

        # return total_value
        total_value = 0
        if hasattr(self, "exportpackage"):
            linkedItems_totalValue_1 = self.exportitem_set.filter(Q(deleted = False)).aggregate(Sum('naira_value'))
            if linkedItems_totalValue_1['total_value__sum'] == None or linkedItems_totalValue['total_value__sum'] <= 0:
                total_value += 0
            total_value += linkedItems_totalValue_1['total_value__sum']

        if hasattr(self, "importpackage"):
            linkedItems_totalValue_2 = self.importitem_set.filter(Q(deleted = False)).aggregate(Sum('total_value'))
            if linkedItems_totalValue_2['total_value__sum'] == None or linkedItems_totalValue['total_value__sum'] <= 0:
                total_value += 0
            total_value += linkedItems_totalValue_2['total_value__sum']

        return total_value


    def un_synchroized_packages(self):
        if self.approved:
            approved_status = 1
        else:
            approved_status = 0

        info_dict = {}

        if hasattr(self, "order"):
            info_dict.update({'pkg_id': self.pk, 'barcode_id': self.gen_barcode_id(), 'box_number': self.number, 'booking_ref': self.order.tracking_number, "box_type": 1, 'shipping_method': self.order.shipping_method,
                      'box_length': self.box_length, 'box_width': self.box_width, 'box_height': self.box_height, 'box_weight': self.box_weight_higher(), 'box_weight_K': self.box_weight_higher_K(),
                     'status': self.status, 'credit_balance_D': self.order.order_balance_D, 'created_at': str(self.created_on), 'approved': approved_status,
                    'linked_items': [ item.item_info() for item in self.orderproduct_set.filter(deleted = False) ]})
        else:
            info_dict.update({'pkg_id': self.pk, 'barcode_id': self.gen_barcode_id(), 'box_number': self.number, 'booking_ref': self.shipment.tracking_number, "box_type": 1, 'shipping_method': self.shipment.shipping_method_dict(),
                      'box_length': self.box_length, 'box_width': self.box_width, 'box_height': self.box_height, 'box_weight': self.box_weight_higher(), 'box_weight_K': self.box_weight_higher_K(),
                     'status': self.status, 'credit_balance_D': self.shipment.credit_balance_D, 'created_at': str(self.created_on), 'approved': approved_status,
                    'linked_items': [ item.item_info() for item in self.shipmentitem_set.filter(deleted = False) ]})

        if self.storageUnit:
            info_dict.update({
                'column': self.storageUnit.column,
                    'row': self.storageUnit.row})

        return info_dict

    def pkg_type(self):
        if hasattr(self, 'export'):
            pkg_type = 'export'
        else:
            pkg_type = 'import'
        return pkg_type

    def sync_package_info(self):
        info_dict = {}
        if self.syncedStatus:
            syncedStatus = 1
            processed    = 1
        else:
            syncedStatus = 0
            processed    = 0
        #print "self.barcode_base64: ",self.barcode_base64
        if self.barcode_base64 == "":
            #image_response = requests.get("https://s3-eu-west-1.amazonaws.com/sokohali/export-barcodes/package-E28.png").content
            #info_dict.update({'barcodeBase64': base64.b64encode(image_response)})
            image_path = "https://s3-eu-west-1.amazonaws.com/sokohali/export-barcodes/package-E28.png"
            info_dict.update({'barcodeBase64': convert_remote_image_to_base64(image_path)})
        else:
            info_dict.update({'barcodeBase64': self.barcode_base64})

        info_dict.update({'pkg_id': self.pk, 'suite_no': self.user.useraccount.suite_no, "receiver_name": "Receiver Name", "receiving_address": "Receiving Address",
                        'barcode_id': self.tracking_number, 'tracking_number': self.tracking_number, "pkg_type": self.pkg_type(), 'shipping_method': self.delivery_speed,
                        'box_length': self.box_length, 'box_width': self.box_width, 'box_height': self.box_height, 'box_weight': self.box_weight_higher(), 'box_weight_K': self.box_weight_higher_K(),
                        'status': self.status, 'balance_D': self.balance_D, 'created_on': str(self.created_on), 'syncedStatus': syncedStatus,
                        'processed': processed})
        return info_dict



    def gen_barcode_id(self):
        # if hasattr(self, "order"):
        #     barcode_data = "%s%s" %(self.id, "Z")
        # elif hasattr(self, "shipment"):
        #     barcode_data = "%s%s" %("Z", self.id)
        # else:
        #     barcode_data = "%s%s" %('E', self.id)
        # return barcode_data
        return self.tracking_number

    def as_dict(self):
        info_dict = {'pkg_no': self.number, 'pkg_id': self.pk, 'status': self.status, 'barcode_id': self.gen_barcode_id()}

        if hasattr(self, "order"):
            info_dict.update({'credit_balance_D': self.order.order_balance_D, 'shipping_method': self.order.shipping_method})
        else:
            info_dict.update({'credit_balance_D': self.shipment.credit_balance_D, 'shipping_method': self.shipment.shipping_method_dict()})

        return info_dict

    def pkg_shipment_type(self):
        if hasattr(self,"export"):
            return "Export"
        return "Import"

    def total_freight_cost(self):
        total_D = self.intl_freight_D + self.local_freight_D + self.courier_cost_D
        total_N = self.intl_freight_N + self.local_freight_N + self.courier_cost_N
        return {"dollar_value": total_D, "naira_value": total_N}

    def total_intl_freight_D(self):
        return self.intl_freight_D + self.courier_cost_D

    def total_intl_freight_N(self):
        return self.intl_freight_N + self.courier_cost_N

    def distinct_tracking_history(self):
        #return self.get_queryset().filter
        # pkg_statuses = ['Received', 'Prepared for Shipping', 'Assigned to batch',
        #                 'Delivered to Carrier', 'Departed', 'Clearing Customs', 'Processing for Delivery',
        #                 'Prepared for Delivery', 'Enroute to Delivery', 'Ready for Collection', 'Delivered']

        #print self.shipmentedithistory_set.filter(status__in = pkg_statuses)#.values('status').distinct()
        #if self.shipment:
        # try:
        #     return self.shipmentedithistory_set.filter(status__in = pkg_statuses)#.values('status').distinct()
        # except:
        #     return self.orderhistory_set.filter(status__in = pkg_statuses)#.values('status').distinct()
        return None
        #if hasattr(self, "export"):
         #   return self.edithistory_set.filter(status__in = pkg_statuses).distinct()#.values('status').distinct()
        #return self.shipmentedithistory_set.all().distinct()

    def pkg_items_statuses(self):
        return self.shippingitem_set.all().values('status')

    # def user_total_payable_vals(self):
    #     user_total_payable_D = self.total_shipping_cost_D + self.insurance_fee_D
    #     user_total_payable_N = self.total_shipping_cost_N + self.insurance_fee_N
    #     return user_total_payable_D, user_total_payable_N

    # def total_freight_vals(self):
    #     total_freight_D = self.local_freight_D + self.intl_freight_D
    #     total_freight_N = self.local_freight_N + self.intl_freight_N
    #
    #     return total_freight_D, total_freight_N

    def save(self,*args, **kwargs):
        self.pkg_id = self.pk
        if self.id is not None:
            self.updated_on = timezone.now()

            #Generate barcode id for app and label
            self.barcode_id = self.gen_barcode_id()

        if self.box_weight_Actual is not None:
            self.box_weight_Actual_K = float(self.box_weight_Actual) * self.lbkg_factor()
        else:
            self.box_weight_Actual_K = 0
        if self.box_weight_Dim is not None:
            self.box_weight_Dim_K    = float(self.box_weight_Dim) * self.lbkg_factor()
        else:
            self.box_weight_Dim = 0

        #save box higher val
        self.box_weight = self.box_weight_higher()
        self.box_weight_K = self.box_weight_higher_K()

        #self.linkedItems_totalValue = self.linkedItems_totalValue_custom()
        super(BasePackage, self).save(*args, **kwargs)
        #super(Package, self).save(*args, **kwargs)

    class Meta():

        ordering = ['-created_on']
        abstract = True

    def __unicode__(self):
        return str(self.tracking_number)

    def flagged_pkgs(self):
        return self.status == "Flagged"



class Package(BasePackage):

    cart_id             = models.CharField(max_length = 100, null = True)

    batch               = models.ForeignKey(Batch, null=True)
    batch_carrier       = models.CharField(max_length = 50, null=True, blank=True)

    carrier             = models.CharField(max_length=20, null=True)

    expires_on          = models.DateTimeField(null=True)
    assigned_on         = models.DateTimeField(null=True)

    #shipping_box_id       = models.IntegerField(default=0)
    #shipping_box_name     = models.CharField(max_length = 20, null=True, blank=True)
    carrier             = models.CharField(max_length = 30, null=True, blank=True)
    way_bill_number     = models.CharField(max_length = 50, null=True, blank=True)

    linkedItems_totalValue = models.FloatField(max_length=10, default=0.0)

    #country                 = models.CharField(max_length = 10, choices = COUNTRY, default = "us")


    ##approvedpackages    = ApprovedPackages()
    #
    #predefinedboxes_in_shipments    = PreDefinedBoxesInShipments()
    #addedboxes_in_shipments         = AddedBoxesInShipments()


    class Meta:
        ordering = ['created_on']
        verbose_name_plural = 'Packages'
        abstract = True

    # def __unicode__(self):
    #     return unicode(self.pk)

# class BaseCommonInfo(models.Model):
#     title           = models.CharField(max_length=10, choices = TITLE)
#     telephone       = models.CharField(max_length=100, null=True)
#     address         = models.CharField(max_length=300, null=True)
#     city            = models.CharField(max_length=100, null=True)
#     state           = models.CharField(max_length=50, null=True)#, choices=STATE)
#     country         = models.CharField(max_length=20, null=True, choices = COUNTRY)
#
#     class Meta:
#         abstract = True

class CommonInfo(models.Model):
    first_name      = models.CharField(max_length=100, null=True)
    last_name       = models.CharField(max_length=100, null=True)

    title           = models.CharField(max_length=10, choices = TITLE)
    telephone       = models.CharField(max_length=100, null=True)
    address         = models.CharField(max_length=300, null=True)
    city            = models.CharField(max_length=100, null=True)
    state           = models.CharField(max_length=50, null=True)#, choices=STATE)
    country         = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        abstract = True


class UserAccount(CommonInfo):
    user            = models.OneToOneField(User, unique = True, null = True)
    username        = models.CharField(max_length=50)
    activation_code = models.CharField(max_length=120, null=True)
    registration_time  = models.DateTimeField(auto_now_add = True)

    credit_amount_D   = models.FloatField(max_length = 20, default = 0)
    credit_amount_N   = models.FloatField(max_length = 20, default = 0)
    pending_amount_N  = models.FloatField(max_length = 20, default = 0)

    suite_no        = models.CharField(max_length=10, null=True)
    how_did_you_find_us     = models.CharField(max_length=15, choices = HOW_DID_YOU_FIND_US)

    image = models.ImageField(upload_to="user_photo", null=True, blank=True)

    deactivated     = models.BooleanField(default=False)
    flagged         = models.BooleanField(default=False)

    #BUSINESS ACCOUNT
    business_account = models.BooleanField(default=False)
    company_name = models.CharField(max_length = 50, null=True)
    industry     = models.CharField(max_length = 50, choices=INDUSTRY, null=True)
    enquiry      = models.TextField()

    how_did_you_find_us = models.CharField(max_length=50, choices=HOW_DID_YOU_FIND_US, null=True)

    photo_id = models.ImageField(upload_to = "Photo_ID", null = True, blank=True)
    utility_bill = models.ImageField(upload_to = "UtilityBill", null = True,  blank=True)

    #shipping address activated
    address_activation = models.BooleanField(default=False)

    #complete address and bank information / utility bill provided
    address_activation_completed = models.BooleanField(default = False)
    address_act_completed_date = models.DateTimeField(null = True)
    bank = models.CharField(max_length = 30, choices = BANKS, default ="", blank=True)

    bank_account_no = models.CharField(max_length = 100, default = "", blank=True)
    bvn_no = models.CharField(max_length = 100, default = "", blank=True)
    #marketer = models.ForeignKey(MarketingMember, null=True)
    marketer                            = models.ForeignKey('service_provider.MarketingMember', null=True)
    special_user = models.BooleanField(default = False)
    sokohali_admin = models.BooleanField(default = False)      

    #special_rate_per_lb_D                 = models.FloatField(default = 0)

    def account_type(self):
        if not self.address_activation:
            if self.address_activation_completed:
                return "Unverified Account"
            else:
                return "Inactive Account"
        # if self.business_account:
        #     return "VIP Silver Business Account"
        elif self.flagged:
            return "Flagged Account"
        elif self.deactivated:
            return "Deactivated Account"
        elif self.user.is_staff:
            return "Admin Account"
        else:
            return "Regular Account"

    def user_address(self):
        return "%s %s, %s, %s." %(self.address, self.city, self.state, self.country)

    def get_user_warehouse(self):
        return self.marketer.WPM.full_address()

    class Meta:
        ordering = ['-registration_time']
        verbose_name_plural = "User Accounts"

    def __unicode__(self):
        return unicode(self.last_name)


class SecurityQuestion(models.Model):
    user        = models.OneToOneField(UserAccount, unique = True, null = True)
    question    = models.CharField(max_length = 100, null=True, blank=True)
    answer      = models.CharField(max_length = 250, null=True, blank=True)
    created     = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        verbose_name_plural = 'Security Questions'


class UserSpecialRate(models.Model):
    user                    = models.ForeignKey(User)
    origin                  = models.CharField(max_length = 100)
    destination             = models.CharField(max_length = 100)
    rate_per_lb_D           = models.FloatField(default = 0)
    #direction               = models.CharField(max_length = 100)
    freight_type            = models.CharField(max_length = 50, choices = SHIPPING_METHOD)

    created_by              = models.ForeignKey(User, related_name="created_by")
    created_on              = models.DateTimeField(default = timezone.now)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "User Special Rates"


class ActionHistory(models.Model):
    user            = models.ForeignKey(User, null=True)
    obj_id          = models.IntegerField(default=0)
    obj_model_name  = models.CharField(max_length = 100)
    action          = models.CharField(max_length=200, null=True)
    obj_description = models.CharField(max_length=1000, null=True)
    # item            = models.ForeignKey('export.ExportItem', null=True)
    # package         = models.ForeignKey('export.ExportPackage', null=True)
    # export          = models.ForeignKey('export.Export', null=True)
    created_on      = models.DateTimeField(default = timezone.now)

    #syncedStatus    = models.IntegerField(default = '0')
    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Action History'

    def __unicode__(self):
        return unicode(self.action)


class MessageCenter(models.Model):
    user                = models.ForeignKey(User, null=True)
    created_on          = models.DateTimeField(default = timezone.now)
    related_to          = models.CharField(max_length = 50, null=True)
    booking_ref         = models.CharField(max_length = 50)
    message             = models.TextField()
    no_of_comments      = models.IntegerField(default=0)

    new                 = models.BooleanField(default = True)
    replied             = models.BooleanField(default=False)
    replied_on          = models.DateTimeField(null = True)
    archive             = models.BooleanField(default=False)

    package             = models.ForeignKey('shipping.ShippingPackage', null=True)
    objects             = models.Manager()


    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        verbose_name_plural = 'Messages'


class MessageCenterComment(models.Model):
    user                    = models.ForeignKey(User, null=True)
    message                 = models.TextField()
    date                    = models.DateTimeField(default = timezone.now)
    message_obj             = models.ForeignKey(MessageCenter, null=True)

    def __unicode__(self):
        return unicode(self.user)


class AddressInfo(models.Model):
    user            = models.ForeignKey(User, null=True)

    title           = models.CharField(max_length=10, choices = TITLE)
    first_name      = models.CharField(max_length=100, null=True)
    last_name       = models.CharField(max_length=100, null=True)
    address_line1   = models.CharField(max_length=300, null=True)
    address_line2   = models.CharField(max_length=300, null=True)
    city            = models.CharField(max_length=100, null=True)
    state           = models.CharField(max_length=50,  null=True)
    country         = models.CharField(max_length=20,  null=True)#, choices = DELIVERY_COUNTRIES)
    telephone       = models.CharField(max_length=100, null=True)
    zip_code        = models.CharField(max_length=20,  null=True)
    created_on      = models.DateTimeField(default = timezone.now)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.user)

    def full_address(self):
        return "%s, %s, %s, %s, %s. %s" %(self.address_line1.title(), self.address_line2.title(), self.city.title(), self.state.title(), self.country.title(), self.telephone)

    def full_address_2(self):
        return "%s, %s, %s, %s, %s. %s" %(self.address_line1, self.address_line2, self.city, self.state, self.country, self.telephone)
    

    def get_receiver_name(self):
        return "%s %s, %s" %(self.title.title(), self.first_name.title(), self.last_name.title())



class AddressBook(AddressInfo):

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Addresses Book"



class JoinWaitingList(models.Model):
    #name  = models.CharField(max_length=100, null=True, blank=True)
    email          = models.EmailField()
    joined_on      = models.DateTimeField(default = timezone.now)

    def __unicode__(self):
        return str(self.email)



