# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from datetime import datetime, date
import pytz
from astral import Astral
import re
from django.utils import timezone
from general.modelfield_choices import STATE, COUNTRY, DELIVERY_COUNTRIES, CURRENCY, SHIPPING_METHOD, MARKETER_COUNTRIES
from service_provider.models import MarketingMember, Subscriber



lb_kg_factor = 0.45359

def not_less_than_today(expiry_date):
    if expiry_date < date.today():
        raise ValidationError(u"%s is a date in the past. Choose a date greater than or equal to today's date" %expiry_date)

def costcalc_settings():
    cost_settings = CostCalcSettings.objects.get(pk = 1)
    return cost_settings

# def costcalc_settings(pk):
#     cost_settings = CostCalcSettings.objects.get(pk = pk)
#     return cost_settings

def newFedExShippingCosts(maxShippingWeight_kg, exchange_rate):#, dvm=None):
    new_fedex_data = NewFedExLocalFreightSettings.objects.get(pk = 1)
    return new_fedex_data.localShippingCharges(maxShippingWeight_kg, exchange_rate)


class BoxBase1(models.Model):
    box_name        = models.CharField(max_length = 50)
    box_length      = models.DecimalField(max_digits = 5, decimal_places = 1)
    box_width       = models.DecimalField(max_digits = 5, decimal_places = 1)
    box_height      = models.DecimalField(max_digits = 5, decimal_places = 1)
    box_weight      = models.DecimalField(max_digits = 5, decimal_places = 1)

    class Meta:
        abstract = True

    def lb_kg_factor(self):
        #costcalc_settings()
        return 0.45359
        #return float(costcalc_settings().lb_kg_factor)

    def box_weight_K(self):
        return round(float(self.box_weight) * self.lb_kg_factor(), 2)


class BatchTypeManager(models.Manager):
    def __init__(self, active, archive, *args, **kwargs):
        super(BatchTypeManager, self).__init__(*args, **kwargs)
        self.active = active
        self.archive = archive

    def get_queryset(self):
        return super(BatchTypeManager, self).get_queryset().filter(Q(active = self.active), Q(archive = self.archive))

    def active_batches(self):
        return super(BatchTypeManager, self).get_queryset().filter(Q(active = self.active))

    def archive_batches(self):
        return super(BatchTypeManager, self).get_queryset().filter(Q(archive = self.archive))

    def last_two_batches(self):
        return [ batch.batch_info() for batch in self.active_batches()[:2] ]


BATCH_STATUS = (
    ('New', 'New'),
    ('Processing', 'Processing'),
    ('Archive', 'Archive'),
    ('ProcessingForDelivery', 'Processing for delivery'),
    ('ClearingCustoms', 'Clearing customs'),
    ('Departed', 'Departed'),
    ('DeliveredToCarrier', 'Delivered to carrier'),
    ('Cancel', 'Cancel'),
)

BATCH_TYPE = (
    ('USA-NGA', 'USA-NGA'),
    ('NGA-USA', 'NGA-USA'),
)

