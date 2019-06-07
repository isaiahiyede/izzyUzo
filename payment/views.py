from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from sokopay.models import SokoPay, MarketerPayment
from sokohaliAdmin.models import CostCalcSettings
from django.utils import timezone
import json, random, math, string




# Create your views here.

@csrf_exempt
def payment_done(request):
	marketer = marketing_member(request)
	# print "got here"
	# print "session keys: ", request.session.values()

	if request.user.is_authenticated:
	    print "user is logged in"

	    tx = request.GET.get('tx')
	    st = request.GET.get('st')
	    amount = request.GET.get('amt')
	    # user = request.session['user']
	    print "amount -- st -- tx", amount,st,tx

	    # jejepay,created = SokoPay.objects.get_or_create(user=request.user,ref_no = tx,
	    #     payment_gateway_tranx_id = generate_creditpurchase_ref(), status= 'Approved',purchase_type_1="PayPal",
	    #     purchase_type_2="Add", bank="PayPal", amount=amount)

	    payment = MarketerPayment.objects.create(
	        user=request.user.useraccount,
	        payment_channel="PayPal",
	        purchase_type_2="Add",
	        created_at=timezone.now(),
	        message="PayPal Vei Wallet Fund",
	        amount=amount,
	        purchase_type_3="veiwallet",
	        ref_no=tx,
	        status="Approved",
	        marketer=marketer,
	        bank=None,
	        teller_no=tx)


	    all_cost = CostCalcSettings.objects.get(marketer=mm,country="Nigeria")
	    dollarNairaRate = all_cost.dollar_exchange_rate
	    request.user.useraccount.credit_amount_D += (float(amount))
	    request.user.useraccount.credit_amount_N += (float(dollarNairaRate) * float(amount))
	    request.user.useraccount.save()
	   
	return render(request,'payment/done.html')

@csrf_exempt
def payment_canceled(request):
	return render(request,'payment/canceled.html')

def payment_process(request):
	form = PayPalPaymentsForm()
	if request.method == 'POST':

		request.session['user'] = request.user

		rp = request.POST
		amount = float(rp.get('amount'))
		percentage_mark_up = float(2.9 * 100)
		marked_up_amount = percentage_mark_up + amount
		ref_no = rp.get('ref_no')

		paypal_dict = {

			'business':settings.PAYPAL_RECEIVER_EMAIL,
			'amount':marked_up_amount,
			'item':'Fund Vei Wallet',
			'invoice': str(ref_no),
			'currency': 'USD',
			'notify_url':'http://{}{}'.format(host,reverse('paypal-ipn')),
			'return_url':'http://{}{}'.format(host,reverse('payment:done')),
			'cancel_return':'http://{}{}'.format(host,reverse('payment:cancel'))

		}

		form = PayPalPaymentsForm(initial=paypal_dict)

	return render(request,'payment/process.html',{'form':form})

