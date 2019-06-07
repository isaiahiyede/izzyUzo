from django.db.models import Q, Sum
from django.contrib.auth.models import User
#from shipping.models import Shipment, ShipmentPackage, MessageCenter
#from shopping.models import Order
from general.models import UserAccount, MessageCenter
from sokopay.models import SokoPay
from shipping.models import ShippingPackage

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils import timezone
from datetime import date
#from django.apps import apps
from general.custom_functions import get_model_from_string, costcalc_settings, marketingmember_costcalc

register = template.Library()


def account_standing(request, user):
    if not request.user.is_authenticated():
        return 0, 0
    #user = User.objects.select_related('useraccount').get(username = request.user)

    useraccount = UserAccount.objects.get(user = user)
    print "useraccount country",useraccount.country

    #user.get_profile()
    #user = useraccount.user
    #user_country = user.useraccount.country

    #1. Calculate sum of user's approved (bank) and successful (card) payments
    #added_payments = SokoPay.objects.user_add_jejepay(request.user).aggregate(Sum('amount'))
    added_payments = SokoPay.objects.user_add_jejepay(user).aggregate(Sum('amount'))
        
    if added_payments['amount__sum'] == None:
        total_added_payments_N = 0
    # else:
    #     if not useraccount.country == "USA":
    #         total_added_payments_N = added_payments['amount__sum']
    else:
        total_added_payments_N = added_payments['amount__sum']
    print "total added payments", total_added_payments_N
    #used_payments = SokoPay.objects.jejepay_withdrawals(request.user).aggregate(Sum('amount'))
    used_payments = SokoPay.objects.sokopay_withdrawals(user).aggregate(Sum('amount'))
    if used_payments['amount__sum'] == None:
        total_used_payments_N = 0
    # else:
    #     if not useraccount.country == "USA":
    #         total_used_payments_N = used_payments['amount__sum']
    else:
        total_used_payments_N = used_payments['amount__sum']
    print "total used payments", total_used_payments_N

    #user_approved_refunds = SokoPay.objects.user_refund_jejepay(request.user).aggregate(Sum('amount'))
    user_approved_refunds = SokoPay.objects.user_refund_jejepay(user).aggregate(Sum('amount'))
    if user_approved_refunds['amount__sum'] == None:
        total_user_refunds_N = 0
    # else:
    #     if not useraccount.country == "USA":
    #         total_user_refunds_N = added_payments['amount__sum']
    else:
        total_user_refunds_N = user_approved_refunds['amount__sum']

    print "total user refunds", total_user_refunds_N

    #Sum of orders and shipments costs

    #4. Calculate the user's credit standing as #1 - #2 - #3
    user_credit_amount_N = total_added_payments_N - total_used_payments_N - total_user_refunds_N
    if not useraccount.country == "United States":
        dollar_exchange_rate = marketingmember_costcalc(request,useraccount.country).dollar_exchange_rate
        user_credit_amount_D = user_credit_amount_N / float(dollar_exchange_rate)
        useraccount.credit_amount_N = user_credit_amount_N
    else:
        user_credit_amount_D = user_credit_amount_N
        user_credit_amount_N = 0
        useraccount.credit_amount_N = 0
        print "USER", useraccount.credit_amount_N
    #return {'user_credit_amount_N': user_credit_amount_N, 'user_credit_amount_D': user_credit_amount_D}
    #useraccount.credit_amount_N = user_credit_amount_N
    useraccount.credit_amount_D = user_credit_amount_D
    useraccount.save()

    return round(user_credit_amount_N, 2), round(user_credit_amount_D, 2)

def format_num(number):
    return intcomma(number)

@register.simple_tag
def account_standing_shipping(request, user, class_name):
    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
    if class_name == "":
        return "<p>=N= %s</p> <p>$ %s</p>" %(format_num(user_credit_amount_N), format_num(user_credit_amount_D))
    return "<p>=N= %s</p> <p class='sm'>$ %s</p>" %(format_num(user_credit_amount_N), format_num(user_credit_amount_D))

@register.simple_tag
def account_standing_shopping(request, user):
    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
    return "<h3>=N= %s</h3> <p>$ %s</p>" %(format_num(user_credit_amount_N), format_num(user_credit_amount_D))