class Batch(models.Model):
    subscriber      = models.ForeignKey(Subscriber, null=True, blank=True)
    shipping_method = models.CharField(max_length=50, default="Air Cargo")
    carrier         = models.CharField(max_length=50, null=True, blank=True)

    awb_doc         = models.FileField(upload_to="awb_doc", null=True, blank=True)
    bol_doc         = models.FileField(upload_to="bol_doc", null=True, blank=True)

    batch_number    = models.CharField(max_length=24, null=True, blank=True)

    port_of_exit    = models.CharField(max_length=50, null=True, blank=True)
    port_of_arrival = models.CharField(max_length=50, null=True, blank=True)
    booking_ref     = models.CharField(max_length=50, null=True, blank=True)
    departure_date  = models.CharField(max_length=50, null=True, blank=True)
    arrival_date    = models.CharField(max_length=50, null=True, blank=True)
    notes1          = models.TextField(null=True, blank=True)
    created_on      = models.DateTimeField(default = timezone.now)

    status          = models.CharField(max_length = 25, default='new')
    batch_type      = models.CharField(max_length = 150, null=True, blank=True)
    #shipment_status = models.CharField(max_length=50, null=True, blank=True)

    freight_type    = models.CharField(max_length=50, null=True, blank=True)
    awb             = models.CharField(max_length=50, null=True, blank=True)
    bol             = models.CharField(max_length=50, null=True, blank=True)
    #total_weight_P    = models.FloatField(max_length=50, default = '0')
    #total_weight_K    = models.FloatField(max_length=50, default = '0' )
    #total_value      = models.FloatField(max_length=50, default = '0')
    #total_value_N    = models.FloatField(max_length=50, default = '0')
    #pkg_count        = models.IntegerField(max_length = 10, default='0')
    total_pellets    = models.CharField(max_length=50, null=True, blank=True)
    shipping_cost_D   = models.FloatField(max_length=50, default=0)
    shipping_cost_N   = models.FloatField(max_length=50,default=0)
    clearing_cost   = models.FloatField(max_length=50, default=0)
    clearing_cost_N   = models.FloatField(max_length=50, default=0)
    harzmat_status  = models.CharField(max_length=50, null=True, blank=True)
    notes2          = models.TextField(null=True, blank=True)
    last_update     = models.CharField(max_length=50, null=True)

    expires_on      = models.DateTimeField(null=True)
    eta             = models.IntegerField(null=True)

    total_weight_P  = models.FloatField(max_length = 10, default = 0.0)
    total_weight_P_K  = models.FloatField(max_length = 10, default = 0.0)

    pkg_count       = models.IntegerField(default = 0)

    total_value     = models.FloatField(max_length=10, default=0.0)
    total_value_bool = models.BooleanField(default=False)

    objects         = models.Manager()

    deleted         = models.BooleanField(default=False)
    # marketer_batches = models.ForeignKey(MarketingMember, null=True, blank=True)

    rank            = models.CharField(max_length=30, null=True,blank=True)
    #objects         = ReverseManager({'batch_status': 'batchedithistory_set', 'shipment': 'shipment_set'})

    active_batches = BatchTypeManager(True, False)
    archive_batches = BatchTypeManager(False, True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Batches"

    # def save(self):
    #     #self.total_value = self.total_value_custom() + self.total_value_CA
    #     self.total_value = self.total_value_shipping() + self.total_value_shopping()#self.total_value_CA
    #     self.total_weight_P = self.total_weight_P_custom() #+ self.total_weight_P_CA
    #     self.total_weight_P_K = self.total_weight_P * lb_kg_factor#costcalc_settings().lb_kg_factor
    #     self.pkg_count = self.pkg_count_custom() #+ self.pkg_count_CA
    #     super(Batch, self).save()

    def created_on_date(self):
        created_on = str(self.created_on.date())
        return datetime.strptime(created_on, "%Y-%m-%d").strftime("%d/%m/%Y")

    def total_weight_P_custom(self):
        #print self.shipmentpackage_set.filter(Q(deleted = False), Q(approved=True))
        # if self.batch_type == "export":
        #     shipping_boxes_TotalWeight = self.exportpackage_set.filter(Q(deleted = False), Q(approved=True)).aggregate(Sum('box_weight'))['box_weight__sum']
        # elif self.batch_type == "import":
        #     shipping_boxes_TotalWeight = self.importpackage_set.filter(Q(deleted = False) , Q(approved = True)).aggregate(Sum('box_weight'))['box_weight__sum']
        shipping_boxes_TotalWeight = self.shippingpackage_set.filter(Q(deleted = False) , Q(approved = True)).aggregate(Sum('box_weight'))['box_weight__sum']

        #print "shpping_boxes_TotalWeight: "+shipping_boxes_TotalWeight
        #print "shopping_boxes_TotalWeight: "+shopping_boxes_TotalWeight
        #shipping_boxes_TotalWeight = self.shipmentpackage_set.filter(Q(deleted = False) , Q(box_weight__isnull = False)).aggregate(Sum('box_weight'))['box_weight__sum']
        #shopping_boxes_TotalWeight = self.orderpackage_set.filter(Q(deleted = False) , Q(box_weight__isnull = False)).aggregate(Sum('box_weight'))['box_weight__sum']

        if shipping_boxes_TotalWeight == None:
            shipping_boxes_TotalWeight = 0

        total_weight = shipping_boxes_TotalWeight
        if total_weight <= 0:
            return 0
        return float(total_weight)

        #for package in packages:
        #    if package.box_weight is not None:
        #        total_weight += package.box_weight
        #    else:
        #        total_weight += package.item_weight
        #return float(total_weight)


        #for package in packages:
        #    if package.box_weight is not None:
        #        total_weight += package.box_weight
        #    else:
        #        total_weight += package.item_weight
        #return float(total_weight)

    def total_weight_P_custom_K(self):
        return self.total_weight_P_custom() * lb_kg_factor#costcalc_settings().lb_kg_factor

    def total_weight_K(self):
        #return self.total_weight_P() * costcalc_settings().pound_kilo_factor
        if self.total_weight_P == None:
            return 0
        return self.total_weight_P * lb_kg_factor#costcalc_settings().lb_kg_factor

    #def total_value_custom(self):
    #    #packages = self.packagedimension_set.all.values_list('id', flat=True)
    #    #linkedItems_totalValue = Packageinfo.objects.filter(Q(pk__in = packages), Q(deleted = False)).aggregate(Sum('total_value'))
    #    #if linkedItems_totalValue['total_value__sum'] <= 0:
    #    #    return 0
    #    #return linkedItems_totalValue['total_value__sum']
    #    assignedPackageItemstotalValue = self.packagedimension_set.all().aggregate(Sum('linkedItems_totalValue'))
    #    if assignedPackageItemstotalValue['linkedItems_totalValue__sum'] == None :#or assignedPackageItemstotalValue['linkedItems_totalValue__sum'] <= 0:
    #        return 0
    #    return assignedPackageItemstotalValue['linkedItems_totalValue__sum']

    def new_total_value_payable_D(self):
        assignesPackagesToBatch = self.shippingpackage_set.all().aggregate(Sum('admin_total_payable_D'))
        if assignesPackagesToBatch['admin_total_payable_D__sum'] == None:
            return 0
        # if self.batch_type == "import":
        #     assignesPackagesToBatch = self.importpackage_set.all().aggregate(Sum('admin_total_payable_D'))
        #     if assignesPackagesToBatch['admin_total_payable_D__sum'] == None:
        #         return 0
        # elif self.batch_type == 'export':
        #     assignesPackagesToBatch = self.exportpackage_set.all().aggregate(Sum('admin_total_payable_D'))
        #     if assignesPackagesToBatch['admin_total_payable_D__sum'] == None:
        #         return 0
        return assignesPackagesToBatch['admin_total_payable_D__sum']

    def new_total_value_payable_N(self):
        assignesPackagesToBatch = self.shippingpackage_set.all().aggregate(Sum('admin_total_payable_N'))
        if assignesPackagesToBatch['admin_total_payable_N__sum'] == None:
            return 0
        # if self.batch_type == "import":
        #     assignesPackagesToBatch = self.importpackage_set.all().aggregate(Sum('admin_total_payable_N'))
        #     if assignesPackagesToBatch['admin_total_payable_N__sum'] == None:
        #         return 0
        # elif self.batch_type == 'export':
        #     assignesPackagesToBatch = self.exportpackage_set.all().aggregate(Sum('admin_total_payable_N'))
        #     if assignesPackagesToBatch['admin_total_payable_N__sum'] == None:
        #         return 0
        return assignesPackagesToBatch['admin_total_payable_N__sum']


    def total_value_shipping(self):
        assignedPackageItemstotalValue = self.shipmentpackage_set.all().aggregate(Sum('linkedItems_totalValue'))
        if assignedPackageItemstotalValue['linkedItems_totalValue__sum'] == None :#or assignedPackageItemstotalValue['linkedItems_totalValue__sum'] <= 0:
            return 0
        return assignedPackageItemstotalValue['linkedItems_totalValue__sum']

    def total_value_shopping(self):
        assignedPackageItemstotalValue = self.orderpackage_set.all().aggregate(Sum('linkedItems_totalValue'))
        if assignedPackageItemstotalValue['linkedItems_totalValue__sum'] == None :#or assignedPackageItemstotalValue['linkedItems_totalValue__sum'] <= 0:
            return 0
        return assignedPackageItemstotalValue['linkedItems_totalValue__sum']


    def total_value_N(self):
        return float(self.total_value) * dollar_naira_rate#costcalc_settings().dollar_naira_rate
        #return float(self.total_value()) * costcalc_settings().dollar_naira_rate

    def get_packages_in_batch(self):
        pkgs = self.shippingpackage_set.filter(deleted=False, approved=True)
        # if self.batch_type == "import":
        #     pkgs = self.importpackage_set.filter(deleted=False, approved=True)
        # else:
        #     pkgs = self.exportpackage_set.filter(deleted=False, approved=True)
        return pkgs

    def pkg_count_custom(self):
        pkg = self.shippingpackage_set.filter(deleted = False, approved = True).count()
        # if self.batch_type == "import":
        #     pkg = self.importpackage_set.filter(deleted = False, approved = True).count()
        # else:
        #     pkg = self.exportpackage_set.filter(deleted = False, approved = True).count()
        return pkg
        # shipping_boxes = self.shipmentpackage_set.filter(deleted = False, approved = True).count()
        # shopping_boxes = self.orderpackage_set.filter(deleted = False, approved = True).count()
        # return shipping_boxes + shopping_boxes


    def shipping_box_count(self):
        return self.batchshippingbox_set.all().count()

    def before_shippingboxes(self):
        return self.created_on >= timezone.make_aware(datetime(2014,9,01,00,00,00), timezone.get_default_timezone())

    def __unicode__(self):
        return '%s - %s' %(self.batch_type, self.carrier)

    def batch_info(self):
        return {'batch_id': self.pk, 'carrier': self.carrier, 'shipping_method': self.freight_type,#self.shipping_method,
                'shipping_boxes': [ box.as_dict() for box in self.batchshippingbox_set.all()]}#,
                   # 'created_on': self.created_on_date()}

    def batch_info_v1(self):
        return {'batch_id': self.pk, 'carrier': self.carrier, 'shipping_method': self.shipping_method,
                'shipping_boxes': [ box.as_dict() for box in self.batchshippingbox_set.all()],
                   'created_on': self.created_on_date()}

    #def batch_info_v1(self):
    #    #new_dict = self.batch_info().update({'created_on': self.created_on_date()})
    #   # return new_dict
    #    old_dict = self.batch_info()
    #    new_dict = dict()
    #    for key, val in old_dict.iteritems():
    #        new_dict[key] = val
    #
    #    #print new_dict
    #    return new_dict.update({'created_on': self.created_on_date()})
    #    return new_dict


class BatchEditHistory(models.Model):
    user            = models.ForeignKey(User)
    batch           = models.ForeignKey(Batch)
    batch_status    = models.CharField(max_length=50, null=True, blank=True)
    updated_on      = models.DateTimeField(null=True)
    eta             = models.IntegerField(null=True)
    created_on      = models.DateTimeField(default = timezone.now)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Batch Status History'
    def __unicode__(self):
        return self.batch.carrier


class BaseCostCalcSettings(models.Model):
    dim_weight_factor       = models.FloatField(max_length = 10, default = 164)
    lb_kg_factor            = models.FloatField(max_length = 10, default = 0.45359)
    kg_lb_factor            = models.FloatField(max_length = 10, default = 2.20462)

    #dollar_naira_rate       = models.FloatField(max_length = 10, default = 239.00)
    dollar_exchange_rate    = models.FloatField(max_length = 10, default = 239.00)

    pound_naira_rate        = models.FloatField(max_length = 10, default = 300.00)

    vat_rate                = models.FloatField(max_length = 10, default = 5)
    vat_rate_1                = models.FloatField(max_length = 10, default = 20)

    insurance_rate          = models.FloatField(max_length = 10, default = 6)
    consolidation_fee       = models.FloatField(max_length = 10, default = 15.00)

    #New Pricing Structure for Service Charge (January 2014)
    sc1_percentage          = models.FloatField(max_length = 10, default = 10.00)
    sc_dollar_rate_1        = models.FloatField(max_length = 10, default = 5.00)
    sc_dollar_rate_2        = models.FloatField(max_length = 10, default = 1.00)
    sc_dollar_rate_3        = models.FloatField(max_length = 10, default = 0.75)

    #consolidation_fee_fixed     = models.FloatField(max_length = 10, default = 15.00)

    unit_strip_package_fee      = models.FloatField(max_length = 10, default = 1.00)

    #New Pricing Structure for Service Charge (1 Oct 2014) start
    order_TPC_1             = models.FloatField(max_length = 10, default = 250.00)
    order_TPC_2             = models.FloatField(max_length = 10, default = 500.00)
    order_TPC_3             = models.FloatField(max_length = 10, default = 1000.00)
    order_TPC_4             = models.FloatField(max_length = 10, default = 5000.00)

    service_charge_min_fee  = models.FloatField(max_length = 10, default = 12.00)
    handling_charge_fee     = models.FloatField(max_length = 10, default = 5.00)

    service_charge_rate_1   = models.FloatField(max_length = 10, default = 7.00)
    service_charge_rate_2   = models.FloatField(max_length = 10, default = 6.50)
    service_charge_rate_3   = models.FloatField(max_length = 10, default = 6.00)
    service_charge_rate_4   = models.FloatField(max_length = 10, default = 5.50)
    service_charge_rate_5   = models.FloatField(max_length = 10, default = 5.00)
    #New Pricing Structure for Service Charge (1 Oct 2014) end

    #changed strip_package_fee to minimum_strip_package_fee
    strip_package_fee_min   = models.FloatField(max_length = 10, default = 5.00)

    #a_f_o_p_rate                = models.FloatField(max_length = 10, default = 0.00)
    #a_f_a_p_rate                = models.FloatField(max_length = 10, default = 105.00)
    #a_f_w_l_rate                = models.FloatField(max_length = 10, default = 1.50)
    #a_f_a_l_rate                = models.FloatField(max_length = 10, default = 2.50)
    #s_f_o_p_rate                = models.FloatField(max_length = 10, default = 0.00)
    #s_f_a_p_rate                = models.FloatField(max_length = 10, default = 1.00)
    #s_f_w_l_rate                = models.FloatField(max_length = 10, default = 1.50)
    #s_f_a_l_rate                = models.FloatField(max_length = 10, default = 2.50)

    #o_p_minimum_fee             = models.FloatField(max_length = 10, default = 8.00)
    #w_l_minimum_fee             = models.FloatField(max_length = 10, default = 5.00)
    #a_l_minimum_fee             = models.FloatField(max_length = 10, default = 20.00)

    #New minimum fee for Express Air International Freight
    expressAir_min_fee              = models.FloatField(max_length = 10, default = 50.00)

    pickup_in_lag_rate      = models.FloatField(max_length = 10, default = 0.00)
    pickup_out_lag_rate     = models.FloatField(max_length = 10, default = 1.00)
    deliv_in_lag_rate       = models.FloatField(max_length = 10, default = 1.50)
    deliv_out_lag_rate      = models.FloatField(max_length = 10, default = 2.50)

    pickup_in_lag_min_fee   = models.FloatField(max_length = 10, default = 0.00)
    pickup_out_lag_min_fee  = models.FloatField(max_length = 10, default = 8.00)
    deliv_in_lag_min_fee    = models.FloatField(max_length = 10, default = 5.00)
    deliv_out_lag_min_fee   = models.FloatField(max_length = 10, default = 20.00)

    is_promo_on             = models.BooleanField(default = False)

    # #US
    # unit_cost_air_freight_1     = models.FloatField(max_length = 10, default = 4.50)
    # unit_cost_air_freight_2     = models.FloatField(max_length = 10, default = 4.20)
    # unit_cost_air_freight_3     = models.FloatField(max_length = 10, default = 4.00)
    # unit_cost_air_freight_4     = models.FloatField(max_length = 10, default = 3.80)
    # unit_cost_air_freight_5     = models.FloatField(max_length = 10, default = 3.60)
    #
    # #Export
    # unit_cost_export_air_freight_1     = models.FloatField(max_length = 5, default = 2.50)
    # unit_cost_export_air_freight_2     = models.FloatField(max_length = 5, default = 3.00)
    # unit_cost_export_air_freight_3     = models.FloatField(max_length = 5, default = 3.50)
    # unit_cost_export_air_freight_4     = models.FloatField(max_length = 5, default = 4.00)
    # unit_cost_export_air_freight_5     = models.FloatField(max_length = 5, default = 4.50)

    export_insurance_rate               = models.FloatField(max_length = 10, default = 2)
    export_consolidation_rate           = models.FloatField(max_length = 10, default = 5)
    export_min_shipping_charge          = models.FloatField(max_length = 5, default = 6)

    flat_cost_air_freight       = models.FloatField(max_length = 10, default = 3.60)

    #UK
    # unit_cost_air_freight_11     = models.FloatField(max_length = 10, default = 4.5)
    # unit_cost_air_freight_21     = models.FloatField(max_length = 10, default = 4.0)
    # unit_cost_air_freight_31     = models.FloatField(max_length = 10, default = 3.2)
    # unit_cost_air_freight_41     = models.FloatField(max_length = 10, default = 2.9)
    # unit_cost_air_freight_51     = models.FloatField(max_length = 10, default = 2.7)
    #
    # unit_cost_sea_freight_1     = models.FloatField(max_length = 10, default = 2.00)
    # unit_cost_sea_freight_2     = models.FloatField(max_length = 10, default = 1.80)
    # unit_cost_sea_freight_3     = models.FloatField(max_length = 10, default = 1.60)
    # unit_cost_sea_freight_4     = models.FloatField(max_length = 10, default = 1.40)
    # unit_cost_sea_freight_5     = models.FloatField(max_length = 10, default = 1.20)

    #New Demurrage variables
    demurrage_rate          = models.FloatField(max_length = 10, default = 0.10)
    demurrage_grace_period  = models.IntegerField(default = 7)
    #New demurrage limit
    #demurrage_limit             = models.IntegerField(max_length = 10, default = 7)

    min_shipping_bal            = models.FloatField(max_length = 10, default = 20)
    vip_min_shipping_bal        = models.FloatField(max_length = 10, default = 200)

    kwd_val_percentage      = models.FloatField(max_length = 5, default = 20)

    customs_clearing_fee = models.FloatField(max_length = 10, default = 1040)

    shipping_weight_threshold = models.FloatField(max_length = 5, default = 10)

    cost_markup         = models.FloatField(max_length = 10, default = 30.00) #%markup

    currency              =     models.CharField(max_length = 20, choices=CURRENCY)

    country   =   models.CharField(max_length = 20, choices=MARKETER_COUNTRIES)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "$%s" %self.dollar_exchange_rate



class CostCalcSettings(BaseCostCalcSettings):

    marketer    =    models.ForeignKey('service_provider.MarketingMember', null=True, blank=True)

    def __unicode__(self):
        return "$%s" %self.dollar_exchange_rate

    class Meta:
        verbose_name_plural = "Cost Calc Settings"

#to avoid makemigrations error
try:
    dollar_naira_rate = costcalc_settings().dollar_naira_rate
    lb_kg_factor = 0.45359
except:
    pass

class ExportObjCostCalcSettings(BaseCostCalcSettings):

    class Meta:
        verbose_name_plural = "Export Cost Calc Records"



FEDEX_ZONES = (
    ('LagosIntra-City', 'LagosIntra-City'),
    ('West', 'West'),
    ('East', 'East'),
    ('North', 'North'),
    ('FarEast', 'FarEast'),
    ('FarNorth', 'FarNorth'),
)

class NewFedExLocalFreightSettings(models.Model):
    #Based on FedEx agreement with Sokohali Ltd.
    #All costs are in Nigerian Naira
    #zone                = models.CharField(max_length = 20, choices = FEDEX_ZONES)

    within_500g_3kg_in_lag_rate    = models.FloatField(max_length = 5, default = 600)#0.5 - 3kg rate
    extra_kg_in_lag_rate       = models.FloatField(max_length = 5, default = 150)

    within_500g_3kg_out_lag_rate    = models.FloatField(max_length = 5, default = 2000)#0.5 - 3kg rate
    extra_kg_out_lag_rate       = models.FloatField(max_length = 5, default = 250)

    shippyme_markup             = models.FloatField(max_length = 10, default = 30.00) #%markup
    #handling_charge             = models.FloatField(max_length = 5, default = 500)
    #hd_extra_charge             = models.FloatField(max_length = 5, default = 500)
    #use_fedex                   = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural     = "New FedEx Local Freight Cost Settings"

    #def __unicode__(self):
    #    return self.zone

    def dollarNairaRate(self):
        #costcalc_settings()
        return float(dollar_naira_rate)
        #return float(costcalc_settings().dollar_naira_rate)

    def localShippingCharges(self, shippingWeight_kg, exchange_rate):
        #dollarNairaRate = self.dollarNairaRate()

        markup = float(self.shippyme_markup)/100
        if shippingWeight_kg > 3:
            extraChargeableWeight = shippingWeight_kg - 3
            AP_ShippingCharge_N = self.within_500g_3kg_out_lag_rate + (extraChargeableWeight * self.extra_kg_out_lag_rate)
            AP_ShippingCharge_D = float(AP_ShippingCharge_N) / exchange_rate

            inLagRate = self.within_500g_3kg_in_lag_rate + (extraChargeableWeight * self.extra_kg_in_lag_rate)
            WL_ShippingCharge_N = inLagRate + (markup * inLagRate)
            WL_ShippingCharge_D =  float(WL_ShippingCharge_N) / exchange_rate

            AL_ShippingCharge_N = AP_ShippingCharge_N + (markup * AP_ShippingCharge_N)
            AL_ShippingCharge_D = float(AL_ShippingCharge_N) / exchange_rate

            return AP_ShippingCharge_D, AP_ShippingCharge_N, WL_ShippingCharge_D, WL_ShippingCharge_N, AL_ShippingCharge_D, AL_ShippingCharge_N
        else:
            AP_ShippingCharge_N = self.within_500g_3kg_out_lag_rate
            AP_ShippingCharge_D = float(AP_ShippingCharge_N) / exchange_rate

            inLagHomeDelivery_markUp = markup * self.within_500g_3kg_in_lag_rate
            WL_ShippingCharge_N = self.within_500g_3kg_in_lag_rate  + inLagHomeDelivery_markUp
            WL_ShippingCharge_D =  float(WL_ShippingCharge_N) / exchange_rate

            outLagHomeDelivery_markUp = markup * self.within_500g_3kg_out_lag_rate
            AL_ShippingCharge_N = self.within_500g_3kg_out_lag_rate  + outLagHomeDelivery_markUp
            AL_ShippingCharge_D = float(AL_ShippingCharge_N) / exchange_rate

            return AP_ShippingCharge_D, AP_ShippingCharge_N, WL_ShippingCharge_D, WL_ShippingCharge_N, AL_ShippingCharge_D, AL_ShippingCharge_N




class DeliveryLocation(models.Model):
    address         = models.CharField(max_length=500, null=True)
    town_area       = models.CharField(max_length=500, null=True)
    city            = models.CharField(max_length=500, null=True)
    #state           = models.CharField(max_length=50)
    telephone       = models.CharField(max_length=50, null=True, blank=True)
    #state           = models.CharField(max_length=50)
    country         = models.CharField(max_length=15, default = "Nigeria", choices = DELIVERY_COUNTRIES)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s - %s' %(self.city, self.state)

    def full_address(self):
        return "%s %s %s, %s, %s." %(self.address, self.town_area, self.city, self.state, self.country)




class FedExLocation(DeliveryLocation):
    # address         = models.CharField(max_length=500, null=True)
    # town_area       = models.CharField(max_length=500, null=True)
    # city            = models.CharField(max_length=500, null=True)
    # telephone       = models.CharField(max_length=50, null=True, blank=True)
    state           = models.CharField(max_length=50, choices=STATE)
    # country         = models.CharField(max_length=15, default = "Nigeria", choices = COUNTRY)
    # #zone            = models.ForeignKey(NewFedExLocalFreightSettings, null=True)
    #country         = models.CharField(max_length=15, default = "Nigeria", choices = COUNTRY)
    zone            = models.CharField(max_length=20, default="", choices = FEDEX_ZONES)

    class Meta:
        ordering = ["state"]
        verbose_name_plural = "FedEx Locations"


    # def __unicode__(self):
    #     return '%s - %s' %(self.city, self.state)



def cityDateTime(city_name):
    a = Astral()
    city = a[city_name]
    zoneName = city.timezone
    currentTime = datetime.now(pytz.timezone(zoneName))
    return currentTime


class HomePageBkgdCity(models.Model):
    city = models.CharField(max_length = 20)
    bkgd_image = models.ImageField(upload_to='HomePageBkgdCity')

    class Meta:
        verbose_name_plural = "Home Page Background City"

    def __unicode__(self):
        return "%s - %s" %(self.city, str(self.cityCurrentDateTime()))

    def cityCurrentDateTime(self):
        try:
            return cityDateTime(self.city)
        except:
            return datetime.now()

    def cityDateTimeHrsDiff(self):
        return self.cityCurrentDateTime().hour - datetime.now().hour

ACTIVE = 'active'
INACTIVE = 'inactive'

COUNTRY_STATUS = (
    ('', 'Select status'),
    (ACTIVE, 'Active'),
    (INACTIVE, 'Inactive')
)

class OperatingCountry(models.Model):
    country         = models.CharField(max_length = 30)
    currency_symbol = models.CharField(max_length = 1)
    currency_rep    = models.CharField(max_length = 20)
    address         = models.CharField(max_length = 300, default = "")
    delivery_address= models.CharField(max_length = 300, default = "")
    status          = models.CharField(max_length = 20, choices = COUNTRY_STATUS)
    logo            = models.ImageField(upload_to="OperatingCountry", null=True)
    full_country_name = models.CharField(max_length= 30, default="")

    def save(self, *args, **kwargs):
        self.country = self.country.lower()
        super(OperatingCountry, self).save(*args, **kwargs)


    def __unicode__(self):
        return "%s - %s" %(self.country, self.currency_symbol)


    def country_active(self):
        if self.status == ACTIVE:
            return True
        return False

    def country_abbr(self):
        if self.country == "us":
            return "usa"
        return self.country


    class Meta:
        verbose_name_plural = "Operating Countries"


class AllButOtherBox(models.Manager):
    def get_queryset(self):
        return super(AllButOtherBox, self).get_queryset().exclude(box_name = "Other")

class PreDefinedBoxes(BoxBase1):
    #box_name        = models.CharField(max_length = 50)
    #box_length      = models.DecimalField(max_digits = 5, decimal_places = 1)
    #box_width       = models.DecimalField(max_digits = 5, decimal_places = 1)
    #box_height      = models.DecimalField(max_digits = 5, decimal_places = 1)
    #box_weight      = models.DecimalField(max_digits = 5, decimal_places = 1)

    description    = models.CharField(max_length=50, default = "item")
    quantity       = models.CharField(max_length=5, default = "1")

    # description2    = models.CharField(max_length=50, null=True, blank=True)
    # quantity2       = models.CharField(max_length=5, blank=True, null=True)
    #
    # description3    = models.CharField(max_length=50, null=True, blank=True)
    # quantity3       = models.CharField(max_length=5, blank=True, null=True)
    #
    # description4    = models.CharField(max_length=50, null=True, blank=True)
    # quantity4       = models.CharField(max_length=5, blank=True, null=True)
    usage_count     = models.IntegerField(default=0)

    objects_all     = models.Manager()

    objects         = AllButOtherBox()

    def __unicode__(self):
        return '%s - %slbs' %(self.box_name, self.box_weight)

    def box_description(self):
        desc = str(self.quantity) + " " + self.description #+ " " + str(self.quantity2) + " " + self.description2 + " " + str(self.quantity3) + " " + self.description3 + " " + str(self.quantity4) + " " + self.description4
        return desc.strip()

    def min_weight(self):
        if self.box_weight < 1:
            return 1
        return self.box_weight

    def min_weight_K(self):
        round(float(self.min_weight()) * self.lb_kg_factor(), 2)

    class Meta:
        verbose_name_plural = "Pre-Defined Boxes"
        ordering = ["box_name"]

class KeywordBase(models.Model):

    def keyword_list_1(self):
        keywords = str(self.keywords).lower()
        newk = keywords.split(',')
        return [k.strip() for k in newk]

    def keyword_list_2(self):
        keywords = str(self.keywords).lower()
        return re.findall('\w+', keywords) #this turns "dress-shoes, "baker" to ["dress", "shoes", "baker"]

    def sorted_keywords_list(self, detector_or_mgr=None):
        #keywords = self.keyword_list()
        #for keyword detector in order/shipment placement
        if detector_or_mgr == None:
            #keywords = self.keyword_list_2()
            keywords = self.keyword_list_1()
        else:
        #for keyword detector in keyword manager
            keywords = self.keyword_list_1()
        keywords.sort()
        #print "keywords: ", keywords
        return keywords

    class Meta:
        abstract = True

#class ShippingKeyword(models.Model):
class ShippingKeyword(KeywordBase):
    category       = models.CharField(max_length=50)
    keywords       = models.TextField()
    shipping_box   = models.ForeignKey(PreDefinedBoxes)


    class Meta:
        ordering = ["category"]

    # def __unicode__(self):
    #     return unicode(self.category)
    #
    # def keyword_list(self):
    #     keywords = str(self.keywords).lower()
    #     newk = keywords.split(',')
    #     return [k.strip() for k in newk]
    #
    # def sorted_keywords_list(self, kwd_mgr):
    #     print kwd_mgr
    #     keywords = self.keyword_list()
    #     keywords.sort()
    #     return keywords


#class SubCategory(models.Model):
class SubCategory(KeywordBase):
    name = models.CharField(max_length=50)
    keywords = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=7, decimal_places=2)
    Category = models.ForeignKey(ShippingKeyword, related_name='categories', null=True)

    def __unicode__(self):
        return self.name

    # def keyword_list(self):
    #     keywords = str(self.keywords).lower()
    #     newk = keywords.split(',')
    #     return [k.strip() for k in newk]
    #
    # def sorted_keywords_list(self):
    #     keywords = self.keyword_list()
    #     keywords.sort()
    #     return keywords

    class Meta:
        unique_together = [("name")]
        verbose_name_plural = "SubCategory"


