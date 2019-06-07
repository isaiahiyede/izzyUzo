from sokopay.models import SokoPay, MarketerPayment
from sokopay.forms import SokoPayForm
import random
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from datetime import datetime
#from general.paystack import initialize_transaction
from general import flutterwave_helpers, paystack_helpers
from general.custom_functions import marketingmember_costcalc, marketing_member
from sokopay.templatetags.account_standing import account_standing, marketingmember_costcalc
from django.contrib import messages
from general.models import UserAccount
from shipping.models import ShippingPackage

def generate_creditpurchase_ref():
    ref_no = ''
    digits = '1234567890'
    ref_no_length = 9
    for x in range(ref_no_length):
        ref_no += digits[random.randint(0, len(digits) - 1)]
    return ref_no


def creditpurchase_ref(obj_id = None):
    if obj_id != None:
        ref = generate_creditpurchase_ref()#+ "|%s" %obj_id
        while SokoPay.objects.filter(ref_no = ref):
            ref = generate_creditpurchase_ref() + "|%s" %obj_id
        # print "ref",ref
        return ref

    ref = generate_creditpurchase_ref()
    while SokoPay.objects.filter(ref_no = ref):
        ref = generate_creditpurchase_ref()
    # print "ref",ref
    return ref


#def initiate_payment(request, actual_amount, markedup_amount, txn_ref, dest_namespace):
def initiate_payment(request, **kwargs):
    actual_amount    = kwargs['actual_amount']
    #markedup_amount  = kwargs['markedup_amount']
    txn_ref          = kwargs['txn_ref']
    #dest_namespace   = kwargs['dest_namespace']
    # actual_amount           = float(actual_amount)
    # kobo_value              = 100
    # markedup_amount         = actual_amount * kobo_value
    # txn_ref                 = txn_ref
    bank                      = 'PayStack'
    #bank                     = 'Flutterwave'

    #print 'actual_amount: ',actual_amount
    if actual_amount > 0:
        if kwargs.has_key('lb_country'):
            mod_kwargs = {'actual_amount': str(actual_amount), 'txn_ref': txn_ref, #'tracking_number': tracking_number,
                  'bank': bank, 'lb_country': kwargs['lb_country']}
        else:
            mod_kwargs = {'actual_amount': str(actual_amount), 'txn_ref': txn_ref, #'tracking_number': tracking_number,
                      'bank': bank}
        response = create_credit_instance(request, **mod_kwargs)

        #print 'buy_jeje response: ',response

        #callback_url = request.build_absolute_uri(reverse('soko_pay:paystack_verify_transaction', args=[txn_ref, dest_namespace]))
        callback_url = ''
        if response['status'] == 'success':
            # kwargs = {'markedup_amount': str(markedup_amount), 'callback_url': callback_url,
            #       'bank': bank, 'email': request.user.email}
            kwargs.update({'txn_ref': txn_ref})
            print "updated kwargs", kwargs
            return paystack_helpers.initiate_charge_card(request, **kwargs)
            #return flutterwave_helpers.initiate_charge_card(request, **kwargs)
            #return flutterwave_helpers.initiate_charge_card(request, markedup_amount, txn_desc, txn_ref)
            #return initialize_transaction(request, **kwargs)


#def call_initiate_payment(request, amount_paid_N, dest_namespace):
def call_initiate_payment(request, **kwargs):
    if kwargs.has_key('lb_country'):
        amount_paid_D   = kwargs['amount_paid_D']
    #dest_namespace  = kwargs['dest_namespace']
    #callback_url = request.build_absolute_uri(reverse(dest_namespace))

    #actual_amount = import_shipment.admin_total_payable_N
        actual_amount = amount_paid_D
    else:
        actual_amount = kwargs['amount_paid_D']

    txn_ref = creditpurchase_ref()
    kwargs.update({'actual_amount': actual_amount, #'markedup_amount': markedup_amount,
              'txn_ref': txn_ref})


    #return initiate_payment(request, actual_amount, markedup_amount, txn_ref, dest_namespace)
    return initiate_payment(request, **kwargs)