def create_jejepay_record(**kwargs):
    SokoPay.object.create(user = kwargs['user'], purchase_type_1 = kwargs['purchase_type_1'],
                          purchase_type_2 = kwargs['purchase_type_2'], amount = kwargs['amount'],
                          ref_no = kwargs['ref_no'], bank = kwargs['bank'], teller_no = kwargs['teller_no'],
                          status = "Approved", message = kwargs['message'])


@register.inclusion_tag("tags/account_widget.html")
def account_widget_v1(request):
    user = User.objects.get(username = request.user.username)

    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)

    account = user.useraccount #user.get_profile()
    user_country = user.useraccount.country
    #ship_credit = account.credit_amount_D
    #ship_credit_N = float(ship_credit) * dollarNairaRate
    #pending_credit = account.pending_amount_N
    #
    #unused_credit = user_unused_credit(request)

    path = request.path
    return {'username': user.username, 'ship_credit_N': user_credit_amount_N, 'ship_credit' : user_credit_amount_D, 'path': path, 'user_country': user_country}



@register.inclusion_tag("snippet/account_widget.html")
def account_widget_v2(request, username=None):
    user = User.objects.get(username = username)

    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)

    account = user.useraccount #user.get_profile()
    user_country = user.useraccount.country
    return {'credit_D': user_credit_amount_D, 'credit_N': user_credit_amount_N, 'username': username}


@register.simple_tag
def shipments_count(user):
    if user.is_authenticated():
        pkgs_count = ShippingPackage.objects.filter(Q(user = user), Q(ordered=True), ~Q(status = 'cancelled')).count()
        return pkgs_count
        # return Export.objects.filter(Q(user = user), ~Q(status = 'cancelled')).count()
    return 0
    #return Shipment.objects.filter(user = user, active = True).count()


@register.simple_tag
def local_shipments_count(user):
    if user.is_authenticated():
        pkgs_count = DomesticPackage.objects.filter(Q(user = user), Q(ordered=True).count())
        return pkgs_count
        # return Export.objects.filter(Q(user = user), ~Q(status = 'cancelled')).count()
    return 0
    #return Shipment.objects.filter(user = user, active = True).count()

@register.simple_tag
def user_totalvalue(user):
    pkgs_value_D = ShippingPackage.objects.filter(Q(user = user), Q(ordered=True), ~Q(status = 'cancelled')).aggregate(Sum('balance_paid_D'))
    pkgs_value_N = ShippingPackage.objects.filter(Q(user = user), Q(ordered=True), ~Q(status = 'cancelled')).aggregate(Sum('balance_paid_N'))
    #imp_value_D = ShippingPackage.objects.filter(Q(user = user), Q(ordered=True), ~Q(status = 'cancelled')).aggregate(Sum('balance_paid_D'))
    #exp_value_N = ExportPackage.objects.filter(Q(user = user), Q(ordered=True), ~Q(status = 'cancelled')).aggregate(Sum('balance_paid_N'))
    #imp_value_N = ShippingPackage.objects.filter(Q(user = user), Q(ordered=True), ~Q(status = 'cancelled')).aggregate(Sum('balance_paid_N'))
    #print exp_value_D, imp_value_D, exp_value_N, imp_value_N
    if pkgs_value_D['balance_paid_D__sum'] != None:
        dollar_val = pkgs_value_D['balance_paid_D__sum']
        naira_val  = pkgs_value_N['balance_paid_N__sum']
    else:
        dollar_val = 0.0
        naira_val = 0.0
    # else:
    #     if not imp_value_D['balance_paid_D__sum'] == None:
    #         dollar_val = exp_value_D['balance_paid_D__sum'] + imp_value_D['balance_paid_D__sum']
    #         naira_val = exp_value_N['balance_paid_N__sum'] + imp_value_N['balance_paid_N__sum']
    #     else:
    #         dollar_val = exp_value_D['balance_paid_D__sum']
    #         naira_val = exp_value_N['balance_paid_N__sum']
    return "$"+ format(dollar_val, '.2f') #+ "/" + "N" + format(naira_val, '.2f')
    # dollar_val = exp_value_D['balance_paid_D__sum'] + imp_value_D['balance_paid_D__sum']
    # naira_val = exp_value_N['balance_paid_N__sum'] + imp_value_N['balance_paid_N__sum']
    # return "$"+ str(dollar_val) + "/" + "N" + str(naira_val)

