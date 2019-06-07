from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from general.models import BasePackage, AddressInfo
from general.modelfield_choices import SENDING_METHOD, DELIVERY_COUNTRIES, DELIVERY_METHOD
from service_provider.models import ShippingChain, WarehouseMember, LocalDistributorLocation, MarketingMember, Direction,WarehouseLocation, LocalDistributionMember
from django.db.models import Q, Sum
# from model_utils import FieldTracker
from sokohaliAdmin.models import NotifyUser
# Create your models here.


class ShippingItem(Direction, models.Model):
    user                        = models.ForeignKey(User, null = True, blank=True)
    shipping_chain              = models.ForeignKey(ShippingChain, null=True, blank=True)
    created_on                  = models.DateTimeField(default = timezone.now)
    courier_tracking_number     = models.CharField(max_length = 500, blank=True, null = True)
    created_by                  = models.CharField(max_length = 500, blank=True, null = True)
    description                 = models.CharField(max_length = 500)
    quantity                    = models.IntegerField(default = 1)
    total_value                 = models.FloatField(max_length = 10, default="0")#In Dollars
    total_value_N               = models.FloatField(max_length = 10, default="0")#In Naira
    package                     = models.ForeignKey('ShippingPackage', null=True)
    marketer                     = models.ForeignKey(MarketingMember, null=True, blank=True)
    status                      = models.CharField(max_length=50, default="Not yet Received")
    status_2                    = models.CharField(max_length=50, default="New")
    deleted                     = models.BooleanField(default=False)
    ordered                     = models.BooleanField(default = False)
    created_by_admin            = models.BooleanField(default=False)
    item_type                   = models.CharField(max_length = 30, default='Regular')
    country                     = models.CharField(max_length = 10, null=True, blank=True)
    cat_num                     = models.CharField(max_length = 250, null=True, blank=True)
    weight                      = models.CharField(max_length = 250, null=True, blank=True)
    notify                      = models.OneToOneField(NotifyUser, null=True, blank=True)
    link                        = models.CharField(max_length = 500, null=True, blank=True)
    tag                         = models.CharField(max_length = 20, null=True, blank=True)
    amount_paid                 = models.FloatField(max_length = 10, default="0")#In Dollars
    balance                     = models.FloatField(max_length = 10, default="0")#In Dollars
    deleted                     = models.BooleanField(default=False)
    archive                     = models.BooleanField(default=False)


    class Meta:
        #db_table = 'packageinfo'
        ordering = ['-created_on']
        verbose_name_plural = 'Shipping Items'

    def __unicode__(self):
        return unicode(self.description)

    def get_absolute_url(self):
        if self.invoice is not None:
            return '%s.s3.amazonaws.com%s' %(settings.AWS_STORAGE_BUCKET_NAME, self.invoice)
        pass

    def item_info(self):
        return {'item_id': self.pk, 'barcode_id': self.package.gen_barcode_id(),
                'description': self.description, 'total_value_D': self.total_value}

    def item_info_v2(self):
        return {'tracking_number': self.package.tracking_number, 'pkg_number': self.package.number,
                'description': self.description, 'quantity': self.quantity,'total_value_D': self.total_value}

    # def amount(self):
    #     return self.total_value_N

    def amount(self):
        return self.total_value


# class USPSLabel(models.Model):
#     tracking_id  =    models.CharField(max_length = 50)
#     label        =    models.FileField(upload_to='import/shipping_labels/%Y/%m/%d')
#     package      =    models.ForeignKey('ShippingPackage')
#
#     class Meta:
#         verbose_name_plural = 'Shipping Label'
#
#
#     def __unicode__(self):
#         return '%s'  %(self.tracking_id)