def call_verify_payment(request):
    return flutterwave_helpers.verify_otp(request)


def card_payment(request, **kwargs_dict):
    if 'lb_country' in kwargs_dict:
        actual_amount_D      = kwargs_dict['actual_amount_D']
        print "country: ",kwargs_dict['lb_country']
        lb_country = kwargs_dict['lb_country']
        #exchange_rate        = marketingmember_costcalc(request,lb_country).dollar_exchange_rate
        #actual_amount_D      = round(actual_amount_N / float(exchange_rate), 2)
    else:
        actual_amount_D      = round(kwargs_dict['actual_amount_N'], 2)
    dest_namespace_1     = kwargs_dict['dest_namespace_1']

    request.session['dest_namespace_1'] = dest_namespace_1

    dest_namespace_2     = kwargs_dict['dest_namespace_2']
    request.session['dest_namespace_2']= dest_namespace_2
    txn_desc             = kwargs_dict['txn_desc']

    if not request.POST.has_key('otp') and not request.GET.has_key('resp'):
        #dest_namespace = 'shipping:shipping_payment'
        print "i got here as well"
        if 'lb_country' in kwargs_dict:
            kwargs = {'amount_paid_D': actual_amount_D,
                      'txn_desc': txn_desc, 'lb_country':lb_country}
        else:
            kwargs = {'amount_paid_D': actual_amount_D,
                      'txn_desc': txn_desc}
        print "kwargs", kwargs
        #pay_response = call_initiate_payment(request, **kwargs)
        return call_initiate_payment(request, **kwargs)
    #     print 'pay_response: ',pay_response
    #     response_msg = pay_response['responseMessage']
    #     pay_response_msg = response_msg.lower()
    # 
    #     responsecode = pay_response['responsecode']
    # 
    #     #responsecode ='02'
    #     if responsecode == '02':
    #         '''Validation required'''
    #         pay_response.update({'response_msg': "%s" %response_msg})
    #         return JsonResponse(pay_response)
    # 
    # 
    #     if 'success' in pay_response_msg:
    #         response_dict = {'response_msg': pay_response_msg,}
    #         if 'package_review' in dest_namespace_1:
    #             #pay_response.update({'pkg_placement': 'True'})
    #             response_dict.update({'pkg_placement': 'True', 'jejepay_ref': pay_response['jejepay_ref']})
    #             return JsonResponse(response_dict)
    #         else:
    #             redirect_url_2 = request.build_absolute_uri(reverse(dest_namespace_2))
    #             messages.success(request, "Your card payment of $%s was successful. Thank you." %actual_amount_D)
    #             response_dict.update({'redirect_url': redirect_url_2})
    #             return JsonResponse(response_dict)
    # 
    # 
    #     if not 'success' in pay_response_msg:
    #         if 'pending' in pay_response_msg:
    #             pay_response.update({'response_msg': "Transaction %s." %response_msg})
    #             print 'pay_response here: ',pay_response
    #             return JsonResponse(pay_response)
    #         else:
    #             messages.error(request, "%s" %response_msg)
    #             #print 'card_payment|kwargs_dict: ',kwargs_dict
    #             jejepay_ref = pay_response.get('jejepay_ref')
    #             flutterwave_helpers.update_jejepay_obj(jejepay_ref, None, response_msg)
    #             return JsonResponse({'redirect_url': request.build_absolute_uri(reverse(dest_namespace_1))})
    #             # try:
    #             #     return JsonResponse({'redirect_url': request.build_absolute_uri(reverse(dest_namespace_1))})
    #             # except:
    #             #     print 'request.get_full_path(): ',request.get_full_path()
    #             #     return JsonResponse({'redirect_url': request.get_full_path()})
    #         #return redirect (request.META.get("HTTP_REFERER", reverse('shipping:shipping_payment')))
    # 
    # 
    #     if 'decoded_responsehtml' in pay_response:
    #         return JsonResponse({'redirect_url': pay_response['intl_card_verification_url']})
    # 
    # #print 'actual_amount_N: ',actual_amount_N
    # '''OTP Validation'''
    # if request.POST.has_key('otp'):
    #     print "i got here"
    #     pay_response = call_verify_payment(request)
    #     print "pay-response:",pay_response
    #     response_msg = pay_response['responsemessage']
    #     pay_response_msg = response_msg.lower()
    #     response_dict = {'response_msg': pay_response_msg}
    #     if 'success' in pay_response_msg or 'approved' in pay_response_msg:
    #         try:
    #             redirect_url_2 = request.build_absolute_uri(reverse(dest_namespace_2))
    #             messages.success(request, "Your card payment of $%s was successful. Thank you." %actual_amount_D)
    #             response_dict.update({'redirect_url': redirect_url_2})
    #             return JsonResponse(response_dict)
    #             #return JsonResponse({'redirect_url': redirect_url_2})
    #             #return JsonResponse({'redirect_url': redirect_url_2})
    #         except Exception as e:
    #             print 'e card: ',e
    #             #pass
    #     else:
    #         messages.error(request, "%s" %response_msg)
    #         return JsonResponse({'redirect_url': request.build_absolute_uri(reverse(dest_namespace_1))})
    # 
    #     #response_dict = {'response_msg': pay_response_msg}
    #     if 'confirmation' in txn_desc.lower():
    #         #pay_response.update({'pkg_placement': 'True'})
    #         response_dict.update({'pkg_placement': 'True', 'jejepay_ref': pay_response['jejepay_ref']})
    #     return JsonResponse(response_dict)