class AirwayBill(models.Model):
    batch_airwaybill                        = models.ForeignKey(Batch,null=True, blank=True)
    batch                                   = models.CharField(max_length = 100,null=True, blank=True)
    shippers_name_and_address               = models.CharField(max_length = 100,null=True, blank=True)
    shippers_number                         = models.IntegerField(null=True, blank=True)
    shippers_acct_no                        = models.CharField(max_length = 100,null=True, blank=True)
    consignees_name_and_address             = models.CharField(max_length = 100,null=True, blank=True)
    consignees_number                       = models.IntegerField(null=True, blank=True)
    consignees_acct_no                      = models.CharField(max_length = 100,null=True, blank=True)
    carrier_agent_name_and_city             = models.CharField(max_length = 100,null=True, blank=True)
    carrier_agent_iata_code                 = models.CharField(max_length = 100, null=True, blank=True)
    agent_acct_no                           = models.IntegerField(null=True, blank=True)
    airport_of_departure                    = models.CharField(max_length = 100, null=True, blank=True)
    origin_routing_code                     = models.CharField(max_length = 100, null=True, blank=True)
    origin_airline_carrier                  = models.CharField(max_length = 100, null=True, blank=True)
    destination_and_departure_routing_code1 = models.CharField(max_length = 100, null=True, blank=True)
    second_airline_carrier                  = models.CharField(max_length = 100, null=True, blank=True)
    state_of_destination                    = models.CharField(max_length = 100, null=True, blank=True)
    third_airline_carrier                   = models.CharField(max_length = 100, null=True, blank=True)
    airport_of_destination                  = models.CharField(max_length = 100, null=True, blank=True)
    requested_flight_and_date1              = models.CharField(max_length = 100, null=True, blank=True)
    requested_flight_and_date2              = models.CharField(max_length = 100, null=True, blank=True)
    handling_info                           = models.CharField(max_length = 100, null=True, blank=True)
    issued_airline_carrier_and_address      = models.CharField(max_length = 100, null=True, blank=True)
    accounting_info                         = models.CharField(max_length = 100, null=True, blank=True)
    ref_number                              = models.CharField(max_length = 100, null=True, blank=True)
    currency_code                           = models.CharField(max_length = 100, null=True, blank=True)
    value_for_carriage                      = models.CharField(max_length = 100, null=True, blank=True)
    value_for_custom                        = models.CharField(max_length = 100, null=True, blank=True)
    amount_of_insurance                     = models.IntegerField(null=True, blank=True)
    number_of_pieces_to_ship                = models.IntegerField(null=True, blank=True)
    gross_weight                            = models.IntegerField(null=True, blank=True)
    chargeable_rate                         = models.DecimalField(max_digits=20,decimal_places=2,null=True, blank=True)
    note_on_the_package                     = models.CharField(max_length = 200, null=True, blank=True)
    nature_and_quantity_of_goods            = models.CharField(max_length = 200, null=True, blank=True)
    regulation_of_goods                     = models.CharField(max_length = 100, null=True, blank=True)
    tracking_number_prefix                  = models.IntegerField(null=True, blank=True)
    airline_tracking_number                 = models.IntegerField(null=True, blank=True)
    other_charges_due_carrier               = models.DecimalField(max_digits=20,decimal_places=2,null=True, blank=True)
    total_prepaid                           = models.DecimalField(max_digits=20,decimal_places=2,null=True, blank=True)
    place_of_execution                      = models.CharField(max_length = 100, null=True, blank=True)
    shippers_name                           = models.CharField(max_length = 100, null=True, blank=True)
    carrier_name                            = models.CharField(max_length = 100, null=True, blank=True)
    created_on                              = models.DateField(default = timezone.now)

    class Meta:
        ordering = ['-created_on']
        # verbose_name_plural = "batches"

    def __unicode__(self):
        return unicode(self.batch)

    def weight_charge(self):
        return self.gross_weight * self.chargeable_rate