class ShippingPackage(BasePackage):
    shipping_chain        = models.ForeignKey(ShippingChain, null=True, blank=True)

    shipment_type         =     models.CharField(max_length=25, null=True, blank=True, default="Regular")
    destination_address   =     models.ForeignKey('DeliveryAddress', null = True, blank = True)
    handling_option       =     models.CharField(max_length = 75, null = True, blank = True)
    #pick_up_charge_D      =     models.FloatField(default = 0.0)
    pickup_location       =     models.ForeignKey('PickupLocation', null = True, blank = True, related_name="pickup_location")
    dropoff_postoffice    =     models.ForeignKey('DropOffPostOffice', null = True, blank = True, related_name="dropoff_postoffice")
    drop_off_location     =     models.ForeignKey(LocalDistributorLocation, verbose_name="Local distributor drop_off_location", related_name = "drop_off_location", null = True)
    default_origin_address       =     models.CharField(max_length = 150, null = True, blank = True)
    default_destination_address  =     models.CharField(max_length = 150, null = True, blank = True)
    delivery_address      =     models.ForeignKey('DeliveryAddress', null = True, blank = True, related_name="delivery_address")
    return_address        =     models.ForeignKey('ReturnAddress', null = True, blank = True, related_name="return_address")

    origin_warehouse      =     models.ForeignKey(WarehouseMember, related_name = "pkg_origin_warehouse", null=True, blank=True)
    destination_warehouse =     models.ForeignKey(WarehouseMember, related_name = "pkg_destination_warehouse", null=True, blank=True)

    total_package_value   =     models.FloatField(max_length=50, default = 0)
    delivery_method       =     models.CharField(max_length = 75, choices = DELIVERY_METHOD, default="Office pickup")
    local_pickup_address  =     models.ForeignKey(LocalDistributorLocation, verbose_name="Local distributor address", related_name = "local_pickup_address", null = True, blank=True)
    override_payment      =     models.BooleanField(default=False)
    #usps_label           =     models.ForeignKey('UspsLabel', related_name = "usps_shipping_label", null = True)

    #tracker               = FieldTracker(fields=['box_height', 'box_length', 'box_width', 'box_weight', 'box_weight_K', 'insure', 'shipping_method'])


    def package_receiving_address(self):  #address of associated warehouse processing member
        if self.handling_option == 'pick-up-package':
            return self.pickup_location.full_address()
        elif self.handling_option == 'drop-at-postoffice':
            return self.dropoff_postoffice.full_address()
        elif self.handling_option == 'drop-at-location':
            return self.drop_off_location.full_address()
        elif self.handling_option == 'send-from-shop':
            return self.default_origin_address

    
    def get_delivery_address(self):
        try:
            return self.delivery_address.full_address()
        except Exception as e:
            print 'e: ',e
            return self.local_pickup_address.full_address()
        finally:
            return self.default_destination_address
            #return "%s, %s, %s, %s, %s, %s, %s" %(WH.address1.title(), WH.address2.title(), WH.city.title(), WH.state.title(), WH.phone_number, WH.zip_code, WH.country.title())


    def get_default_destination_warehouse(self):
        #WH = self.destination_warehouse.full_address()
        WH = self.default_destination_address
        return WH

    def itemcount(self):
        return self.shippingitem_set.count()

    def items_recieved(self):
        return self.shippingitem_set.filter(status="Received")

    def items_recieved_count(self):
        return self.shippingitem_set.filter(status="Received").count()

    def item_packages(self):
        return self.shippingitem_set.all()

    def item_invoice(self):
        return self.shippingpackageinvoice_set.all()

    def get_pickup_location(self):
        return self.pickup_location

    def items_count(self):
        return self.shippingitem_set.count()

    def items_description(self):
        desc = []
        items = self.shippingitem_set.all()
        for i in items:
            desc.append(i.description)
        return ",".join(desc)

    def items_total_value(self):
        # the_sum = 0
        # items = self.shippingitem_set.all()
        # for i in items:
        #     the_sum+=i.total_value
        # return the_sum
        return self.shippingitem_set.all().aggregate(Sum('total_value'))['total_value__sum']

    def get_package_subscriber(self):
        return self.shipping_chain.subscriber

    def package_info(self):
        return {'pkg_tracking_number':self.tracking_number,'pkg_items_count':self.items_count,'pkg_items_description':self.items_description,
        'pkg_items_total_value':self.items_total_value,'pkg_box_weight_higher':self.box_weight_higher,'pkg_box_weight_higher_K':self.box_weight_higher_K}




class ShippingPackageInvoice(models.Model):
    user            = models.ForeignKey(User, null = True)
    created_on      = models.DateTimeField(default = timezone.now)
    invoice         = models.FileField(upload_to='shipping_package_invoices/%Y/%m/%d')
    package         = models.ForeignKey('ShippingPackage', null=True)

    class Meta:
        verbose_name_plural  = "Shipping Package Invoice"

    def __unicode__(self):
        return self.package.tracking_number