def create_credit_instance(request, **kwargs):
    obj_id                  = kwargs.get('obj_id')
    txn_ref                 = kwargs.get('txn_ref')
    tracking_number         = kwargs.get('tracking_number', '')

    cust_id                 = request.user.id
    cust_name               = request.user.get_full_name()

    #markedup_amount         = kwargs['markedup_amount']
    actual_amount           = kwargs['actual_amount']
    txn_ref                 = txn_ref
    #site_redirect_url       = kwargs['site_redirect_url']
    bank                    = kwargs['bank']

    #Create record in db for "valid" form data
    if kwargs.has_key('lb_country'):
        # mm = marketing_member(request)
        # payment = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel='Card Payment',created_at=datetime.now(),
        #                                              amount=actual_amount,ref_no=txn_ref,bank=bank,marketer=mm,teller_no=tracking_number)
        # payment.save()
        return {'status': 'success'}
    else:
        form = SokoPayForm({'user': cust_id, 'amount': actual_amount, 'purchase_type_1': 'Card Payment',
                           'purchase_type_2': 'Add', 'ref_no': txn_ref, 'bank': bank})
        if form.is_valid():
            others              = form.save(commit = False)
            others.teller_no    = tracking_number
            others.save()

            return {'status': 'success'}

        print 'form.errors: ',form.errors
        return {'status': 'fail'}