@register.simple_tag
def orders_count(user):
    #if user.is_authenticated():
    #    return Order.objects.filter(Q(user = user), ~Q(status="cancelled")).distinct().count()
    return 0
    #return Order.objects.filter(Q(user = user) , (Q(status = "Approved") | Q(status = "processing"))).count()

@register.simple_tag
def messages_count(user):
    if user.is_authenticated():
       # return MessageCenter.objects.filter(user = user, new = True).count()
       return MessageCenter.objects.filter(user = user).count()

    # return 0

@register.inclusion_tag("zaposta_snippet/zaposta_account_standing.html")
def zaposta_acct_standing(request, shop_or_ship, acct_standing_border, pkg_model=None):
    user = request.user
    data_dict = {}
    shop_or_ship_text = ''
    useraccount = UserAccount.objects.get(user=user)
    print 'pkg_model: ',pkg_model

    if shop_or_ship == True and pkg_model != None:
        # if pkg_model == 'ShipmentPackage':
        #     PkgModel = get_model_from_string('shipping', pkg_model)#apps.get_model(app_label='shipping', model_name=pkg_model)
        #     shop_or_ship_text = 'shipment'
        # else:
        #     PkgModel = get_model_from_string('shopping', pkg_model)#apps.get_model(app_label='shopping', model_name=pkg_model)
        #     shop_or_ship_text = 'order'

        PkgModel = get_model_from_string('export', 'ExportPackage')
        shop_or_ship_text = 'export'

        #print PkgModel.objects.filter(Q(user = user), ~Q(batch = None), ~Q(expires_on = None), Q(expires_on__gte = timezone.now())).order_by('expires_on')
        #print expected_pkgs
        #expected_pkg = ShipmentPackage.objects.filter(Q(user = user), ~Q(batch = None), ~Q(expires_on = None)).order_by('expires_on').values('expires_on')[0]
        try:
            #expected_pkg = PkgModel.objects.filter(Q(user = user), ~Q(batch = None), ~Q(expires_on = None), Q(expires_on__gte = timezone.now())).order_by('expires_on')[0]#.values('expires_on')[0]
            expected_pkg = PkgModel.objects.filter(Q(user = user))[0]#.values('expires_on')[0]
            try:

                tracking_number = expected_pkg.shipment.tracking_number
                #print tracking_number
            except Exception as e:
                #print e
                tracking_number = expected_pkg.order.tracking_number

            #data_dict.update({'expires_on': expected_pkg['expires_on'], 'tracking_number': tracking_number})
            data_dict.update({'expires_on': expected_pkg.expires_on, 'tracking_number': tracking_number})
        except Exception as e:
            print e
            data_dict.update({'expires_on': date.today()})

    #print data_dict

    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
    print user_credit_amount_N, user_credit_amount_D
    data_dict.update({'zap_credit_N': user_credit_amount_N, 'zap_credit_D' : user_credit_amount_D,
            'shop_or_ship': shop_or_ship, 'acct_standing_border': acct_standing_border,
            'shop_or_ship_text': shop_or_ship_text, "country": useraccount.country, 'user':user})

    return data_dict
   # return {'zap_credit_N': user_credit_amount_N, 'zap_credit_D' : user_credit_amount_D,
    #        'shop_or_ship': shop_or_ship, 'acct_standing_border': acct_standing_border}

@register.inclusion_tag("zaposta_snippet/zaposta_account_standing_inner.html")
def zaposta_acct_standing_v1(request, acct_standing_border):
    user = request.user
    data_dict = {}
    
    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
    print "got here",user_credit_amount_N, user_credit_amount_D
    data_dict.update({'zap_credit_N': user_credit_amount_N, 'zap_credit_D' : user_credit_amount_D,
            'acct_standing_border': acct_standing_border, 'user':user})

    return data_dict
