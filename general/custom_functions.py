from sokohaliAdmin.models import CostCalcSettings, ExportObjCostCalcSettings,\
                    NewFedExLocalFreightSettings, OperatingCountry
from itertools import chain
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import time
from django.utils.html import strip_tags
from django.apps import apps
from general.models import UserAccount, ActionHistory, UserSpecialRate, AddressBook
from general.modelfield_choices import COUNTRIES
import random
from shipping.models import ShippingItem, ShippingPackage, DeliveryAddress

from django.contrib.auth.models import User
from sokopay.models import SokoPay
from sokopay.forms import SokoPayForm
from django.shortcuts import render, redirect,render_to_response
import hashlib, requests
from django.db.models import Sum, F, Q, FloatField

from service_provider.models import LocalDistributorLocation, LocalDistributorPrice,  MarketingMember, Subscriber
import math
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Max
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
import string
from django.template import Context, RequestContext

from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMessage
from django.template.loader import get_template, render_to_string
from cities_light import models as world_geo_data




def format_num(num):
    return intcomma(num)


def costcalc_settings():
    cost_settings = CostCalcSettings.objects.get(pk = 1)
    return cost_settings

# def costcalc_settings(pk):
#     cost_settings = CostCalcSettings.objects.get(pk = pk)
#     return cost_settings

# reviewed code
# def marketer_costcalc_settings(marketer, shipping_origin):
#     cost_settings = CostCalcSettings.objects.get(marketer = marketer, country = shipping_origin)
#     return cost_settings


def set_cookie(request, response, key, value, max_age_seconds):
    if not check_cookie(request, key):
        response.set_cookie(key, value, max_age_seconds)
    return response


def check_cookie(request, cookie_key):
    return request.COOKIES.has_key(cookie_key)


def add_space(word):
    the_new_word = list(word)
    new_word = []
    for i in the_new_word:
        if i.isupper():
            i = " " + i
        new_word.append(i)
    return "".join(new_word)


def tranex_data_info():
    return TranexShippingCostSettings.objects.get(pk = 1)


def fedex_data_info():
    fedex_data = FedexDeliveryCostSettings.objects.get(pk = 1)
    return fedex_data


def new_fedex_data():
    new_fedex_data = NewFedExLocalFreightSettings.objects.get(pk = 1)
    return new_fedex_data


def expressAir_data_info():
    expressAir_data = ExpressAirDeliveryCostSettings.objects.get(pk = 1)
    return expressAir_data


def country_freight_costs(costcalc, country):
     if country == COUNTRIES[0]:
          shipping_UnitCost_Air         = costcalc.flat_cost_air_freight

          shipping_UnitCost_Air_1       = costcalc.unit_cost_air_freight_1
          shipping_UnitCost_Air_2       = costcalc.unit_cost_air_freight_2
          shipping_UnitCost_Air_3       = costcalc.unit_cost_air_freight_3
          shipping_UnitCost_Air_4       = costcalc.unit_cost_air_freight_4
          shipping_UnitCost_Air_5       = costcalc.unit_cost_air_freight_5

          exchange_rate = costcalc.dollar_naira_rate

     elif country == COUNTRIES[1]:
          shipping_UnitCost_Air         = 0

          shipping_UnitCost_Air_1       = costcalc.unit_cost_air_freight_11
          shipping_UnitCost_Air_2       = costcalc.unit_cost_air_freight_21
          shipping_UnitCost_Air_3       = costcalc.unit_cost_air_freight_31
          shipping_UnitCost_Air_4       = costcalc.unit_cost_air_freight_41
          shipping_UnitCost_Air_5       = costcalc.unit_cost_air_freight_51

          exchange_rate = costcalc.pound_naira_rate

     return shipping_UnitCost_Air, shipping_UnitCost_Air_1, shipping_UnitCost_Air_2, shipping_UnitCost_Air_3, \
               shipping_UnitCost_Air_4, shipping_UnitCost_Air_5, exchange_rate


# def country_freight_costs(costcalc, country):
#      if country == COUNTRIES[0]:
#           shipping_UnitCost_Air         = costcalc.flat_cost_air_freight

#           shipping_UnitCost_Air_1       = costcalc.unit_cost_air_freight_1
#           shipping_UnitCost_Air_2       = costcalc.unit_cost_air_freight_2
#           shipping_UnitCost_Air_3       = costcalc.unit_cost_air_freight_3
#           shipping_UnitCost_Air_4       = costcalc.unit_cost_air_freight_4
#           shipping_UnitCost_Air_5       = costcalc.unit_cost_air_freight_5

#           exchange_rate = costcalc.dollar_naira_rate

#      elif country == COUNTRIES[1]:
#           shipping_UnitCost_Air         = 0

#           shipping_UnitCost_Air_1       = costcalc.unit_cost_air_freight_11
#           shipping_UnitCost_Air_2       = costcalc.unit_cost_air_freight_21
#           shipping_UnitCost_Air_3       = costcalc.unit_cost_air_freight_31
#           shipping_UnitCost_Air_4       = costcalc.unit_cost_air_freight_41
#           shipping_UnitCost_Air_5       = costcalc.unit_cost_air_freight_51

#           exchange_rate = costcalc.pound_naira_rate

#      return shipping_UnitCost_Air, shipping_UnitCost_Air_1, shipping_UnitCost_Air_2, shipping_UnitCost_Air_3, \
#                shipping_UnitCost_Air_4, shipping_UnitCost_Air_5, exchange_rate


def country_exchange_rate(country, cost_calc=None):
     if cost_calc == None:
          cost_calc = costcalc_settings()
     if country == COUNTRIES[0]:
          return cost_calc.dollar_naira_rate
     elif country == COUNTRIES[1]:
          return cost_calc.pound_naira_rate


def get_file_path(instance, filename):
     ext = filename.split('.')[-1]
     filename = "%.%s" %(uuid.uuid4(), ext)
     return os.path.join('uploads/logos', 'filename')


def currencyEquivalentOfDollar(currency_rate, dollar_rate, value):
     return round((float(dollar_rate/currency_rate) * value), 2)


def operatingCountryStatus(country):
     return OperatingCountry.objects.get(country = country).status


def get_order_datetime(order_tracking_no):
    if order_tracking_no[0] == "Z":
        order_tracking_no = order_tracking_no[1:]

    order_year = int("20%s" %order_tracking_no[:2])
    order_month = int(order_tracking_no[2:4])
    order_day   = int(order_tracking_no[4:6])
    actual_order_datetime = timezone.make_aware(datetime(order_year, order_month, order_day, 00, 00, 00), timezone.get_default_timezone())
    return actual_order_datetime

    #start_date = datetime(2015, 10, 9, 00, 00, 00)
    #orders = Order.objects.filter(Q(status = "processing"), Q(date_joined__lte = end_date))