def create_paypal_instance(request, **kwargs):
    obj_id                  = kwargs.get('obj_id')
    txn_ref                 = kwargs.get('txn_ref')
    tracking_number         = kwargs.get('tracking_number', '')

    cust_id                 = request.user.id
    cust_name               = request.user.get_full_name()

    #markedup_amount         = kwargs['markedup_amount']
    actual_amount           = kwargs['actual_amount']
    txn_ref                 = txn_ref
    #site_redirect_url       = kwargs['site_redirect_url']
    bank                    = kwargs['bank']

    #Create record in db for "valid" form data

    form = SokoPayForm({'user': cust_id, 'amount': actual_amount, 'purchase_type_1':'PP',
                       'purchase_type_2': 'Add', 'ref_no': txn_ref, 'bank': bank, 'status':'Successful',
                       'message':'Applied to package with tracking number -- ' + tracking_number
                       })
    if form.is_valid():
        others              = form.save(commit = False)
        others.teller_no    = tracking_number
        others.save()

        return {'status': 'success'}

    print 'form.errors: ',form.errors
    return {'status': 'fail'}




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
    # if hasattr(obj, "export"):
    #     obj_type = "Export"
    # else:
    #     obj_type = "Import"

    if user == None:
        user = request.user
    else:
        user = user
    SokoPay.objects.create(user = user, amount = amount_N, purchase_type_1 = 'SokoPay Withdrawal',
                           purchase_type_2 = 'Remove', ref_no = ref_no, bank = 'SokoPay', teller_no = obj.tracking_number,
                           status = 'Approved', message = 'Applied to %s' %(obj.tracking_number))

    #add_payment_record_to_objhistory(request, prev_balance_N, new_balance_N, obj, user)

def marketer_payment(request, payment_channel, message, amount, pkg, mm, status):
    payment = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel=payment_channel,created_at=datetime.now(),message=message,
                                            amount=amount,package=pkg,marketer=mm,status=status)
    payment.save()
        


def pay_with_paypal(request, obj, user, amount_to_pay_D):
    useraccount = UserAccount.objects.get(user = user)
    dollar_exchange_rate = obj.costcalc_instance.dollar_exchange_rate 
    amount_to_pay_N         = amount_to_pay_D * float(dollar_exchange_rate)
    obj.balance_D           -= amount_to_pay_D
    obj.balance_N           -= amount_to_pay_N
    obj.balance_paid_D      += amount_to_pay_D
    obj.balance_paid_N      += amount_to_pay_N
    if useraccount.country == "United States":
        amount_N                = amount_to_pay_D
    else:
        amount_N                = amount_to_pay_N

    ref_no = creditpurchase_ref(obj.id)

    paypal_obj = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel="PayPal",created_at=datetime.now(),message='Payment for package -  %s' %(obj.tracking_number),
                                            amount=amount_to_pay_D,package=obj,marketer=marketing_member(request),status="Successful")

    # paypal_obj = SokoPay.objects.create(user = user, amount = amount_to_pay_D, purchase_type_1 = 'PayPal',
    #                        purchase_type_2 = 'Add', ref_no = ref_no, bank = 'PayPal', teller_no = obj.tracking_number,
    #                        status = 'Successful', message = 'Applied to %s' %(obj.tracking_number))

    paypal_obj.save()
    obj.save()
    return obj




