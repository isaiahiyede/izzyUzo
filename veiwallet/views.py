# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from django.shortcuts import render, redirect
#from paystack.resource import TransactionResource
import string, random, ast, json
# from general.models import UserAccount
# from .models import Bank
# from wallet.account_standing import account_standing, bank_codes, account_standing_new
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
# from wallet.Transfer import Transfer, Miscellaneous
from django.contrib import messages
from django.core.urlresolvers import reverse
from general.views import paginate_list
# from gameplay.models import Gameplay
from django.contrib.auth.decorators import login_required,user_passes_test
from general.staff_access import *
from django.db.models import Q
# from general.custom_functions import *
from django.http import JsonResponse
from sokopay.models import SokoPay, MarketerPayment
from general.custom_passes_test import request_passes_test
from sokohaliAdmin.models import CostCalcSettings
from django.contrib import messages



# Create your views here.
paystack_secret_key = "sk_live_f01aa6eefc33918ceb59eaf7f6d0789cac72c93c"
# paystack_secret_key = 'sk_test_21bc0443ebf15694ca9b48445bffd01ab8243c28'  
paystack = Paystack(secret_key=paystack_secret_key)


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def view_wallet(request):
    try:
        user = UserAccount.objects.get(user=request.user)
    except Exception as e :
        print "e", e
        user = None
    # game    = Gameplay.objects.filter(user=user)
    # balance = account_standing(request,request.user)
    payment = MarketerPayment.objects.filter(user=request.user.useraccount)
    # query = request.GET.get('q')
    # if query:
    #     payment = payment.filter(
    #         Q(ref_no__iexact=query) |
    #         Q(status__icontains=query) |
    #         Q(message__icontains=query) 
    #         )
    wallet = payment
    
    return render(request, 'volkmann/vei_wallet.html', {'wallet':wallet, 'user':user}) 


def generate_purchaseRef():
    rand = ''.join(
             [random.choice(
                 string.ascii_letters + string.digits) for n in range(16)]) 
    return rand

def purchase_ref():
    ref = generate_purchaseRef()#+ "|%s" %obj_id
    return ref

@login_required
def mainPay(request):
	marketer = marketing_member(request)
	print "i got here"
	rp = request.POST
	print 'rp',rp
	if request.method == "POST":
	    bot_catcher = request.POST.get('bot_catcher')
	    print "bot_catcher",bot_catcher
	    payment_method = request.POST.get('payment-method')
	    if bot_catcher != "botty":
	        return redirect(reverse('general:homepage'))
	    try:    
	        value = int(request.POST.get('amount'))
	    except:
	        messages.info(request, 'Invalid amount entered')
	        # return redirect('wallet:wallet')
	        return redirect
	    if payment_method == "bank":
	        # print a
	        random_ref = purchase_ref()
	        
	        bank_payment = MarketerPayment.objects.create(
		    	user=request.user.useraccount,
		    	payment_channel="Bank Payment",
		    	purchase_type_2="Add",
		    	created_at=timezone.now(),
		    	message="Vei Wallet Fund",
				amount=amount,
				ref_no=random_ref,
				marketer=marketer,
				bank=None,
				teller_no=random_ref)

	        payment = MarketerPayment.objects.filter(user=request.user.useraccount)
	        return redirect('wallet:wallet')
	    # if value > 9999:
	    #     messages.info(request, 'You have exceeded the Top up Limit, Pls enter an amount less than 10,000')
	    #     return redirect('wallet:wallet')
	    # print "value", value
	    amount = value
	    # print "amount", amount
	    email = request.user.email
	    
	    #secret_key = 'sk_test_9fe140b2bf798accdc2aade269cac47bc2de7ecc'
	    random_ref = purchase_ref()
	    request.session['ref_no']= random_ref
	    request.session['user']= request.user
	    request.session['amount']= amount
	    url = 'wallet:verify_payment'
	    callback_url = request.build_absolute_uri(reverse(url))
	    print "callback-url", callback_url
	    response = Transaction.initialize(reference=random_ref, 
	                              amount=float(amount * 100), email=email, callback_url=callback_url)
	    # print 'response:', response
	    data = response.get('data')
	    # print "data:", data
	    authorization_code=data['access_code']
	    # print "access_code", authorization_code
	    url = data['authorization_url']
	    # print 'url', url
	    payment = MarketerPayment.objects.create(
	    	user=request.user.useraccount,
	    	payment_channel="Card Payment",
	    	purchase_type_2="Add",
	    	created_at=timezone.now(),
	    	message="Paystack Vei Wallet Fund",
	    	purchase_type_3="veiwallet",
			amount=amount,
			ref_no=random_ref,
			marketer=marketer,
			bank=None,
			teller_no=random_ref)

	    user_acc = request.user.useraccount

	    return redirect(url)
	 
	return render(request, 'volkmann/vei_wallet.html')
   
   
def verify_payment(request):
	mm = marketing_member(request)
	ref = request.session['ref_no']
	response_dict = Transaction.verify(reference=ref)
	data = response_dict.get('data')
	print 'status', data['status']

	if data['status'] == 'success':
	    status = "Approved"
	    user = request.session['user']
	    amount = request.session['amount']
	    all_cost = CostCalcSettings.objects.get(marketer=mm,country="Nigeria")
	    dollarNairaRate = all_cost.dollar_exchange_rate
	    user.useraccount.credit_amount_D += (float(amount) / float(dollarNairaRate))
	    user.useraccount.credit_amount_N += amount
	    user.useraccount.save()
	else:
	    status = data['status']
	bank_record = MarketerPayment.objects.get(ref_no=ref)
	bank_record.status = status
	bank_record.message = data['gateway_response']
	bank_record.save()
	messages.success(request, "You have sucessfully funded your VEI Wallet.")
	del request.session['ref_no']
	del request.session['user']
	del request.session['amount']
	return redirect('wallet:wallet')

