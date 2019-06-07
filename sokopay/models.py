from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
from general.modelfield_choices import OFFERED_SERVICES
from service_provider.models import Subscriber, ShippingChain, MarketingMember
from general.models import UserAccount
from shipping.models import ShippingPackage, DomesticPackage

CP = "Card Payment"
BD = "Bank Deposit"
WT = "Wire Transfer"
AD = "Admin"
RF = "Refund"
JW = "SokoPay Withdrawal"
JR = "SokoPay Refund"
PP = "PayPal"
SK = "SokoPay"

SOKOPAY_TYPE_1 = (
    (CP, CP),
    (BD, BD),
    (WT, WT),
    (AD, AD),
    (RF, RF),
    #(u'SC', u'Credit from Shippyme Acct.'),
    (JW, JW),
    (JR, JR),
    (PP, PP),
)

PAYMENT_CHANNELS = (
    (CP, CP),
    (BD, BD),
    (WT, WT),
    (PP, PP),
    (SK, SK),
)


SOKOPAY_TYPE_2 = (
    ('Add', 'Add'),
    ('Remove', 'Remove'),
    ('Refund', 'Refund'),
)

SOKOPAY_STATUS = (
    (u'Approved', u'Approved'),
    (u'Pending Approval', u'Pending Approval'),
    (u'Declined', u'Declined'),
    (u'Successful', u'Successful'),
    (u'Failed', u'Failed'),
)

SOKOPAY_CURRENCY = (
    (u'NGN', u'NGN'),
    (u'USD', u'USD'),
)

SOKOPAY_BANK = (
    (u'Wells Fargo', u'Wells Fargo'),
    (u'Fidelity Bank', u'Fidelity Bank'),
    (u'GTBank', u'GTBank'),
    (U'UBA', u'UBA'),
    (u'Zenith Bank', u'Zenith Bank'),
    (u'Suntrust Bank', u'Suntrust Bank'),
    (u'WebPay', u'WebPay'),
    (u'Admin', u'Admin'),
    (u'SokoPay', u'SokoPay'),
    (u'Interswitch', u'Interswitch'),
    (u'Bank Deposit', u'Bank Deposit'),
    (u'PayStack', u'PayStack'),
    (u'Flutterwave', u'Flutterwave'),
    (u'PayPal', u'PayPal'),
)

class CustomManager(models.Manager):
    def add_jejepay(self):
        return super(CustomManager, self).get_queryset().filter(Q(purchase_type_2 = "Add"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )

    def remove_jejepay(self):
        return super(CustomManager, self).get_queryset().filter(Q(purchase_type_2 = "Remove"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )

    def user_add_jejepay(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_2 = "Add"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )

    def user_remove_jejepay(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_2 = "Remove"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )

    def user_refund_jejepay(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_2 = "Refund"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )

    def card_payments(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_1 = CP))

    def bank_deposits(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_1 = BD) | Q(purchase_type_1 = WT), Q(purchase_type_2 = 'Add'))

    def sokopay_withdrawals(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_1 = JW) , Q(purchase_type_2 = "Remove"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )
        #return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(purchase_type_1 = JW) | Q(purchase_type_2 = "Remove"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )

    def sokopay_log(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user = user), Q(status = "Successful") | Q(status = "Approved"), Q(purchase_type_1 = JW) | Q(purchase_type_1 = RF) | Q(purchase_type_1 = AD) | Q(purchase_type_1 = JR))

    def mm_successful_card_payments_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = CP), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ))

    def mm_unsuccessful_card_payments_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = CP), ~Q(status__icontains = "Successful") , ~Q(status__icontains = "Approved") )

    def mm_successful_sokopay_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = JW) , Q(purchase_type_2 = "Remove"), Q(status__icontains = "Approved") )

    def mm_unsuccessful_sokopay_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = JW) , Q(purchase_type_2 = "Remove"), ~Q(status__icontains = "Approved") )
    
    def mm_pending_sokopay_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = BD) | Q(purchase_type_1 = WT), Q(purchase_type_2 = 'Add'), Q(status__icontains = "Pending Approval"))
    
    def mm_add_sokopay_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = BD) | Q(purchase_type_1 = WT), Q(purchase_type_2 = "Add"), ( Q(status__icontains = "Successful") | Q(status__icontains = "Approved") ) )
    
    def mm_decline_sokopay_log(self, mm):
        return super(CustomManager, self).get_queryset().filter(Q(user__useraccount__marketer = mm), Q(purchase_type_1 = BD) | Q(purchase_type_1 = WT), Q(purchase_type_2 = "Add"), ( Q(status__icontains = "Declined") ) )

    