class NotifyUser(models.Model):
    user                = models.ForeignKey(User,null=True,blank=True)
    suite_no            = models.CharField(max_length = 150, null=True, blank=True)
    name                = models.CharField(max_length = 150, null=True, blank=True)
    address             = models.CharField(max_length = 250, null=True, blank=True)
    last_four_digits    = models.CharField(max_length = 50, null=True, blank=True)
    image_field         = models.ImageField(upload_to = "notifyUser-photo-id/%Y/%m/%d", null=True, blank=True)
    item_description    = models.CharField(max_length = 350, null=True, blank=True)
    created_on          = models.DateField(default = timezone.now)
    created_by          = models.CharField(max_length = 50, null=True, blank=True)
    weight              = models.DecimalField(max_digits=6, null=True, blank=True, decimal_places=2)
    status              = models.CharField(max_length = 50, default="Received")

    def __unicode__(self):
        return "%s  %s  %s" %(self.created_by, self.created_on, self.name)
    

class BatchPromo(models.Model):
    shipment_type               = models.CharField(max_length = 75)
    available_space             = models.CharField(max_length = 125)
    estimated_departure_time    = models.DateTimeField()
    current_rate                = models.FloatField(default = 0.0)
    origin                      = models.CharField(max_length = 125)
    destination                 = models.CharField(max_length = 125)
    weight_range_at_rate        = models.CharField(max_length = 125)
    start_date                  = models.DateTimeField(null = True)
    end_date                    = models.DateTimeField( null = True)
    is_active                   = models.BooleanField(default = False)

    def __unicode__(self):
        return '%s %s' %(self.shipment_type, self.is_active)