def form_errors(form_error_list):
    #return {'errors': {field: str(strip_tags(errorlist)[0]) for field, errorlist in form_error_list.iteritems()}}
    return {field: str(strip_tags(errorlist)[0]) for field, errorlist in form_error_list.iteritems()}


def get_model_from_string(app_name, model_string):
    return apps.get_model(app_label = app_name, model_name = model_string)


def random_suite_no():
    #random_code = '1-%d' %random.randint(0, 9)
    #random_code = '%d' %random.randint(0, 9)
    random_code = ''
    #alnum = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for x in range(4):
        random_code += str(random.randint(0, 9))
        #random_code += random.choice(alnum)
    #print random_code
    return random_code


def generate_suite_no():
    random_code = random_suite_no()
    while UserAccount.objects.filter(suite_no=random_code):
        #random_code = generate_suite_no()
        random_code = random_suite_no()
    return random_code


def generate_mm_random_code():
    random_code = random_suite_no()
    print 'random_code out: ',random_code
    while MarketingMember.objects.filter(random_code=random_code):
        random_code = random_suite_no()
        print 'random_code inside: ',random_code
    return random_code


def get_random_code(stringlength):
    random_chars = "".join([random.choice(string.ascii_letters + string.digits) for n in range(stringlength)])
    return random_chars


# class TrackingNumber():
#     def __init__(self, prefix, char_length):
#     #def __init__(self, prefix, obj_type, char_length):
#         self.prefix = prefix
#         #self.obj_type = obj_type
#         self.char_length = char_length
#         #self.todaysdate = todaysdate#datetime.date.today()

#     def calc_time_converter(self):
#         return str(time.strftime("%y%m%d"))

#     def random_code(self):
#         random_number = User.objects.make_random_password(length = self.char_length, allowed_chars='0123456789')
#         return random_number

#     def generate_tracking_no(self):
#         return self.prefix + self.calc_time_converter() + self.random_code()

#     def tracking_no(self, model_class):
#         tracking_number = self.generate_tracking_no()#None
#         while model_class.objects.filter(tracking_number = tracking_number):
#                 tracking_number = TrackingNumber().generate_tracking_no()
#         # if self.obj_type == "export":
#         #     while Export.objects.filter(tracking_number = tracking_number):
#         #         tracking_number = TrackingNumber().generate_tracking_no()
#         # elif self.obj_type == "ex_package":
#         #     while ExportPackage.objects.filter(tracking_number = tracking_number):
#         #         tracking_number = TrackingNumber().generate_tracking_no()
#         # elif self.obj_type == "import":
#         #     while ImportShipment.objects.filter(tracking_number = tracking_number):
#         #         tracking_number = TrackingNumber().generate_tracking_no()
#         return tracking_number


def has_special_rate_for_route(request, origin, destination, freight_type):
    try:
        special_rate = UserSpecialRate.objects.get(user = request.user, origin = origin, destination = destination, freight_type__icontains = freight_type)
        return True, special_rate.rate_per_lb_D
    except Exception as e:
        print 'has_special_rate_for_route | e: ',e
        return False, 0.0


class TrackingNumber():
    def __init__(self, marketing_member, origin, destination, prefix, char_length):
        #print "TrackingNumber | origin and destination ", origin, destination
        self.prefix = prefix
        self.char_length = char_length
        self.mm_code = marketing_member.random_code
        self.origin_code = world_geo_data.Country.objects.filter(name = origin.lower())[0].code3
        self.destination_code = world_geo_data.Country.objects.filter(name = destination.lower())[0].code3


    def calc_time_converter(self):
        return str(time.strftime("%y%m%d"))


    def random_code(self):
        random_number = User.objects.make_random_password(length = self.char_length, allowed_chars='0123456789')
        return random_number


    def generate_tracking_no(self):
        # tracking_number = str(self.prefix) + str(self.calc_time_converter()) + str(self.random_code()) + str(self.mm_code) + str(self.origin_code.upper()) + ">" + str(self.destination_code.upper())
        # print "tracking nmber: ", tracking_number
        return str(self.calc_time_converter()) + str(self.random_code()) + str(self.mm_code) + str(self.origin_code.upper()) + "-" + str(self.destination_code.upper())


    def tracking_no(self, model_class):
        tracking_number = self.generate_tracking_no()#None
        while model_class.objects.filter(tracking_number = tracking_number):
            tracking_number = TrackingNumber().generate_tracking_no()

        return tracking_number    


def remove_from_string(string, what_to_remove):
    return string.replace(what_to_remove, '')


def remove_(chosen_status):
    delimiter1 = '_'
    delimiter2 = ' '
    return delimiter2.join(chosen_status.split(delimiter1))


def get_orderpackages_weight(request, orderpackages):
    packages = orderpackages
    Actual_Weight_lbs = 0
    Actual_Weight_kg = 0
    Dimensional_Weight_lbs = 0
    Dimensional_Weight_kg = 0
    for pkg in packages:
        Actual_Weight_lbs += pkg.box_weight_Actual
        Actual_Weight_kg  += pkg.box_weight_Actual_K
        Dimensional_Weight_lbs += pkg.box_weight_Dim
        Dimensional_Weight_kg  += pkg.box_weight_Dim_K
    return Actual_Weight_lbs, Actual_Weight_kg, Dimensional_Weight_lbs, Dimensional_Weight_kg


def generate_creditpurchase_ref():
    ref_no = ''
    digits = '1234567890'
    ref_no_length = 9
    for x in range(ref_no_length):
        ref_no += digits[random.randint(0, len(digits) - 1)]
    return ref_no


def creditpurchase_ref(request, obj_id = None):
    if obj_id != None:
        ref = generate_creditpurchase_ref()+ "|%s" %obj_id
        while SokoPay.objects.filter(ref_no = ref):
            ref = generate_creditpurchase_ref() + "|%s" %obj_id
        return ref

    ref = generate_creditpurchase_ref()
    while SokoPay.objects.filter(ref_no = ref):
        ref = generate_creditpurchase_ref()
    return ref


def buy_jejepay_credit_deposit_general(form, message = None):
    user = form.cleaned_data['user']
    print "purchase type",form.cleaned_data['purchase_type_1']
    purchase_type = form.cleaned_data['purchase_type_1']
    amount_purchased = form.cleaned_data['amount']
    if amount_purchased > 0:
        #CreditPurchaseForm
        form.save()
        if message is not None:
            jejepay = form.instance
            jejepay.status = "Approved"
            jejepay.message = message
            jejepay.save()
        accountToUpdate = UserAccount.objects.get(user = user)
        #username = accountToUpdate.username
        accountToUpdate.pending_amount_N += amount_purchased
        accountToUpdate.save()
        return True
    else:
        return False