class CourierLabel(models.Model):
    tracking_id  =    models.CharField(max_length = 50)
    label        =    models.FileField(upload_to='shipping_labels/%Y/%m/%d')
    package      =    models.ForeignKey('ShippingPackage', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Courier Package Label'


    def __unicode__(self):
        return '%s'  %(self.tracking_id)


class DeliveryAddress(AddressInfo):

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Delivery Addresses"


class ReturnAddress(AddressInfo):

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Return Addresses"


class DropOffPostOffice(AddressInfo):

    class Meta:
        verbose_name_plural = "Drop at Post Office Addresses" #%(self.user)


class PickupLocation(AddressInfo):

    def __unicode__(self):
        return "Pick up Location " #%(self.user)


    class Meta:
        verbose_name_plural = "Package pick up addresses"


class DockReceipt(models.Model):
    shipping_package                                = models.ForeignKey(ShippingPackage, null=True, blank=True)
    tracking_number                   = models.CharField(max_length=100,null=True, blank=True)
    exporter_name_and_address                       = models.CharField(max_length = 100,null=True, blank=True)
    zip_code                                        = models.CharField(max_length = 100,null=True, blank=True)
    consigned_to                                    = models.CharField(max_length = 100,null=True, blank=True)
    notify_party_name_and_address                   = models.CharField(max_length = 100,null=True, blank=True)
    document_number                                 = models.CharField(max_length = 100,null=True, blank=True)
    bl_or_awb_number                                = models.CharField(max_length = 100,null=True, blank=True)
    export_references                               = models.CharField(max_length = 100,null=True, blank=True)
    forwarding_agent_fmc_no                         = models.CharField(max_length = 100,null=True, blank=True)
    state_and_country_of_origin_or_ftz_number       = models.CharField(max_length = 100,null=True, blank=True)
    domestic_routing                                = models.CharField(max_length = 100,null=True, blank=True)
    loading_pier                                    = models.CharField(max_length = 100,null=True, blank=True)
    type_of_move                                    = models.CharField(max_length = 100,null=True, blank=True)
    containerized                                   = models.BooleanField(default=False)
    precarriage_by                                  = models.CharField(max_length = 100,null=True, blank=True)
    place_of_receipt_by_precarrier                  = models.CharField(max_length = 100,null=True, blank=True)
    exporting_carrier                               = models.CharField(max_length = 100,null=True, blank=True)
    port_of_loading                                 = models.CharField(max_length = 100,null=True, blank=True)
    foreign_port_of_unloading                       = models.CharField(max_length = 100,null=True, blank=True)
    place_of_delivery_by_oncarrier                  = models.CharField(max_length = 100,null=True, blank=True)
    mks_nos                                         = models.CharField(max_length = 100,null=True, blank=True)
    no_of_pkgs                                      = models.IntegerField(null=True, blank=True)
    description_of_package_and_goods                = models.CharField(max_length = 100,null=True, blank=True)
    gross_weight                                    = models.IntegerField(null=True, blank=True)
    measurement                                     = models.CharField(max_length=100, null=True, blank=True)
    lighter_truck                                   = models.CharField(max_length = 100,null=True, blank=True)
    arrived_date                                    = models.CharField(max_length = 100,null=True, blank=True)
    arrived_time                                    = models.CharField(max_length = 100,null=True, blank=True)
    created_on                                      = models.DateField(default = timezone.now)
    created_by                                      = models.CharField(max_length = 100,null=True, blank=True)
    batch                                           = models.CharField(max_length = 100,null=True, blank=True)
    unloaded_date                                   = models.CharField(max_length = 100,null=True, blank=True)
    unloaded_time                                   = models.CharField(max_length = 100,null=True, blank=True)
    checked_by                                      = models.CharField(max_length = 100,null=True, blank=True)
    placed_location                                 = models.CharField(max_length = 100,null=True, blank=True)
    receiving_clerk_name                            = models.CharField(max_length = 100,null=True, blank=True)
    date_from_receiving_clerk                       = models.CharField(max_length = 100,null=True, blank=True)


    def __unicode__(self):
        return '%s %s' %(self.exporter_name_and_address, self.consigned_to)
    
    
class DomesticPackage(models.Model):
    user                = models.ForeignKey(User, null=True)
    tracking_number     = models.CharField(max_length=20, null=True, blank=True)
    weight_kg           = models.DecimalField(max_digits = 15, decimal_places = 1)
    weight_lb           = models.DecimalField(max_digits = 15, decimal_places = 1)
    amount              = models.FloatField(default = 0)
    balance_paid        = models.FloatField(default = 0)
    description         = models.CharField(max_length = 200, null=True, blank=True)
    status              = models.CharField(max_length=25, default = "New")
    marketer            = models.ForeignKey(MarketingMember, null=True)
    deleted             = models.BooleanField(default=False)
    ordered             = models.BooleanField(default=False)
    shipper             = models.ForeignKey(LocalDistributionMember, null=True)
    created_on          = models.DateTimeField(null=True)
    pickup_address      = models.ForeignKey('DeliveryAddress', null = True, blank = True, related_name="pickup_address")
    dropoff_address     = models.ForeignKey('DeliveryAddress', null = True, blank = True, related_name="dropoff_address")
    pickup_center       = models.ForeignKey(LocalDistributorLocation, null = True, blank = True, related_name="pickup_center")
    dropoff_center      = models.ForeignKey(LocalDistributorLocation, null = True, blank = True, related_name="dropoff_center")
    
    
    def __unicode__(self):
        return self.tracking_number
    

