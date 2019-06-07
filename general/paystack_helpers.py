from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from general.custom_functions import marketingmember_costcalc, marketing_member
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse


# paystack_secret_key = "sk_test_a131298bbb05eab5322f639c7a3c89a48d0202d1"  
# paystack = Paystack(secret_key=paystack_secret_key)
# jumzy's   paystack_secret_key = "sk_test_9fe140b2bf798accdc2aade269cac47bc2de7ecc"
paystack_secret_key = "sk_live_f01aa6eefc33918ceb59eaf7f6d0789cac72c93c"
# paystack_secret_key = 'sk_test_21bc0443ebf15694ca9b48445bffd01ab8243c28'

paystack = Paystack(secret_key=paystack_secret_key)

local_markup_percentage    = round(1.5 / 100.00, 4)
intl_markup_percentage     = round(3 / 100.00, 4)

def get_markup_charge(request):
    markup_percentage    = local_markup_percentage
    markup_min_charge    = 0.3
    return markup_percentage, markup_min_charge, True
    
    
    
    
def initiate_charge_card(request, **kwargs):
    if request.method == "POST":
        markup_percentage, markup_min_charge, is_nigerian_card = get_markup_charge(request)
        txn_desc            = kwargs['txn_desc']
        txn_ref             = kwargs['txn_ref']
        request.session['txn_ref']= txn_ref
        actual_amount_D     = round(kwargs.get('actual_amount', 0), 2)
        request.session['actual_amount_D']=actual_amount_D
        print 'markup_percentage, markup_min_charge: ',markup_percentage, markup_min_charge
        markup_charge_D      = round((float(actual_amount_D) * markup_percentage) + markup_min_charge, 2)
        if is_nigerian_card:
            max_markup_charge_D = 5
            if markup_charge_D > max_markup_charge_D:
                markup_charge_D = max_markup_charge_D
            amount_D             = round(actual_amount_D + markup_charge_D, 2)
            cost_calc            = marketingmember_costcalc(request, 'Nigeria')
            amount_N             = format(amount_D * float(cost_calc.dollar_exchange_rate), '.2f')
            amountz             = amount_D * float(cost_calc.dollar_exchange_rate) * 100
        print "going to paystack to charge card"
        email = request.user.email
        url = 'general:verifyPayment'
        callback_url = request.build_absolute_uri(reverse(url))
        print "callback-url", callback_url
        response = Transaction.initialize(reference=txn_ref, 
                                  amount=amountz, email=email, callback_url=callback_url)
        print 'response:', response
        data = response.get('data')
        print "data:", data
        authorization_code=data['access_code']
        print "access_code", authorization_code
        url = data['authorization_url']
        print 'url', url
    return redirect(url)
    


def verify_payment(request):
    print "rG", request.GET
    ref = request.session['txn_ref']
    response_dict = Transaction.verify(reference=ref)
    data = response_dict.get('data')
    print "data", data
    print "response_dict", response_dict
    amount = data['amount']
    status = data['status']
    response = data['gateway_response']
    print amount, status, response
    # jejepay     = update_jejepay_obj(ref,ref,response)
    # jejepay.amount = amount
    # jejepay.save()
    go_to_url = request.session['dest_namespace_1']
    if go_to_url == None:
        go_to_url = request.session['dest_namespace_2']
        del request.session['dest_namespace_2']
    print "go url:", go_to_url
    del request.session['dest_namespace_1']
    #messages.info(request, response)
    return redirect(request.build_absolute_uri(reverse(go_to_url)+'?jejepay_ref='+ref+'&resp='+status))