def add_payment_record_to_objhistory(request, prev_balance_N, new_balance_N, obj, user = None):
    prefix_msg = "Balance %s applying jejepay credit: =N= %s"
    #Current balance record
    msg1 = prefix_msg %("before", str(prev_balance_N))
    msg2 = prefix_msg %("after", str(new_balance_N))
    msgs = [msg1, msg2]

    for msg in msgs:
        if hasattr(obj, "order_balance_N"):
            if user == None:
                order_history(request, msg, None, None, obj)
            else:
                order_history(request, msg, None, None, obj, user.username)
        else:
            kwargs = {'status': msg, 'item': None, 'package': None,
             'batch': None, 'shipment': None, 'export': None}
            if user == None:
                kwargs.update({'user': request.user})
            else:
                kwargs.update({'user': user})

            if hasattr(obj, 'drop_off_location'):
                kwargs.update({'export': obj})
            else:
                kwargs.update({'shipment': obj})
            create_shipment_history(**kwargs)


def use_shipping_credit(request, amount_N, ref_no, prev_balance_N, new_balance_N, obj, user = None):
    if hasattr(obj, "order_balance_N"):
        obj_type = "order"
    else:
        obj_type = "booking"

    if user == None:
        user = request.user
    else:
        user = user
    SokoPay.objects.create(user = user, amount = amount_N, purchase_type_1 = 'SokoPay Withdrawal',
                           purchase_type_2 = 'Remove', ref_no = ref_no, bank = 'SokoPay', teller_no = obj.tracking_number,
                           status = 'Approved', message = 'Applied to %s %s' %(obj_type, obj.tracking_number))

    add_payment_record_to_objhistory(request, prev_balance_N, new_balance_N, obj, user)


def create_jejepay_record(user, amount_N, ref_no, obj):
    if hasattr(obj, "order_balance_N"):
        obj_type = "order"
    else:
        obj_type = "booking"
    SokoPay.objects.create(user = user, amount = amount_N, purchase_type_1 = 'SokoPay Refund',
                           purchase_type_2 = 'Add', ref_no = ref_no, bank = 'SokoPay', teller_no = obj.tracking_number,
                           status = 'Approved',  message = 'Refund for %s %s' %(obj_type, obj.tracking_number))


def card_pay_validation(request, txnref, shop_or_ship = None):
    kwargs = ({'txnref': txnref, 'payRef': request.POST['payRef'], 'retRef': request.POST['retRef']})
    if shop_or_ship != None:
        if shop_or_ship == "shopping":
            kwargs.update({'order_placement': 'order_placement'})
        else:
            kwargs.update({'shipment_placement': 'shipment_placement'})
    purchase_record = get_object_or_404(SokoPay, ref_no = request.POST["txnref"])
    response = webservice_requery(request, request.user.username, purchase_record.id)
    kwargs.update({'ResponseDescription': response, "requery": True})
    purchase_record = update_balance(request, **kwargs)

    return response


def generate_interswitch_hash(**kwargs):
    #Interswitch Config Details
    global product_id, pay_item_id, mac_key

    txn_ref = kwargs["txn_ref"]
    product_id = product_id#"4325"#kwargs["product_id"]
    amount = kwargs["amount"]
    mac_key = mac_key#"65FEBAC2436D976138274713A7FF6A29FFFA8D7D7A2FDEA141B361CE1A955393D876487B679CD8708F2467CCE9C44FA07155CD6BD63104D5A31A03D2B931534B"

    if kwargs.has_key("requery"):
        #for requery of pending approval card payments
        #val_to_hash = txn_ref + product_id + mac_key
        val_to_hash =  product_id + txn_ref + mac_key
    else:
        #for card payments
        pay_item_id = pay_item_id#"101"
        #site_redirect_url = "http://zaposta.elasticbeanstalk.com/shopping/epay-confirmation/"
        #site_redirect_url = kwargs['site_redirect_url']
        site_redirect_url = kwargs['site_redirect_url']#site_redirect_url_epay_confirmation
        val_to_hash = txn_ref + product_id + pay_item_id + str(amount) + site_redirect_url + mac_key
        #print "txn_ref: ", txn_ref
        #print "product_id: ", product_id
        #print "pay_item_id: ", pay_item_id
        #print "amount: ", amount
        #print "site_redirect_url: ", site_redirect_url
        #print "mac_key: ", mac_key
        #print "val_to_hash: ", val_to_hash

    return hashlib.sha512(val_to_hash).hexdigest()


def show_transaction_response(request, response, txnref):
    #try:
    #    msg = InterswitchResponse.objects.get(response_code = request.POST['resp'])
    #except:
    #    msg = "Unsuccessful"ResponseDescription
    messages.error(request, "Oh No! Your card payment was not successful")
    messages.error(request, "Reason: %s" %response)
    messages.error(request, "Reference No:  %s" %txnref)
    messages.error(request, "Please try again or use a different payment option.")


def webservice_requery(request, username, credit_purchase_id):
    credit_purchase = get_object_or_404(SokoPay, id = credit_purchase_id)

    txn_ref                 = credit_purchase.ref_no
    amount                  = credit_purchase.amount_plus_surcharge()

    #product_id, hash_val = generate_interswitch_hash(**{"txn_ref": txn_ref, "amount": amount})
    product_id, hash_val = credit_purchase.requery_hash()

    #url = 'https://stageserv.interswitchng.com/test_paydirect/api/v1/gettransaction.json'
    url = 'https://webpay.interswitchng.com/paydirect/api/v1/gettransaction.json'
    payload = {'productid': product_id, 'transactionreference': txn_ref, 'amount': amount}
    #print payload
    header_vars = {'Hash': hash_val}
    req = requests.get(url, params=payload, headers=header_vars, verify = False)
    jsonResponse = req.json()
    #print "jsonResponse", jsonResponse
    response = jsonResponse[u'ResponseDescription']

    return response