class SokoPay(models.Model):
    user            = models.ForeignKey(User, null = True, related_name="jejepay")
    purchase_type_1   = models.CharField(max_length=20, default = "Card Payment")
    purchase_type_2   = models.CharField(max_length=20, choices=SOKOPAY_TYPE_2)
    amount          = models.FloatField(default=0.0)#in Naira
    #currency        = models.CharField(max_length=3, choices=SOKOPAY_CURRENCY)
    ref_no          = models.CharField(max_length=50, null=True, blank=True)
    payment_gateway_tranx_id    = models.CharField(max_length=30, null=True, blank=True) #payment_gateway_tranx_id

    bank              = models.CharField(max_length=50, choices=SOKOPAY_BANK)
    teller_no         = models.CharField(max_length=100, null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    status            = models.CharField(max_length=100, default='Pending Approval')#, choices=SOKOPAY_STATUS)
    message           = models.CharField(max_length=100, null=True, blank=True)

    exchange_rate     = models.FloatField(default=0)

    objects           = CustomManager()

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return unicode(self.user)

    def successful_approved(self):
        status = self.status.lower()
        if "successful" in status:
            return True
        elif "approved" in status:
            return True
        return False

    def shop_ship_ref(self):
        try:
            shop_ship_id = ref_no.split('|')[1]
            if self.message == "shopping":
                return get_object_or_404(Order, id = shop_ship_id).tracking_number
            #if shipping
            return get_object_or_404(Shipment, id = shop_ship_id).tracking_number
        except:
            return None


    def amount_plus_surcharge(self):
        return int(round(self.amount * (101.5/100), 2) * 100)
    
 
 
 
class MarketerPaymentManager(models.Manager):
    def get_card_payments(self):
        return super(MarketerPaymentManager, self).get_queryset().filter(payment_channel = "Card Payment")
 
    def card_payments(self, user):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(user = user), Q(payment_channel = "Card Payment"))

    def bank_payments(self, user):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(user = user), Q(payment_channel = "Bank Deposit") | Q(payment_channel = "Wire Transfer"))

    def sokopay_payments(self, user):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(user = user), Q(payment_channel = "SokoPay"))
        
    def paypal_payments(self, user):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(user = user), Q(payment_channel = "PayPal"))
    
    def mm_successful_card_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer), Q(payment_channel = "Card Payment"), Q(status__icontains = "Successful") | Q(status__icontains = "Approved"))

    def mm_unsuccessful_card_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer), Q(payment_channel = "Card Payment"), ~Q(status__icontains = "Successful") , ~Q(status__icontains = "Approved") )

    def mm_successful_sokopay_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer), Q(payment_channel = "SokoPay"), Q(status__icontains = "Approved") )

    def mm_unsuccessful_sokopay_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer), Q(payment_channel = "SokoPay"), Q(status__icontains = "Declined") )

    def mm_pending_sokopay_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer), Q(payment_channel = "SokoPay"), Q(status__icontains = "Pending Approval") )

    def mm_successful_bank_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer),  Q(status__icontains = "Approved"), (Q(payment_channel = "Bank Deposit") | Q(payment_channel = "Wire Transfer")))
    
    def mm_declined_bank_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer),  Q(status__icontains = "Declined"), (Q(payment_channel = "Bank Deposit") | Q(payment_channel = "Wire Transfer")))
    
    def mm_pending_bank_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer),  Q(status__icontains = "Pending Approval"), (Q(payment_channel = "Bank Deposit") | Q(payment_channel = "Wire Transfer")))

    def mm_paypal_payments(self, marketer):
        return super(MarketerPaymentManager, self).get_queryset().filter(Q(marketer = marketer), Q(payment_channel = "Paypal"))
 
    
    
    
class MarketerPayment(models.Model):
    user            = models.ForeignKey(UserAccount, null = True)
    payment_channel = models.CharField(max_length=20, default = "Card Payment", choices=PAYMENT_CHANNELS)
    purchase_type_2   = models.CharField(max_length=20, default="Add", choices=SOKOPAY_TYPE_2)
    purchase_type_3   = models.CharField(max_length=20, null=True, blank=True)
    amount          = models.FloatField(max_length=15)#in Naira
    #currency        = models.CharField(max_length=3, choices=SOKOPAY_CURRENCY)
    package         = models.ForeignKey(ShippingPackage, null=True, blank=True)
    ref_no          = models.CharField(max_length=50, null=True, blank=True)
    payment_gateway_tranx_id    = models.CharField(max_length=30, null=True, blank=True) #payment_gateway_tranx_id
    marketer          = models.ForeignKey(MarketingMember, null=True, blank=True)
    bank              = models.CharField(max_length=50, null=True, blank=True)
    teller_no         = models.CharField(max_length=100, null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    approved_by       = models.CharField(max_length=100, null=True, blank=True)
    status            = models.CharField(max_length=100, default='Pending Approval')#, choices=SOKOPAY_STATUS)
    message           = models.CharField(max_length=100, null=True, blank=True)
    local_package     = models.ForeignKey(DomesticPackage, null=True, blank=True)
    #exchange_rate     = models.FloatField(default=0)

    objects           = MarketerPaymentManager()
 
    
    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return unicode(self.user)
 
 
 
 
class SubscriberPaymentManager(models.Manager):
    def get_paid_rented_service(self, chain, service, owner):
        return super(SubscriberPaymentManager, self).get_queryset().filter(Q(service=service), Q(chain=chain), Q(owned_by=owner))
 
 
    
class SubscriberPayment(models.Model):
    service          = models.CharField(max_length=50, choices=OFFERED_SERVICES)
    owned_by         = models.ForeignKey(Subscriber, related_name="owned_by")
    rented_by        = models.ForeignKey(Subscriber, related_name="rentee")
    amount           = models.FloatField(max_length=50)
    ref_no           = models.CharField(max_length=30)
    sokohali_fee     = models.FloatField(max_length = 50)
    total_value      = models.FloatField(max_length=15)
    status           = models.CharField(max_length=100, default = "Pending Approval")
    message          = models.CharField(max_length=100, null=True, blank=True)
    date             = models.DateTimeField(auto_now_add=True)
    chain            = models.ForeignKey(ShippingChain, null=True, blank=True)
    objects          = SubscriberPaymentManager()
    
    
    def __unicode__(self):
        return self.service