class Trucking(models.Model):
    job_number          = models.CharField(max_length=50, null=True, blank=True)
    cargo_decsription   = models.TextField(null=True, blank=True)
    created_on          = models.DateTimeField(default = timezone.now)
    created_by          = models.CharField(max_length=50,null=True, blank=True)
    done_by             = models.CharField(max_length=50,null=True, blank=True)
    actual_cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    total_cargo_weight  = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    bol_number          = models.CharField(max_length=50, null=True, blank=True)
    origin              = models.CharField(max_length=50, null=True, blank=True)
    destination         = models.CharField(max_length=50, null=True, blank=True)
    pick_up_time        = models.CharField(max_length=50, null=True, blank=True)
    drop_off_time       = models.CharField(max_length=50, null=True, blank=True)
    time_to_pick_up     = models.CharField(max_length=50, null=True, blank=True)
    time_to_drop_off    = models.CharField(max_length=50, null=True, blank=True)
    status              = models.CharField(max_length=20, null=True, blank=True, default="New")
    paid                = models.BooleanField(default = False)
    deleted             = models.BooleanField(default = False)
    archive             = models.BooleanField(default = False)
    bol_image           = models.ImageField(upload_to='BillofLaden', null=True, blank=True)


    class Meta:
        ordering = ['-created_on']

    def __unicode__(self):
        return '%s' %(self.job_number)
    