def purchase_credit(request, order=None, shipment=None, **kwargs):
    tracking_number = None
    if order != None:
        txn_ref = creditpurchase_ref(request, order.id)
        tracking_number = order.tracking_number
    elif shipment != None:
        txn_ref = creditpurchase_ref(request, shipment.id)
        tracking_number = shipment.tracking_number
    else:
        txn_ref = creditpurchase_ref(request)

    form = SokoPayForm()
    todaysdate  = datetime.now()

    template_name = 'soko_pay/card-pay.html'
    #template_name = 'shopping_client/card-pay.html'

    if request.method == "POST":
        ##for mobile app
        if kwargs.has_key("source") and kwargs["source"] == "mobileApp":
            cust_id                 = kwargs["user_id"]
            cust_name               = kwargs["full_name"]
        else:
            cust_id                 = request.user.id
            cust_name               = request.user.get_full_name()

        pay_type                    = "card_payment"

        if kwargs.has_key("paypal"):
           pay_type             = "paypal"
           # actual_amount      = float(kwargs['markedup_amount'])
           txn_ref              = txn_ref
           bank                 = "Paypal"
           template_name_1      = "shopping_client/paypal-data.html"
           purchase_type_1      = "Paypal"
           receiver_mail        = kwargs['receiver_mail']


        try:
            markedup_amount         = request.POST['amount']
            txn_ref                 = request.POST['txn_ref']
            actual_amount           = request.POST['actual_amount']
            site_redirect_url       = request.POST['site_redirect_url']
            #print "here 1"
        except:
            markedup_amount         = kwargs['markedup_amount']
            actual_amount           = kwargs['actual_amount']
            txn_ref                 = txn_ref
            site_redirect_url       = kwargs['site_redirect_url']
            #print site_redirect_url


        #Create record in db for "valid" form data

        form = SokoPayForm({'user': cust_id, 'amount': actual_amount, 'purchase_type_1': 'Card Payment',
                           'purchase_type_2': 'Add', 'ref_no': txn_ref, 'bank': 'Interswitch'})
        #print kwargs
        if form.is_valid():
            #add_credit = form.cleaned_data['amount']
            #ref_no = form.cleaned_data['ref_no']
            #purchase_type_2 = form.cleaned_data['purchase_type_2']
            if actual_amount >= 25 or markedup_amount >= 25:# and purchase_type_1 == "Card Payment":
                others = form.save(commit = False)
                if tracking_number != None:
                    others.teller_no = tracking_number
                #others.amount = amount_val
                others.save()
                #form.save(
                #form.save()

                #Generate hash value to send to GTPay
                #hash_val = generate_gtpay_hash(**{"gtpay_tranx_id": gtpay_tranx_id, "gtpay_tranx_amt": gtpay_tranx_amt, "gtpay_tranx_noti_url": gtpay_tranx_noti_url})
                hash_val = ''
                if not kwargs.has_key("paypal"):
                    hash_val = generate_interswitch_hash(**{"txn_ref": txn_ref, "amount": markedup_amount, 'site_redirect_url': site_redirect_url})
                #print "hash_val %s" %hash_val
                #print "credit purchase amount: %s" %amount
                return render(request, 'soko_pay/interswitch-data.html',
                                          {'hash_val': hash_val,'amount': markedup_amount,
                                           'txn_ref': txn_ref,'cust_id': cust_id, 'site_redirect_url': site_redirect_url,
                                            'cust_name': cust_name, 'pay_type': pay_type,
                                            'product_id': product_id, 'purchase_url': purchase_url, 'rest_json': rest_json},
                                        )
            else:
                alert = "Please enter a minimum amount of =N=25.00."
                return render(request, template_name,
                                          {'alert': alert, 'order': order, 'shipment': shipment,
                                           'txn_ref': txn_ref, 'todaysdate': todaysdate},
                                          )
        else:
            #print form.errors
            alert = "Kindly enter the amount in numbers without the Naira symbol and any comma."
            return render(request, template_name,
                                      {'alert': alert, 'order': order, 'shipment': shipment,
                                       'txn_ref': txn_ref, 'todaysdate': todaysdate},
                                      )
    else:
        return render(request, template_name,
                                  {'order': order,'shipment': shipment,
                                   'txn_ref': txn_ref,
                                   'todaysdate': todaysdate},
                                  )


# -----------------------------------------------------------------
# This block of functions help determine the costs associated with each of the delivery method options


def get_packages(request):
     return ShippingPackage.objects.filter(user = request.user, ordered = False, deleted = False)


def get_no_of_packages(request):
     return get_packages(request).count()


#return all the items in the current user's cart
def get_cart_items(request):
     #if request.user.is_authenticated():
     #     return ShipmentItem.objects.filter(user = request.user, cart_id = _cart_id(request))
     #else:
     # country = request.COOKIES['country']
     # return ShipmentItem.objects.filter(cart_id = _cart_id(request), country = country)
    #country = request.COOKIES.get('country', 'us')
    #return ShippingItem.objects.filter(user = request.user, country = country, deleted = False)
    # print "cart items unassigned......", ShippingItem.objects.filter(user = request.user, ordered = False, deleted = False)
    shipping_origin        = request.session['shipping_origin']
    shipping_destination   = request.session['shipping_destination']
    return ShippingItem.objects.filter(user = request.user, origin = shipping_origin, destination = shipping_destination, ordered = False, deleted = False, item_type="Regular", package=None)


#determine total value of items in current user's cart
def item_cart_value_total(request):
    #item_value_total = get_cart_items(request).aggregate(total=Sum(F('total_value') * F('quantity'), output_field = FloatField()))['total']
    item_value_total = get_cart_items(request).aggregate(total=Sum(F('total_value'), output_field = FloatField()))['total']
    return item_value_total
     # cart = get_cart_items(request)
     # for item in cart:
     #      if item.total_value is not None:
     #           item_value_total += (float(item.total_value) * item.quantity)
     # return item_value_total

#determine the total dollar value of current user's cart
def cartWorth(request):
     cart_worth = item_cart_value_total(request)
     return cart_worth

#determine the total weight of boxes selected from the "Select Box" tab by the current user
def total_SelectBoxWeight(request):
     select_box_weight = 0
     packages = get_packages(request)
     for box in packages:
          #if box.box_weight is None:
          #     box_weight = 0
          #else:
          #     box_weight = box.box_weight
          #select_box_weight += float(box_weight)
          select_box_weight += float(box.box_weight_higher())
     return select_box_weight

#determine the total weight of the weight values entered in the "Enter Dimensions" tab by the current user
def total_EnterDimensionWeight(request):
     enter_dimension_weight = 0
     packages = get_packages(request)
     for pkg in packages:
          if pkg.box_weight_Actual is None:
               weight = 0
          else:
               weight = pkg.box_weight_Actual
          enter_dimension_weight += float(weight)
     return enter_dimension_weight


#determine the Shipping Weight of the current user's cart
def shipping_Weight(request):
     #totalSelectBoxWeight          = total_SelectBoxWeight(request)
     #totalEnterDimensionsWeight    = total_EnterDimensionWeight(request)
     #totalLWHWeight                = total_EnterDimension_dimensionalWeight(request)
     #totalDimensionalWeight        = [totalEnterDimensionsWeight, totalLWHWeight]
     #greatestDimensionalWeight     = max(totalDimensionalWeight)
     #total_weight = totalSelectBoxWeight + greatestDimensionalWeight
     #return total_weight
     return total_SelectBoxWeight(request)