def apply_shipping_credit(request, obj, user = None, amount_to_pay_D=None):
    if user == None:
        shipping_credit_N, shipping_credit_D = account_standing(request, request.user)
        user = request.user
    else:
        shipping_credit_N, shipping_credit_D = account_standing(request, user)
    useraccount = UserAccount.objects.get(user = user)
    #convert shipping_credit_D using exchange_rate of obj
    #exchange_rate = country_exchange_rate(obj.country, costcalc_settings())
    #dollar_exchange_rate = marketingmember_costcalc(request).dollar_exchange_rate
    dollar_exchange_rate = obj.costcalc_instance.dollar_exchange_rate
    if not useraccount.country == "United States":
        shipping_credit_D = float(shipping_credit_N) / dollar_exchange_rate
        prev_balance_N = obj.balance_N
    else:
        shipping_credit_N = float(shipping_credit_D) * dollar_exchange_rate
        prev_balance_N = obj.balance_D
    #shipping
    #if hasattr(obj, 'user_total_payable_N'):
    #prev_balance_N = obj.balance_N
    shipping_cost_D = obj.admin_total_payable_D
    shipping_cost_N = obj.admin_total_payable_N

    if amount_to_pay_D == None:

        if shipping_credit_N >= shipping_cost_N:
            obj.balance_D = 0
            obj.balance_N = 0
            obj.balance_paid_D = shipping_cost_D
            obj.balance_paid_N = shipping_cost_N
            #Amount applied
            if useraccount.country == "United States":
                amount_N = shipping_cost_D
            else:
                amount_N = shipping_cost_N
        # else:
        #     if shipping_credit_N > 0:
        #         obj.balance_D          = shipping_cost_D - shipping_credit_D
        #         obj.balance_N          = shipping_cost_N - shipping_credit_N
        #         obj.balance_paid_D = shipping_credit_D
        #         obj.balance_paid_N = shipping_credit_N
        #
        #         #Amount applied
        #         amount_N = shipping_credit_N
    else:
        amount_to_pay_N         = amount_to_pay_D * float(dollar_exchange_rate)
        obj.balance_D           -= amount_to_pay_D
        obj.balance_N           -= amount_to_pay_N
        obj.balance_paid_D      += amount_to_pay_D
        obj.balance_paid_N      += amount_to_pay_N
        if useraccount.country == "United States":
            amount_N                = amount_to_pay_D
        else:
            amount_N                = amount_to_pay_N
        #amount_N                = amount_to_pay_N

    #obj.apply_shipping_credit = True
    if useraccount.country == "United States":
        new_balance_N = obj.balance_D
    else:
        new_balance_N = obj.balance_N

    ref_no = creditpurchase_ref(obj.id)
    mm = marketing_member(request)
    use_shipping_credit(request, amount_N, ref_no, prev_balance_N, new_balance_N, obj, user)
    marketer_payment(request, "SokoPay", "Paid", shipping_cost_D, obj, mm, "Approved")
    obj.save()
    return obj


def update_payment_record_for_packages(request, packages, jejepay_ref=None):
    print 'applying payment'
    if jejepay_ref == None:
        jejepay_ref = request.GET.get('jejepay_ref')

    print 'jejepay_ref: ',jejepay_ref
    #jejepay   = SokoPay.objects.get(ref_no = jejepay_ref)
    #status    = (jejepay.status).lower()
    #jejepay   = MarketerPayment.objects.get(ref_no = jejepay_ref)
    #status    = (jejepay.status).lower()
    mm = marketing_member(request)
    status = request.session['status'].lower()
    #tranx_id = request.session['tranx_id']
    tranx_id = jejepay_ref
    print 'status: ',status
    if 'approved' in status or 'success' in status:
         #import_shipment.save()
         print 'packages 2nd: ',packages

         for pkg in packages:
            print 'pkg.admin_total_payable_D: ',pkg.admin_total_payable_D
            pkg.balance_paid_D  = pkg.user_total_payable_D
            pkg.balance_paid_N = pkg.user_total_payable_N
            pkg.user_total_payable_D=pkg.admin_total_payable_D=pkg.balance_D = 0
            pkg.user_total_payable_N=pkg.admin_total_payable_N=pkg.balance_N = 0
            #apply_shipping_credit(request, pkg)
            pkg.save()
            payment = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel='Card Payment',created_at=datetime.now(),ref_no=jejepay_ref,
                                            amount=pkg.balance_paid_D,package=pkg,marketer=mm,status="Successful",payment_gateway_tranx_id =tranx_id)
            payment.save()
            # jejepay.package = ShippingPackage.objects.get(id=pkg.id)
            # jejepay.save()




def update_paypal_payment_record_for_packages(request, packages):
    print 'applying payment'

    for pkg in packages:
        print "see me up"
        print "amount payable: ",pkg.user_total_payable_D

        jejepay = SokoPay.objects.create(user=request.user,ref_no = pkg.tracking_number,payment_gateway_tranx_id = "N/A",
            purchase_type_1="PayPal",purchase_type_2="Add", bank="PayPal", amount=pkg.user_total_payable_D, teller_no= generate_creditpurchase_ref(),
            message="payment applied for booking with tracking number - " + pkg.tracking_number)

        jejepay.save()

        pkg.balance_paid_D  = pkg.user_total_payable_D
        pkg.balance_paid_N = pkg.user_total_payable_N

        pkg.save()




