def pkg_Actual_Dim_Weights(packages):
    total_actual_weight = packages.aggregate(total=Sum('box_weight_Actual'))['total']
    total_actual_weight_k = packages.aggregate(total=Sum('box_weight_Actual_K'))['total']
    total_dim_weight = packages.aggregate(total=Sum('box_weight_Dim'))['total']
    total_dim_weight_k = packages.aggregate(total=Sum('box_weight_Dim_K'))['total']

    return total_actual_weight, total_actual_weight_k, total_dim_weight, total_dim_weight_k


# This block of functions ends here
# -----------------------------------------------------------------


'''Customer Address Book'''

def get_office_pick_up_address(customer, city):
    addresses = AddressBook.objects.filter(user = customer, city = city)
    if addresses:
        return addresses[0].id, addresses[0]
    return False


officePickUpAddresses = {"Ikeja": {"street": "No 14, Ladipo Kuku Street", "town_area": "Off Allen Avenue", "telephone": "08102723294", "city": "Ikeja", "state": "Lagos", "country": "Nigeria"},
                       "Yaba": {"street": "No 13, Hughes Avenue, Alagomeji", "town_area": "Off Herbert Macaulay way", "telephone": "08102723294", "city": "Yaba", "state": "Lagos", "country": "Nigeria"},
                        "Ikoyi": {"street": "No 138, Awolowo Road", "town_area": "", "telephone": "","city": "Ikoyi", "state": "Lagos", "country": "Nigeria"},
                        "Lagos Island": {"street": "No 27, Kakawa Street", "town_area": "Behind CMS Bookshop", "telephone": "","city": "Lagos Island", "state": "Lagos", "country": "Nigeria"}}


def create_office_pick_up_address(user, city):
    matching_address = officePickUpAddresses[city]
    print "selected city.....", matching_address

    address,status = DeliveryAddress.objects.get_or_create(user = user, title = user.useraccount.title, first_name = user.first_name, last_name = user.last_name,
                                                    telephone = matching_address["telephone"], address = "%s, %s" %(matching_address["street"], matching_address["town_area"]), city = matching_address["city"],
                                                    state = matching_address["state"], country = matching_address["country"])


    return address.id, address


def selected_delivery_address_id(user, dvm, delivery_city):
    if dvm in ['AF - OP', 'SF - OP', 'EX - OP']:
        address_id = create_office_pick_up_address(user, delivery_city)[0]
    elif dvm in ['AF - AP', 'SF - AP', 'EX - AP']:
        delivery_loc = get_list_or_404(DropOffLocation, city = delivery_city, courier = "RedStar")[0]
        #address_id = Fedex_office_pickup_address(user, fedex_loc)[0]
        address_id = create_office_pick_up_address(user, delivery_loc)[0]
    return address_id


def get_customer_addresses(request, country):
    print 'get_customer_addresses | country: ',country
    return AddressBook.objects.filter(user = request.user, country=country)
'''Customer Address Book'''


# def __init__(self, marketing_member, origin, destination, prefix, char_length):

def update_pkg_values(marketing_member, origin, destination, pkg, costcalc_obj, initial, model_class, insure, payment_type):
    #print 'updating pkg values'
    #model_class_name = model_class.__name__

    pkg.ordered = True
    pkg.payment_method = payment_type

    # if initial == "EX":
    #     pkg.shipment_type = "export"
    # else:
    #     pkg.shipment_type = "import"


    pkg.tracking_number =  tracking_number = booking_ref = TrackingNumber(marketing_member, origin, destination, initial, 5).tracking_no(model_class)
    pkg.costcalc_instance = costcalc_obj

    if insure:
        pkg.user_total_payable_D += pkg.insurance_fee_D
        pkg.user_total_payable_N += pkg.insurance_fee_N

        pkg.admin_total_payable_D += pkg.insurance_fee_D
        pkg.admin_total_payable_N += pkg.insurance_fee_N

    if payment_type in ["Payment on hold", "Bank Deposit"]:
        pkg.balance_D = pkg.admin_total_payable_D
        pkg.balance_N = pkg.admin_total_payable_N
    pkg.save()
    return tracking_number


def update_pkg_total_value(model, package):
    #if model.__name__ == "ShippingPackage":
    if package.shippingitem_set.all():
        total_pkg_value = package.shippingitem_set.all().aggregate(Sum('total_value'))['total_value__sum']
        model.objects.filter(pk = package.pk).update(total_package_value = total_pkg_value)
    # elif model.__name__ == "ExportPackage":
    #     total_pkg_value = package.exporttitem_set.all().aggregate(Sum('naira_value'))['naira_value__sum']
    #     model.objects.filter(pk = package.pk).update(naira_value = total_pkg_value)


def marketing_member(request):
    try:
        marketing_member = request.user.useraccount.marketer 
    except Exception as e:
        try:
           marketing_member = request.marketing_member 
        except:
            
            # marketing_member = MarketingMember.objects.get(pk=9)
            # marketing_member = MarketingMember.objects.all()[0]
            marketing_member = MarketingMember.objects.get(pk=1)

    return marketing_member


def get_marketing_member_user(request, username, email=None):
    user = None
    '''Return user depending on which marketing_member they belong to'''
    try:
        mm = subscriber_marketer(request)
        if email:
            user = get_object_or_404(User, email = email, useraccount__marketer = mm)
        else:
            user = get_object_or_404(User, username = username, useraccount__marketer = mm)
    except:
        '''for localhost with no marketing_member configured'''
        user = get_object_or_404(User, username = username)
    return user


def marketingmember_costcalc(request,lb_country):
    # print "country:",lb_country
    # marketingmember = MarketingMember.objects.all()[0] #delete after confirmation
    marketingmember = marketing_member(request)
    # print "mm_costcalc:",marketingmember
    # return marketingmember.costcalcsetting
    # print "lb_country:",lb_country
    cst_setting = CostCalcSettings.objects.get(marketer=marketingmember,country=lb_country)
    return cst_setting


def create_obj_costcalc(request,lb_country):
    # print "look here:",lb_country
    lb_country = lb_country
    # print "the country: ",lb_country
    package = request.session.get('pkg')
    # print "the package: ",package
    #create cost calc instance for order
    orderCostCalc = ExportObjCostCalcSettings()
    try:
        costcalc = marketingmember_costcalc(request,lb_country)
    except:
        marketing_member = package.shipping_chain.subscriber.marketingmember
        # print "Mm: ",marketing_member
        costcalc = CostCalcSettings.objects.get(marketer=marketing_member,country=lb_country)
    #costcalc = get_object_or_404(CostCalcSettings, pk=1)
    for field in costcalc._meta.fields:
        # print field
        #setattr(orderCostCalc, field.name, getattr(product.order, field.name))
        setattr(orderCostCalc, field.name, getattr(costcalc, field.name))

    orderCostCalc.id = None
    orderCostCalc.save()

    return orderCostCalc
    #obj.costcalc_instance = orderCostCalc
    #return obj, orderCostCalc


def get_marketing_member_shipping_rate(request, origin, destination, shipping_method, weight_kg):
    package = request.session.get('package')
    # print "package: ",package
    # print "am here again"
    # print "MM: ",marketingmember
    # print 'origin: ',origin
    # print 'destination again: ',destination
    try:
        marketingmember = marketing_member(request)
        shipping_rate = marketingmember.get_route_delivery_method_range_rate(origin, destination, shipping_method, weight_kg)
    except:
        marketingmember = package.shipping_chain.subscriber.marketingmember
        shipping_rate = marketingmember.get_route_delivery_method_range_rate(origin, destination, shipping_method, weight_kg)
    print "MM: ",marketingmember
    print "the rate: ",shipping_rate
    return shipping_rate



def region_local_freight_costs(request, region, weight_kg, country):
    weight_kg = math.ceil(weight_kg)
    print "weight: ",weight_kg, region
    local_freight_cost_D = local_freight_cost_N = 0
    print 'region: ',region
    if weight_kg >= 1: #min weight is 1kg
        '''dropoff offered locations'''
        if region == None:
            return 0, 0
        else:
            try:
                local_distributor = LocalDistributorPrice.objects.get(region = region, weight = weight_kg, weight_unit = 'kg')
                print "ldist:", local_distributor
                mark_up = local_distributor.mark_up_value
                local_freight_cost_N = local_distributor.price + ((mark_up * local_distributor.price) / 100)
                ld_country = local_distributor.region.courier.country.name
                print "ld_country" , ld_country
                print "local_freight: ",local_freight_cost_N
            except Exception as e:
                print 'e: ',e
                '''for highest value weight in region. Calculate price/kg'''
                distributor_max_weight_kg = LocalDistributorPrice.objects.filter(region = region, weight_unit = 'kg').aggregate(Max('weight'))['weight__max']
                print "max-weight:",distributor_max_weight_kg
                local_distributor = LocalDistributorPrice.objects.get(region = region, weight = distributor_max_weight_kg, weight_unit = 'kg')
                mark_up = local_distributor.mark_up_value
                print 'local_distributor.price: ',local_distributor.price
                price_per_kg = local_distributor.price / float(local_distributor.weight)
                print 'price_per_kg: ',price_per_kg
                ld_country = local_distributor.region.courier.country.name
                local_freight_cost_N = round(price_per_kg * weight_kg, 2) + (mark_up * round(price_per_kg * weight_kg, 2) / 100)
                print "LCFN:", local_freight_cost_N

            #if request.marketing_member:
            #      #dollar_exchange_rate = request.marketing_member.dollar_exchange_rate
            if country == "United States":
                country = local_distributor.region.courier.country.name

            print "cty: ",country
            costcalc = marketingmember_costcalc(request,ld_country)
            local_freight_cost_D = round(local_freight_cost_N / float(costcalc.dollar_exchange_rate), 2)
            print "LFCD: ",local_freight_cost_D
            #else:
            #     local_freight_cost_D = 0
            # local_costcalc = marketingmember_costcalc(request,country)
            # print "LCC: ",local_costcalc
            # local_freight_cost_N = thirty_percent(round(local_freight_cost_D * float(local_costcalc.dollar_exchange_rate), 2))
            # print "LFCN: ",local_freight_cost_N
    print "see here"
    return  local_freight_cost_D,  local_freight_cost_N


#def get_local_freight_from_state(request, weight_lbs, state, country):
def get_local_freight_from_state(request, weight_lbs, location_id):
    location = LocalDistributorLocation.objects.get(pk = location_id)
    #location = LocalDistributorLocation.objects.filter(state = state, country = country)[0]
    #location = LocalDistributorLocation.objects.filter(state = state, country = country)[0]
    print 'location: ',location
    region = location.region
    shipping_origin = request.session.get('shipping_origin',"None")
    shipping_destination = request.session.get('shipping_destination',"None")

    if shipping_origin == 'United States':
        lb_country = shipping_destination
    elif request.session.has_key('lb_country'):
        lb_country = request.session.get('lb_country')
    else:
        lb_country = shipping_origin

    weight_kg = weight_lbs * 0.453592 #lb_kg_factor
    local_freight_cost_D, local_freight_cost_N = region_local_freight_costs(request, region, weight_kg, lb_country)
    return local_freight_cost_D, local_freight_cost_N


def get_local_freight_from_state_hd(request, weight_lbs, state, country):
    print 'get_local_freight_from_state_hd | weight_lbs, state, country', weight_lbs, state, country
    location = LocalDistributorLocation.objects.filter(state = state, country = country)[0]
    print 'location: ',location
    region = location.region

    shipping_origin = request.session.get('shipping_origin',"None")
    shipping_destination = request.session.get('shipping_destination',"None")

    if shipping_origin == 'United States':
        lb_country = shipping_destination
    elif request.session.has_key('lb_country'):
        lb_country = request.session.get('lb_country')
    else:
        lb_country = shipping_origin

    weight_kg = weight_lbs * 0.453592 #lb_kg_factor
    local_freight_cost_D, local_freight_cost_N = region_local_freight_costs(request, region, weight_kg, lb_country)
    return local_freight_cost_D, local_freight_cost_N


#def get_office_pickup_locations(request, origin, destination, country, state=None):
def get_office_pickup_locations(request, origin, destination, direction):
  mm = marketing_member(request)
  try:
    return mm.get_route_distributors_locations(origin, destination, direction)
  except Exception as e:
    print "get_office_pickup_locations :", e
    return None


def fetch_country_regions(country):
    regions = world_geo_data.Region.objects.filter(country__name = country).values_list('name', 'name')
    return regions


def get_pkgs_shipping_related_costs(request, packages):
    cost_calc                      = marketingmember_costcalc(request)
    exchange_rate                  = cost_calc.dollar_exchange_rate
    #print packages.values_list('id')
    total_shipping_cost_D = packages.aggregate(total = Sum(F('local_freight_D')))['total']# + F('intl_freight_D') + F('courier_cost_D'),))#['total']
    #print 'total_shipping_cost_D: ',total_shipping_cost_D
    total_shipping_cost_N = total_shipping_cost_D * exchange_rate

    insurance_fee_D = packages.aggregate(total = Sum('insurance_fee_D'))['total']
    insurance_fee_N = insurance_fee_D * exchange_rate

    total_payable_D = total_shipping_cost_D

    if request.session.has_key('export_insure'):
        total_payable_D += insurance_fee_D

    total_payable_N = total_payable_D * exchange_rate

    return total_shipping_cost_D, total_shipping_cost_N, insurance_fee_D, insurance_fee_N, total_payable_D, total_payable_N


def paginate_list(request, objects_list, num_per_page):
    paginator   =   Paginator(objects_list, num_per_page) # show number of jobs per page
    page  = request.GET.get('page')
    try:
        paginated_list  = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer, deliver first page
        paginated_list   =   paginator.page(1)
    except  EmptyPage:
        #if page is out of range(e.g 9999), deliver last page of results
        paginated_list      =   paginator.page(paginator.num_pages)
    return paginated_list


def get_context_dicts(request, packages):
    context = {}

    shipping_origin        = request.session.get('shipping_origin',"None")
    shipping_destination   = request.session.get('shipping_destination',"None")

    lb_country = request.session.get('lb_country')

    pick_up_charge_D = packages.aggregate(Sum('pick_up_charge_D'))['pick_up_charge_D__sum']
    pick_up_charge_N = packages.aggregate(Sum('pick_up_charge_N'))['pick_up_charge_N__sum']

    freight_local_D = packages.aggregate(Sum('local_freight_D'))['local_freight_D__sum']
    freight_local_N = packages.aggregate(Sum('local_freight_N'))['local_freight_N__sum']

    freight_intl_D = packages.aggregate(Sum('intl_freight_D'))['intl_freight_D__sum']
    freight_intl_N = packages.aggregate(Sum('intl_freight_N'))['intl_freight_N__sum']

    courier_cost_D = packages.aggregate(Sum('courier_cost_D'))['courier_cost_D__sum']
    courier_cost_N = packages.aggregate(Sum('courier_cost_N'))['courier_cost_N__sum']

    '''For Export'''
    if courier_cost_D > 0:
        freight_intl_D += courier_cost_D
        freight_intl_N += courier_cost_N
    total_weight_Actual = packages.aggregate(Sum('box_weight_Actual'))['box_weight_Actual__sum']
    total_weight_Actual_K = packages.aggregate(Sum('box_weight_Actual_K'))['box_weight_Actual_K__sum']

    total_weight_Dim = packages.aggregate(Sum('box_weight_Dim'))['box_weight_Dim__sum']
    total_weight_Dim_K = packages.aggregate(Sum('box_weight_Dim_K'))['box_weight_Dim_K__sum']

    service_charge_D = packages.aggregate(Sum('service_charge_D'))['service_charge_D__sum']
    service_charge_N = packages.aggregate(Sum('service_charge_N'))['service_charge_N__sum']

    balance_D = packages.aggregate(Sum('balance_D'))['balance_D__sum']
    balance_N = packages.aggregate(Sum('balance_N'))['balance_N__sum']

    total_D = packages.aggregate(Sum('admin_total_payable_D'))['admin_total_payable_D__sum']
    total_N = packages.aggregate(Sum('admin_total_payable_N'))['admin_total_payable_N__sum']

    VAT_charge_D = packages.aggregate(Sum('VAT_charge_D'))['VAT_charge_D__sum']
    VAT_charge_N = packages.aggregate(Sum('VAT_charge_N'))['VAT_charge_N__sum']

    insurance_fee_D = packages.aggregate(Sum('insurance_fee_D'))['insurance_fee_D__sum']
    insurance_fee_N = packages.aggregate(Sum('insurance_fee_N'))['insurance_fee_N__sum']

    try:
      package_owner = packages[0].user.get_full_name()
    except:
      try:
          package_owner = request.user.get_full_name()
      except:
          package_owner = ''

    current_datetime = datetime.now()

    context.update({'freight_local_D':freight_local_D, 'freight_local_N':freight_local_N,
    'freight_intl_N':freight_intl_N, 'freight_intl_D':freight_intl_D, 'service_charge_D':service_charge_D,
    'service_charge_N':service_charge_N,'balance_D':balance_D, 'balance_N':balance_N,
    'total_actual_weight': total_weight_Actual,'total_actual_weight_k': total_weight_Actual_K,
    'total_dim_weight': total_weight_Dim,'total_dim_weight_k': total_weight_Dim_K, 'packages':packages,
    'owner': package_owner,'pickup_charge_N':pick_up_charge_N, 'pickup_charge_D':pick_up_charge_D,
    'total_N':total_N, 'total_D':total_D,'VAT_D':VAT_charge_D, 'VAT_N':VAT_charge_N,
    'insurance_fee_D': insurance_fee_D, 'insurance_fee_N': insurance_fee_N,
    'current_datetime': current_datetime, 'lb_country':lb_country})
    return context


def firstStringCharisI(text):
    return text[0] == "I"


def sokohali_sendmail(request, user, title, text, pkg=None):
    mm = marketing_member(request)
    emailtext = mm.email_text
    name       = user.first_name
    to         = [user.email]
    from_email = '{} <{}>'.format(request.storefront_name, request.storefront_email)
    subject = title
    msg_text = render_to_string(text)
    ctx  = {
        'username': name,
        'body': get_template(text).render(Context({'request':request})),
        'request':request,
        'emailtext':emailtext,
        }
    if not pkg == None:
        ctx['body'] = get_template(text).render(Context({'pkg':pkg, 'request':request}))
    message = get_template('base/base_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)


def sokohali_send_notification_email(mm, user, title, text, pkg=None):
    mm = mm
    emailtext  = mm.email_text
    name       = user.first_name
    to         = user.email
    from_email = '{} <{}>'.format(mm.storefront_name, mm.email)
    subject = title
    msg_text = render_to_string(text)
    ctx  = {
        'username': name,
        'body': get_template(text).render(Context({'mm':mm})),
        'emailtext':emailtext,
        }
    if not pkg == None:
        ctx['body'] = get_template(text).render(Context({'pkg':pkg, 'mm':mm}))
    message = get_template('base/mobile_notify_base.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)


def sokohali_subscriber_sendmail(request, user, title, text, pkg=None):
    name       = user.first_name
    to         = [user.email]
    from_email = '{} <{}>'.format('Sokohali', 'info@sokohali.com')
    subject = title
    bcc      = '{} <{}>'.format('Sokohali', 'admin@sokohali.com')
    msg_text = render_to_string(text)
    ctx  = {
        'username': name,
        'body': get_template(text).render(Context({'request':request})),
        'request':request,
        }
    message = get_template('base/base_subscriber_email.html').render(Context(ctx))
    # msg = EmailMessage(subject, message, from_email, to)
    msg = EmailMultiAlternatives(subject, message, from_email, to, bcc)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)


def sokohali_subscriber_mail(request, user, title, text, email):
    name       = user
    to         = [email]
    from_email = '{} <{}>'.format('Sokohali', 'info@sokohali.com')
    subject = title
    msg_text = text
    print "msg_text :",msg_text
    ctx  = {
        'username': name,
        'body': text,
        'request':request,
        }
    message = get_template('base/base_subscriber_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)



def marketer_contactus_mail(request, user, subject, message, email):
    name       = user
    to         = 'info@sokohali.com'
    from_email = email
    subject = subject
    msg_text = message
    print "msg_text :",msg_text
    ctx  = {
        'username': name,
        'body': text,
        'request':request,
        }
    message = get_template('base/base_subscriber_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)



def subscriber_contactus_mail(request, user, subject, text, email):
    # to = ["uchechukwu.ca@gmail.com"]
    mm = marketing_member(request)
    mrt_mail = mm.email
    # print "mrt_mail :", mrt_mail
    name = user
    to =[mrt_mail]
    from_email = email
    subject = subject
    text = text
    ctx  = {
        'username': name,
        'body':text,
        'request':request,
        }
    
    message = get_template('base/base_subscriber_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    # msg = EmailMessage('Cheap Shipping', 'dfhfdhxfh', 'donkripton@yahoo.com', ["uchechukwu.ca@gmail.com"])
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)
    # return HttpResponse(msg)


def subscriber_contactus_mail_volk(request, user, subject, text, email, phone_number):
    # to = ["uchechukwu.ca@gmail.com"]
    mm = marketing_member(request)
    mrt_mail = mm.email
    # print "mrt_mail :", mrt_mail
    name = user
    to =[mrt_mail]
    from_email = email
    subject = subject
    text = text
    ctx  = {
        'username': name,
        'phone_number':phone_number,
        'body':text,
        'request':request,
        }
    
    message = get_template('base/base_subscriber_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)
    # return HttpResponse(msg)

   
# added until we agree on a more generic solution
def sokohali_batchUpdates_notification(request, title, text, pkg):
    name       = pkg.user.username
    to         = [pkg.user.email]
    subject = title
    try:
        from_email = '{} <{}>'.format(request.storefront_name, request.storefront_email)
    except:
        from_email = 'olaoguns@zoho.com'
    ctx  = {
        'username': name,
        'body': get_template(text).render(Context({'pkg':pkg, 'request':request})),
        'request':request
        }
    print "here"
    message = get_template('base/base_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)



def get_marketing_member_users(request):
    mm = marketing_member(request)
    all_users = UserAccount.objects.filter(marketer = mm)
    return all_users



def initialize_paypal_payment(request, **kwargs):
    # print 'rP: ', request.POST
    # print "session keys: ", request.session.values()
    template_name               = 'general_client/paypal-data.html'
    actual_amount               = kwargs['actual_amount']
    markedup_amount             = kwargs['markedup_amount']
    receiver_email              = kwargs['receiver_mail']
    return_url                  = kwargs['site_redirect_url']
    pay_type                    = 'PayPal'
    txn_ref                     = generate_creditpurchase_ref()

    if request.method == "POST":
        print 'posting to paypal'
        return render(request,template_name,
                      {'amount': markedup_amount,
                       'site_redirect_url': return_url,
                       'receiver_email':receiver_email,
                       'txn_ref':txn_ref,
                        'pay_type': pay_type}
                        )
    else:
        return render(request,template_name,
                      {'amount': markedup_amount,
                       'site_redirect_url': return_url,
                       'receiver_email':receiver_email,
                       'txn_ref':txn_ref,
                        'pay_type': pay_type}
                        )


def flag_packages(request, user_id, action):
    pkgs = []
    mm = marketing_member(request)
    imprt = ShippingPackage.objects.filter(user__useraccount__marketer = mm,  user__useraccount__pk= user_id)
    pkgs = imprt
    #print pkgs
    for pkg in pkgs:
        if action == "flag":
            pkg.status = "Flagged"
            pkg.save()
        else:
            pkg.status = "New"
            pkg.save()
    return pkgs


def get_pkg_by_tracking_no_prefix(tracking_number):
    tracking_no_prefix = tracking_number[0]
    if tracking_no_prefix == "E":
        pkg = get_object_or_404(ExportPackage, tracking_number=tracking_number)
    else:
        pkg = get_object_or_404(ShippingPackage, tracking_number=tracking_number)
    return pkg


def pkg_status_list(tracking_number,pkg_model,user,status):
    status = status
    print "user", user
    obj_status = ActionHistory.objects.create(user=user,obj_id=tracking_number,obj_model_name=pkg_model,
        action=status,obj_description=status)
    return obj_status


def user_manager_history(user,client_id,user_model,status,action):
    history_instance = ActionHistory.objects.create(user=user,obj_id=client_id,obj_model_name=user_model,action=status,obj_description=action)
    return history_instance


def shipment_history(user,pkg_id,pkg_model,status,action):
    history_instance = ActionHistory.objects.create(user=user,obj_id=pkg_id,obj_model_name=pkg_model,action=status,obj_description=action)
    return history_instance

def sokopayment_history(user, payment_ref,pay_model,status,action):
    history_instance = ActionHistory.objects.create(user=user,obj_id=payment_ref,obj_model_name=pay_model,action=status,obj_description=action)
    return history_instance


def checkSubscriber(request):
    try:
        mm = marketing_member(request)
    except:
    	subscriber = request.user.subscriber
    if mm:
        subscriber = mm.subscriber
        #WHM = subscriber.get_warehouses()
        try:
            WHM = subscriber.warehousemember
            print WHM
        except:
            WHM = None
        try:
            Shipper = subscriber.shippingmember
        except:
            Shipper = None
        try:
            clearing_agent = subscriber.customclearingagent
        except:
            clearing_agent = None
        if WHM and Shipper and clearing_agent:
            client = "marketer whole chain"
        elif WHM and Shipper:
            client =  "marketer, WHM and Shipper"
        elif WHM and clearing_agent:
            client =  "marketer, WHM and clearing_agent"
        elif WHM:
            client =  "marketer and WHM"
        elif Shipper and clearing_agent:
            client =  "marketer, Shipper and clearing_agent"
        elif Shipper:
            client =  "marketer and Shipper"
        elif clearing_agent:
            client =  "marketer and clearing_agent"
        else:
            client =  "Ordinary marketer"
    else:
        WHM = subscriber.get_warehouses()
        Shipper = subscriber.get_shippers()
        clearing_agent = subscriber.get_clearing_agents()
        if WHM and Shipper and clearing_agent:
            client =  "WHM, Shipper, clearing_agent."
        elif WHM and Shipper:
            client =  "WHM and Shipper"
        elif WHM and clearing_agent:
            client =  "WHM and clearing_agent"
        elif WHM:
            client =  "WHM"
        elif Shipper and clearing_agent:
            client =  "Shipper and clearing_agent"
        elif Shipper:
            client =  "Shipper"
        elif clearing_agent:
            client =  "clearing_agent"
        else:
            client =  "Ordinary subscriber"
    return client

def inv_history(user,client_id,user_model,status,action):
    history_instance = ActionHistory.objects.create(user=user,obj_id=client_id,obj_model_name=user_model,action=status,obj_description=action)
    return history_instance