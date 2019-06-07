from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from sokopay.models import SokoPay, MarketerPayment
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime
from django.contrib import messages
from sokopay.forms import SokoPayForm, SokoPayAddForm, MarketerPaymentForm
from sokopay.templatetags.account_standing import account_standing, format_num
from general.custom_functions import country_exchange_rate, costcalc_settings, add_payment_record_to_objhistory, buy_jejepay_credit_deposit_general, remove_from_string, \
                                use_shipping_credit, purchase_credit, firstStringCharisI, remove_from_string, marketing_member, initialize_paypal_payment 
#from general.payment_helpers import apply_shipping_credit
from general import payment_helpers
from general.models import UserAccount
from general.staff_access import staff_check_for_booking
from general.payment_helpers import creditpurchase_ref, create_credit_instance, initiate_payment, call_initiate_payment, update_payment_record_for_packages, \
                                    call_verify_payment
from shipping.models import ShippingPackage, DomesticPackage
from general import flutterwave_helpers
import ast, json
from service_provider.views import request_subscriber
from django.views.decorators.csrf import csrf_exempt
from service_provider.models import MarketingMember
from sokohaliAdmin.models import CostCalcSettings
from django.db.models import Q, Count, Sum
from django.utils import timezone
import json, random, math, string






def generate_purchaseRef():
    rand = ''.join(
             [random.choice(
                 string.ascii_letters + string.digits) for n in range(16)]) 
    return rand


def purchase_ref():
    ref = generate_purchaseRef()#+ "|%s" %obj_id
    return ref


@login_required
def add_funds(request):

    
    template_name = 'soko_pay/add_funds.html'

    ref_no      = creditpurchase_ref(request)
    todaysdate  = datetime.now()
    form        = SokoPayAddForm()
    print request.POST
    if request.method == 'POST':
        form    = SokoPayAddForm(request.POST)
        if form.is_valid():
            print form
            print "here"
            success = buy_jejepay_credit_deposit_general(form)
            if (success):
                username = request.user.username#UserAccount.objects.get(user = request.user).username
                #return redirect (reverse ('userAccount.views.user_jeje_pay_info', args=[username]))
                messages.info(request, "Your soko-pay credit purchase was successful. Our Finance department will approve it shortly after confirmation. Thank you.")
                return redirect (reverse ('soko_pay:user_transactions'))
                #return redirect (reverse ('userAccount:user_jeje_pay_info', args=[username]))
            # print form.errors
            # else:
            #     error_alert = 'Amount Entered must be greater than 0.'
            #     return render(request, "soko_pay/add_funds.html",
            #                               {'error_alert': error_alert, 'form': form, 'ref_no': ref_no,
            #                                'todaysdate': todaysdate, 'user': request.user})

        else:
            print form.errors
            error_alert = 'Please correct the highlighted field(s).'
            return render(request, template_name,
                                      {'error_alert': error_alert, 'form': form, 'ref_no': ref_no,
                                       'todaysdate': todaysdate, 'user': request.user})
        #print form.errors
    return render(request, template_name,
                              {'form': form, 'ref_no': ref_no, 'todaysdate': todaysdate, 'user': request.user})



@login_required(login_url='/volk/login/')
def add_funds_volk(request):

    template_name = 'volkmann/vei_wallet.html'
    mm = marketing_member(request)
    
    ref_no      = creditpurchase_ref(request)
    todaysdate  = datetime.now()
    form        = MarketerPaymentForm()
    print request.POST
    if request.method == 'POST':
        form    = MarketerPaymentForm(request.POST)
        if form.is_valid():
            marketer_form = form.save(commit=False)
            marketer_form.purchase_type_3 = "veiwallet"
            marketer_form.user = request.user.useraccount
            marketer_form.message = "Funding veiwallet"
            marketer_form.marketer = mm
            marketer_form.save()
            # print form
            print "here"
            # success = buy_jejepay_credit_deposit_general(form)
            # if (success):
            username = request.user.username # UserAccount.objects.get(user = request.user).username
            # return redirect (reverse ('userAccount.views.user_jeje_pay_info', args=[username]))
            messages.info(request, "Your vei wallet add credit was successful. Our Finance department will approve it shortly after confirmation. Thank you.")
            return redirect (reverse ('soko_pay:user_transactions'))
            # return redirect (reverse ('userAccount:user_jeje_pay_info', args=[username]))
            # print form.errors
            # else:
            #     error_alert = 'Amount Entered must be greater than 0.'
            #     return render(request, "soko_pay/add_funds.html",
            #                               {'error_alert': error_alert, 'form': form, 'ref_no': ref_no,
            #                                'todaysdate': todaysdate, 'user': request.user})

        else:
            print form.errors
            print form
            error_alert = 'Please correct the highlighted field(s).'
            return render(request, template_name,
                                      {'error_alert': error_alert, 'form': form, 'ref_no': ref_no,
                                       'todaysdate': todaysdate, 'user': request.user,'mm':mm})
        #print form.errors
    return render(request, template_name,
                              {'form': form, 'ref_no': ref_no, 'todaysdate': todaysdate, 'user': request.user,'mm':mm})



@login_required(login_url='/volk/login/')
def add_funds_volk_card(request):

    template_name = 'volkmann/vei_wallet_card.html'
    mm = marketing_member(request)

    #print form.errors
    return render(request, template_name, {'mm':mm})


@login_required
def pay_for_shipments(request):
    context = {}
    try:
        mm = marketing_member(request)
        context['mm'] = mm
    except:
        count_items = 0
    shipments = ShippingPackage.objects.filter(user = request.user, deleted=False)
    context['shipments'] = shipments
    return render(request,'volkmann/payforshipments.html',context)


@login_required
def user_transactions(request):

    #if request.user.useraccount.address_activation == False:
    #    return redirect (reverse("shipping:address_activation", args=[request.user.username]))

    # try:
    #     user = User.objects.get(username = username)
    # except User.DoesNotExist:
    #     raise Http404
    #credit_purchases = SokoPay.objects.filter(user = user)
    #card_payments = SokoPay.objects.card_payments(request.user)

    #jejepay_log = SokoPay.objects.jejepay_log(request.user)

    # jejepay_credits = SokoPay.objects.user_add_jejepay(request.user)

    if request.user.useraccount.marketer.storefront_name == "volkmannexpress":
        template_name = "volkmann/transactions.html"
    else:
        template_name = "soko_pay/transactions.html"
    
    # if request.GET.has_key('resp'):
    #     pay_response = str(request.GET.get('resp'))
    #     jejepay_ref = request.GET.get('jejepay_ref')
    #     jejepay = MarketerPayment.objects.get(ref_no = jejepay_ref)
    #     jejepay.status = pay_response
    #     jejepay.save()

    user_transactions = MarketerPayment.objects.filter(user=request.user.useraccount)
    jejepay_credits = user_transactions.filter(Q(purchase_type_2="Add"))
    jejepay_debits  = user_transactions.filter(Q(purchase_type_2="Refund") | Q(purchase_type_2="Remove"))
    useraccount = UserAccount.objects.get(user = request.user)
    country = useraccount.country
    print "country", country
    #bank_deposits = SokoPay.objects.bank_deposits(request.user)

    return render(request, template_name, 
        {'jejepay_credits': jejepay_credits, 'jejepay_debits': jejepay_debits, 'country': country})


def obj_variables(obj):
    if hasattr(obj, "order_balance_N"):
        return getattr(obj, "order_balance_N"), getattr(obj, "order_balance_D"), getattr(obj, "jejepay_credit_applied_N"), getattr(obj, "jejepay_credit_applied_D")
    else:
        return getattr(obj, "credit_balance_N"), getattr(obj, "credit_balance_D"), getattr(obj, "shipping_credit_applied_N"), getattr(obj, "shipping_credit_applied_D")


def set_obj_values(obj, selected_dict):
    for key, val in selected_dict.iteritems():
            setattr(obj, key, val)
    return obj


def user_acc_bal(request, user):
    userAcc = UserAccount.objects.get(user = user) 
    return round(userAcc.credit_amount_N, 2), round(userAcc.credit_amount_D, 2)


@login_required
@csrf_exempt
def pay_for_package(request):
    print 'i got here a'
    mm = marketing_member(request)
    user = request.user
    user_credit_amount_N, user_credit_amount_D = user_acc_bal(request, user)
    useraccount = UserAccount.objects.get(user = user)

    if user_credit_amount_N <= 0:
        messages.warning(request, "Insufficient wallet balance. Please fund your VEI Wallet.")
        return redirect (request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        print 'rp',request.POST

        shipping_pkg = ShippingPackage.objects.get(pk=request.POST.get('ship_package'))
        all_cost = CostCalcSettings.objects.get(marketer=mm,country=useraccount.country)

        if not useraccount.country == "United States" or "USA":
            dollarExchangeRate = all_cost.dollar_exchange_rate
            amount_D = shipping_pkg.balance_N / dollarExchangeRate
            amount_N = shipping_pkg.balance_N
            print 'amount_D',amount_D
            
        else:
            print 'got to the else'
            amount_D = shipping_pkg.balance_N

        # credit_bal_N, credit_bal_D, credit_applied_N, credit_applied_D = obj_variables(obj)

        # prev_balance_N = credit_bal_N

        if useraccount.credit_amount_D >= amount_D:

            useraccount.credit_amount_N = float(useraccount.credit_amount_N) - float(shipping_pkg.balance_N)
            useraccount.credit_amount_D = float(useraccount.credit_amount_D) - float(amount_D)

            shipping_pkg.balance_paid_D = shipping_pkg.user_total_payable_D
            shipping_pkg.balance_paid_N = shipping_pkg.user_total_payable_N

            #generated on booking confirmation
            shipping_pkg.user_total_payable_D = shipping_pkg.user_total_payable_D
            shipping_pkg.user_total_payable_N = shipping_pkg.user_total_payable_N

            #generated during processing
            shipping_pkg.admin_total_payable_D = shipping_pkg.admin_total_payable_D
            shipping_pkg.admin_total_payable_N = shipping_pkg.admin_total_payable_N

            shipping_pkg.balance_D = 0.0
            shipping_pkg.balance_N = 0.0

            useraccount.save()

            shipping_pkg.save()

            payment = MarketerPayment.objects.create(
                user=request.user.useraccount,
                payment_channel="VT",
                purchase_type_2="Remove",
                created_at=timezone.now(),
                message="Payment for Package with tracking_number " + str(shipping_pkg.tracking_number),
                status="Approved",
                purchase_type_3="veiwallet",
                amount=amount_D,
                ref_no=purchase_ref(),
                marketer=mm,
                bank=None,
                teller_no=purchase_ref())

            messages.info(request, "You have successfully applied $%s to booking %s" %(str(amount_D), shipping_pkg.tracking_number))
            # return redirect (reverse('general:my_shipments'))
            return redirect (request.META.get("HTTP_REFERER", "/"))
        else:
            messages.info(request, "insufficient VEI Wallet balance.")
            return redirect (request.META.get("HTTP_REFERER", "/"))

    else:
         #shipment = get_object_or_404(Shipment, pk = id)
         return render(request, 'volkmann/payforshipments.html', {'obj': shipping_pkg})

   

@login_required
def pay_with_zappay_credit(request, shop_or_ship, id):
    user = request.user

    order = ""
    shipment = ""
    obj = ""
    if shop_or_ship == "order":
        order = get_object_or_404(Order, user = user, id = id)
        obj = order
        obj.apply_jejepay_credit = True

    elif shop_or_ship == "shipment":
        shipment = get_object_or_404(Shipment, user = user, id = id)
        obj = shipment
        obj.apply_shipping_credit = True

    user_credit_amount_N, user_credit_amount_D = account_standing(request, user)

    if user_credit_amount_N <= 0:
        messages.info(request, "Please fund your SokoPay Wallet.")
        return redirect (request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":

        #dollarNairaRate = costcalc_settings().dollar_naira_rate

        #obj exchange rate
        dollarNairaRate = country_exchange_rate(obj.country, costcalc_settings())
        try:
            amount_N = abs(float(remove_from_string(request.POST['amount'], ",")))
        except ValueError:
            messages.info(request, "Please provide the amount you want to pay in integers.")
            return redirect (request.META.get("HTTP_REFERER", "/"))

        amount_D = amount_N / dollarNairaRate

        credit_bal_N, credit_bal_D, credit_applied_N, credit_applied_D = obj_variables(obj)



        #credit_bal_N = shipment.credit_balance_N
        #credit_bal_D = shipment.credit_balance_D

        prev_balance_N = credit_bal_N


        if user_credit_amount_N >= amount_N:


            # if amount_N - credit_bal_N > 5:
            #     messages.info(request, "Please provide a value that is less or equal to the balance you want to offset.")
            #     return redirect (request.META.get("HTTP_REFERER", "/"))

            #int because of the decimal places
            if int(amount_N) <= int(credit_bal_N):
                if amount_N >= credit_bal_N:

                    jejepay_credit_applied_N = credit_applied_N + credit_bal_N
                    jejepay_credit_applied_D = credit_applied_D + credit_bal_D

                    credit_balance_N = 0
                    credit_balance_D = 0

                    # if hasattr(obj, "order_balance_N"):
                    #     selected_dict = {"order_balance_N": 0, "order_balance_D": 0, "jejepay_credit_applied_N": jejepay_credit_applied_N, "jejepay_credit_applied_D": jejepay_credit_applied_D, 'apply_jejepay_credit': True}
                    # else:
                    #     selected_dict = {"credit_balance_N": 0, "credit_balance_D": 0, "shipping_credit_applied_N": jejepay_credit_applied_N, "shipping_credit_applied_D": jejepay_credit_applied_D, 'apply_shipping_credit': True}
                else:
                    jejepay_credit_applied_N = credit_applied_N + amount_N
                    jejepay_credit_applied_D = credit_applied_D + amount_D

                    new_credit_balance_N = credit_bal_N - amount_N

                    if new_credit_balance_N <0.50:
                        credit_balance_N = 0
                        credit_balance_D = 0
                    else:
                        credit_balance_N = new_credit_balance_N
                        credit_balance_D = new_credit_balance_N/dollarNairaRate
            # if amount_N <= credit_bal_N:
            #
            #     jejepay_credit_applied_N = credit_applied_N + credit_bal_N
            #     jejepay_credit_applied_D = credit_applied_D + credit_bal_D
            #
            #     if hasattr(obj, "order_balance_N"):
            #         selected_dict = {"order_balance_N": 0, "order_balance_D": 0, "jejepay_credit_applied_N": jejepay_credit_applied_N, "jejepay_credit_applied_D": jejepay_credit_applied_D, 'apply_jejepay_credit': True}
            #     else:
            #         selected_dict = {"credit_balance_N": 0, "credit_balance_D": 0, "shipping_credit_applied_N": jejepay_credit_applied_N, "shipping_credit_applied_D": jejepay_credit_applied_D, 'apply_shipping_credit': True}
            #
            #     set_obj_values(obj, selected_dict)
            else:
                messages.info(request, "Please provide a value that is less or equal to the balance you want to offset.")
                return redirect (request.META.get("HTTP_REFERER", "/"))

            # else:
            #
            #     jejepay_credit_applied_N = credit_applied_N + amount_N
            #     jejepay_credit_applied_D = credit_applied_D + amount_D
            #
            #     new_credit_balance_N = credit_bal_N - amount_N
            #
            #     if new_credit_balance_N <0.50:
            #         credit_balance_N = 0
            #         credit_balance_D = 0
            #     else:
            #         credit_balance_N = new_credit_balance_N
            #         credit_balance_D = new_credit_balance_N/dollarNairaRate
            #
            #
            #     if hasattr(obj, "order_balance_N"):
            #         selected_dict = {"order_balance_N": credit_balance_N, "order_balance_D": credit_balance_D, "jejepay_credit_applied_N": jejepay_credit_applied_N, "jejepay_credit_applied_D": jejepay_credit_applied_D}
            #     else:
            #         selected_dict = {"credit_balance_N": credit_balance_N, "credit_balance_D": credit_balance_D, "shipping_credit_applied_N": jejepay_credit_applied_N, "shipping_credit_applied_D": jejepay_credit_applied_D}
            #
            #     set_obj_values(obj, selected_dict)

            if hasattr(obj, "order_balance_N"):
                new_balance_N = obj.order_balance_N
                selected_dict = {"order_balance_N": credit_balance_N, "order_balance_D": credit_balance_D, "jejepay_credit_applied_N": jejepay_credit_applied_N, "jejepay_credit_applied_D": jejepay_credit_applied_D, 'apply_jejepay_credit': True}
            else:
                selected_dict = {"credit_balance_N": credit_balance_N, "credit_balance_D": credit_balance_D, "shipping_credit_applied_N": jejepay_credit_applied_N, "shipping_credit_applied_D": jejepay_credit_applied_D, 'apply_jejepay_credit': True}
                new_balance_N = obj.credit_balance_N

            set_obj_values(obj, selected_dict)

            #shipment.apply_shipping_credit = True
            #shipment.save()

            obj.save()
            #Use shipping credit and create a record
            #prefix_msg = "Balance %s applying jejepay credit: =N= %s"
            use_shipping_credit(request, amount_N, creditpurchase_ref(request), prev_balance_N, abs(new_balance_N), obj)

            if hasattr(obj, "order_balance_N"):
                messages.info(request, "You have successfully applied =N=%s to order %s" %(str(amount_N), obj.tracking_number))
                return redirect (reverse('general:my_orders'))
                #return redirect (reverse('userAccount:open_orders', args=[request.user.username]))
            else:
                messages.info(request, "You have successfully applied =N=%s to booking %s" %(str(amount_N), obj.tracking_number))
                return redirect (reverse('general:my_shipments'))
                #return redirect (reverse('shipping:track_shipment'))
            #return redirect('/shipping/track-shipment/')
        else:
             messages.info(request, "The amount you have specified is greater than Max Amount Payable(=N=).")
             return redirect (request.META.get("HTTP_REFERER", "/"))

    else:
         #shipment = get_object_or_404(Shipment, pk = id)
         return render(request, 'soko_pay/pay-with-zappay-credit.html', {'obj': obj, 'user_credit_amount_N': user_credit_amount_N})



@login_required
def pay_by_bank_deposit(request, **kwargs):
    mm          = marketing_member(request)
    ref_no      = creditpurchase_ref(kwargs["id"])
    todaysdate  = datetime.now()
    form        = MarketerPaymentForm()
    #shop_or_ship = request.session["ship_or_ship"]

    # if shop_or_ship == "shopping":
    #     balance_N = get_object_or_404(Order, id = kwargs['id']).order_balance_N
    #     header_msg = "Pay for Order through bank deposit"
    # elif shop_or_ship == "shipping":
    try:
        balance_D = get_object_or_404(DomesticPackage, tracking_number = kwargs['id']).amount
    except Exception as e:
        print "e", e
        balance_D = get_object_or_404(ShippingPackage, tracking_number = kwargs['id']).balance_D
    header_msg = "Pay for Package through bank deposit"

    template_name = "soko_pay/add_funds.html"
    action_type = "pay_by_bank_deposit"
    try:
        pkg = DomesticPackage.objects.get(tracking_number = kwargs['id'])
        response_dict = {'ref_no': ref_no,'todaysdate': todaysdate, 'user': request.user, 'local_pkg': pkg, 'mm':mm, 'balance_D': balance_D, 'action_type': action_type, 'header_msg': header_msg}
        package = None
        local_pkg = pkg
    except Exception as e:
        print "e2", e
        pkg = ShippingPackage.objects.get(tracking_number =kwargs['id'])
        response_dict = {'ref_no': ref_no,'todaysdate': todaysdate, 'user': request.user, 'pkg': pkg, 'mm':mm, 'balance_D': balance_D, 'action_type': action_type, 'header_msg': header_msg}
        package = pkg
        local_pkg = None
    #print request.POST
    if request.method == 'POST':
        form    = MarketerPaymentForm(request.POST)
        message = "Being Payment for package balance"
        if form.is_valid():
            
            rp = request.POST.get
            payment_channel = rp('payment_channel')
            amount = rp('amount')
            ref_no =rp('ref_no')
            bank = rp('bank')
            teller_no = rp('teller_no')
            payment = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel=payment_channel,created_at=todaysdate,message=message,
                                                     amount=amount,package=package,ref_no=ref_no,marketer=mm,bank=bank,teller_no=teller_no,local_package=local_pkg)
            payment.save()
            
            #form.save(commit=False)
            #success = buy_jejepay_credit_deposit_general(form)
            #if (success):
                #username = request.user.username#UserAccount.objects.get(user = request.user).username
                #return redirect (reverse ('userAccount.views.user_jeje_pay_info', args=[username]))
                #return redirect (reverse ('userAccount:user_jeje_pay_info', args=[username]))
            
            # form.created_at = todaysdate
            # form.user = UserAccount.objects.get(user=request.user)
            # print pkg
            # form.package = ShippingPackage.objects.get(tracking_number=pkg)
            # form.marketer = MarketingMember.objects.get(pk=mm.id)
            # print form.marketer
            # form.message = "Being Payment for package balance"
            # form.save()
            messages.info(request, "Your payment has been submitted. Our Finance department will approve it shortly after confirmation. Thank you.")
            return redirect (reverse ('general:my_soko_pay'))

            # else:
            #     error_alert = 'Amount Entered must be more than 0.'
            #     response_dict.update({'error_alert': error_alert, 'form': form })
            #     return render(request, template_name, response_dict)

        else:
            error_alert = 'Please correct the hightlighted field(s)'
            response_dict.update({'error_alert': error_alert, 'form': form })
            return render(request, template_name, response_dict)
        #print form.errors
    response_dict.update({'form': form})
    return render(request, template_name, response_dict)


#site_redirect_url_epay_confirmation = 'http://www.zaposta.com/shopping/epay-confirmation/'

@login_required
@user_passes_test(staff_check_for_booking, login_url='/admin/orders/new/', redirect_field_name=None)
def buy_jejepay_credit_card(request):
    #global site_redirect_url_epay_confirmation
    #kwargs = {'site_redirect_url': site_redirect_url_epay_confirmation}
    if request.method == "POST":
        print request.POST, 
        actual_amount               = request.POST.get('amount')
        if actual_amount != '' and actual_amount > 0:
            amount =  float(request.POST.get('amount'))
            dest_namespace          = 'soko_pay:user_transactions'
            kwargs_dict             = {'actual_amount_N': amount, 'dest_namespace_1': None,
                                       'dest_namespace_2': dest_namespace, 'txn_desc': 'Buy Credit',
                                       }
            return payment_helpers.card_payment(request, **kwargs_dict)
        else:
            messages.error(request, 'Please complete the amount field')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        # if request.POST.has_key('otp'):
        #     pay_response = call_verify_payment(request)
        #     response_msg = pay_response['responsemessage']
        #     pay_response_msg = response_msg.lower()
        #     if not 'success' in pay_response_msg:
        #         return JsonResponse({'response_msg': pay_response_msg})
        #
        # else:
        #     actual_amount           = float(request.POST.get('amount', 0))
        #     kobo_value              = 100
        #     markedup_amount         = actual_amount * kobo_value
        #     txn_ref                 = request.POST['txn_ref']
        #
        #     #dest_namespace          = 'soko_pay:user_transactions'
        #     #return initiate_payment(request, actual_amount, markedup_amount, txn_ref, dest_namespace)
        #
        #     kwargs = {'amount_paid_N': actual_amount, 'txn_desc': 'Buy Credit'}
        #     pay_response = call_initiate_payment(request, **kwargs)
        #     print 'pay_response: ',pay_response
        #     response_msg = pay_response['responseMessage']
        #     pay_response_msg = response_msg.lower()
        #     if not 'success' in pay_response_msg:
        #         if 'pending' in pay_response_msg:
        #             pay_response.update({'response_msg': "Transaction %s." %response_msg})
        #             return JsonResponse(pay_response)
        #         else:
        #             messages.error(request, "Oops. %s. Please try again." %response_msg)
        #             return JsonResponse({'redirect_url': request.build_absolute_uri(reverse('shipping:shipping_payment'))})

        # actual_amount           = float(request.POST.get('actual_amount', 0))
        # kobo_value              = 100
        # markedup_amount         = actual_amount * kobo_value
        # txn_ref                 = request.POST['txn_ref']
        # bank                    = 'PayStack'
        #
        # print 'actual_amount: ',actual_amount
        # if actual_amount > 0:
        #
        #     kwargs = {'actual_amount': str(actual_amount), 'txn_ref': txn_ref, #'tracking_number': tracking_number,
        #               'markedup_amount': str(markedup_amount), 'bank': bank}
        #     response = create_credit_instance(request, **kwargs)
        #
        #     print 'buy_jeje response: ',response
        #
        #     callback_url = request.build_absolute_uri(reverse('soko_pay:paystack_verify_transaction', args=[txn_ref]))
        #     if response['status'] == 'success':
        #         kwargs = {'markedup_amount': str(markedup_amount), 'callback_url': callback_url,
        #               'bank': bank, 'email': request.user.email}
        #         return initialize_transaction(request, **kwargs)

    #todaysdate  = datetime.now()
    txn_ref = creditpurchase_ref()
    return render(request, 'soko_pay/pay-with-card.html', {'txn_ref': txn_ref, 'pay_method': 'Card','sokopay':'sokopay',
                                                            'months_list': flutterwave_helpers.months_list(),
                                                            'years_list': flutterwave_helpers.years_list()})
                                  #{'txn_ref': txn_ref,'todaysdate': todaysdate,
                                  # 'pay_method': 'Card'})

    #kwargs = {'site_redirect_url': settings.INTERSWITCH_REDIRECT_URL_EPAY_CONFIRMATION}
    #return purchase_credit(request, order=None, **kwargs)

# @login_required
# @user_passes_test(staff_check_for_booking, login_url='/admin/orders/new/', redirect_field_name=None)
# def select_payment_option(request, shop_or_ship, id):
#     #username = request.user
#     user = request.user
#     order = ""
#     shipment = ""
#     if shop_or_ship == "order":
#         order = get_object_or_404(Order, user = user, id = id)
#         request.session["ship_or_ship"] = "shopping"
#     elif shop_or_ship == "export":
#         request.session["ship_or_ship"] = "export"
#         shipment = get_object_or_404(Export, user = user, id = id)
#
#     user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
#     return render(request, "soko_pay/select-payment-option.html", {'user_credit_amount_N': user_credit_amount_N,
#                                                                              'order': order, 'shipment': shipment})

@login_required
@user_passes_test(staff_check_for_booking, login_url='/admin/orders/new/', redirect_field_name=None)
def select_payment_option(request):
    try:
        local_pkg = request.session['local_pkg']
        tracking_number = local_pkg.tracking_number
    except:
        tracking_number = request.GET.get('tracking_number')
    mm = marketing_member(request)
    print "mm:", mm
    #print 'tracking_number: ',tracking_number
    return render(request, "soko_pay/select_payment_option.html", {'tracking_number': tracking_number, 'mm': mm})


# def get_pkg(user, tracking_number):
#     if firstStringCharisI(tracking_number):
#         obj = get_object_or_404(ShippingPackage, user=user, tracking_number=tracking_number)
#     else:
#         obj = get_object_or_404(ExportPackage, user=user, tracking_number=tracking_number)
#     return obj


def get_pkg(user,tracking_number):
    obj = get_object_or_404(ShippingPackage, user=user, tracking_number=tracking_number)
    return obj


@login_required
@user_passes_test(staff_check_for_booking, login_url='/admin/orders/new/', redirect_field_name=None)
def pay_balance(request):
    #username = request.user
    user = request.user
    mm = marketing_member(request)
    context_dict = {}

    '''check if POST is not coming from PayStack or PayPal'''
    #if not request.GET.has_key('trxref') or request.GET.has_key("tx"):
        #keep user selected options in memory
        #print 'keeping request.GET for paystack/paypal'
        
    if request.method == "GET" and not request.GET.has_key('resp'):
        request.session['requestGET'] = request.GET


    requestGET = request.session['requestGET']
    tracking_number = requestGET.get('tracking_number')
    pay_method = requestGET.get('pay_method')

    print 'pay_method - tracking_number ',pay_method, tracking_number

    pkg = get_pkg(user, tracking_number)
    
    if request.GET.has_key('resp'):
        print "I got back from flutterwave"
        pay_response = str(request.GET.get('resp'))
        #pay_response =  ast.literal_eval(request.GET.get('resp'))
        jejepay_ref = request.GET.get('jejepay_ref')
        #jejepay_ref = pay_response['merchtransactionreference']
        pay_response_msg = pay_response
        #pay_response_msg = pay_response['responsemessage']
        request.session['status'] = pay_response_msg
        print pay_response_msg
        if pay_response_msg != "success":
        #if pay_response_msg != "Approved": #or pay_response_msg != "Success":
                #messages.error(request, pay_response_msg)
            print "Am going home"
            tranx_id = jejepay_ref
            #tranx_id = pay_response['merchtransactionreference']
            request.session['tranx_id'] = tranx_id
            # for pkg in packages:
            #     print "PKG:",pkg.tracking_number
            payment = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel='Card Payment',created_at=datetime.now(),ref_no=jejepay_ref,
                    amount=pkg.user_total_payable_D,package=pkg,marketer=mm,status=pay_response_msg,payment_gateway_tranx_id =tranx_id)
            payment.save()
            messages.error(request, "Your Payment is "+ pay_response_msg)
        else:
            print "flutter"
            packages = ShippingPackage.objects.filter(tracking_number=tracking_number)
            update_payment_record_for_packages(request, packages, jejepay_ref)
            messages.success(request, "Your Payment is Successful")
        return redirect (reverse('general:my_shipments'))

    if request.method == "POST" or (request.GET.has_key("tx") and request.GET.has_key("st")):
        print 'i am coming from paypal'

        if pay_method == "Card":
            amount_paid_D = pkg.balance_D
            amount_paid_N = pkg.balance_N
            msg_info = "You have successfully paid $%s for package %s" %(str(amount_paid_D), tracking_number)

            dest_namespace_2 = 'soko_pay:pay_balance'
            #dest_namespace_2 = 'soko_pay:pay_balance'
            #return call_initiate_payment(request, amount_paid_N, dest_namespace)
            lb_country = "Nigeria"
            dest_namespace = 'soko_pay:pay_balance'
            kwargs_dict = {'actual_amount_D': amount_paid_D, 'dest_namespace_1': None, 'lb_country':lb_country,
                                       'dest_namespace_2': dest_namespace_2, 'txn_desc': 'Pay for package balance'}
            return payment_helpers.card_payment(request, **kwargs_dict)

            #response_dict = payment_helpers.card_payment(request, **kwargs_dict)
            # print "Respo:", response_dict.content
            # print type(response_dict)
            # #pay_response = response_dict.content
            # try:
            #     pay_response = ast.literal_eval(response_dict.content)
            #     #print 'pay_response: ',pay_response
            #     pay_response_msg = pay_response['response_msg']
            #     if 'success' in pay_response_msg.lower():
            #         payment_helpers.apply_shipping_credit(reuest, pkg)
            #     return response_dict
            # except Exception as e:
            #     print "inner e:", e
            #     return response_dict


        if pay_method == "SokoPay":
            print "see me for sokopay"
            amount_to_pay_D = pkg.balance_D
            # amount_to_pay_N = abs(float(remove_from_string(request.POST.get('amount'), ',')))
            #
            # if amount_to_pay_N > pkg.balance_N:
            #     messages.error(request, "The specified amount is greater than package balance. It should be less.")
            #     return redirect(reverse('general:my_shipments'))

            payment_helpers.apply_shipping_credit(request, pkg, pkg.user, amount_to_pay_D)
            payment_helpers.marketer_payment(request, "SokoPay", "Paid",amount_to_pay_D,pkg,mm,"Approved")
            msg_info = "Payment successfully applied to %s" %pkg.tracking_number
            
            messages.success(request, msg_info)
            return redirect(reverse('general:my_shipments'))


        if pay_method == "PP":
            print "see me for paypal"
            amount_to_pay_D = pkg.balance_D
            # amount_to_pay_N = abs(float(remove_from_string(request.POST.get('amount'), ',')))
            #
            # if amount_to_pay_N > pkg.balance_N:
            #     messages.error(request, "The specified amount is greater than package balance. It should be less.")
            #     return redirect(reverse('general:my_shipments'))

            payment_helpers.pay_with_paypal(request, pkg, pkg.user, amount_to_pay_D)
            
            msg_info = "Payment successfully applied to %s" %pkg.tracking_number

            messages.success(request, msg_info)
            return redirect(reverse('general:my_shipments'))

    else:
        # '''Verify PayStack payment status and apply'''
        # if pay_method == "Card" and request.GET.has_key('trxref') and request.GET.has_key('jejepay_ref'):
        #     pkgs            = [pkg]
        #     update_payment_record_for_packages(request, pkgs)
        #     messages.success(request, msg_info)
        #     return redirect(reverse('general:my_shipments'))
        user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
        obj = get_pkg(user, tracking_number)


        if pay_method == 'PP' and not (request.GET.has_key("tx") and request.GET.has_key("st")):
            print 'i wanna go pay at paypal'
            request.session['tracking_number'] = tracking_number
            request.session['pay_method'] = pay_method
            return_url     = 'http://127.0.0.1:8000/confirm_paypal_payment/'
            receiver_mail  = 'jonesodezi@gmail.com'
            markedup_amount = round(pkg.balance_D * (102.9/100), 2) #amount + 2.9% charge
            kwargs = {'actual_amount': pkg.balance_D, 'markedup_amount': markedup_amount, 'site_redirect_url': return_url, 'receiver_mail': receiver_mail, 'PayPal':'PayPal','pay_balance':'pay_balnace'}
            return initialize_paypal_payment(request, **kwargs)


        elif pay_method == 'Card' and not (request.GET.has_key('resp')):
            template_name = "soko_pay/pay-with-card.html"
            txn_ref = creditpurchase_ref()
            context_dict.update({'txn_ref': txn_ref,
                                'months_list': flutterwave_helpers.months_list(),
                                'years_list': flutterwave_helpers.years_list()})
            
            
        elif pay_method == 'SokoPay':
            #if user_credit_amount_D >= obj.balance_D:

            if user_credit_amount_D >= obj.balance_D:
                template_name = "soko_pay/pay-with-sokopay-credit.html"
                context_dict.update({'user_credit_amount_D': user_credit_amount_D})
            else:
            #     balance_D = obj.balance_D - user_credit_amount_D
                 messages.error(request, "Your SokoPay balance of ${} is insufficient to pay for this package.".format(round(user_credit_amount_D, 2)))
            #     messages.error(request, "You need to top up your wallet with atleast ${} through Buy Credit or use other payment methods.".format(round(balance_D, 2)))
                 return redirect(reverse('general:my_shipments'))

        context_dict.update({'obj': obj, 'pay_method': pay_method})

        return render(request, template_name, context_dict)



#''' Subscriber payments '''

def subscriberPayment(request):
    subscriber = request_subscriber(request)
    amount = request.GET.get('amount')
    owner = request.GET.get('owner')
    print amount, owner
    return render(request, 'soko_pay/sub_payment_options.html', {'amount':amount, 'owner':owner})


def SubCardPayment(request):
    subscriber = request_subscriber(request)
    context_dict = {}
    amount = float(request.GET.get('amount'))
    owner = request.GET.get('owner')
    sokofee = round((0.1 * amount),2)
    total_amount = sokofee + amount
    pay_method = "sub_payment"
    if request.method == 'GET':
        txn_ref = creditpurchase_ref()
        template_name = 'soko_pay/pay-with-card.html'
        context_dict.update({'txn_ref': txn_ref,'subscriber': subscriber,'amount':amount, 'owner':owner,
                                'months_list': flutterwave_helpers.months_list(), 'pay_method':pay_method,
                                'years_list': flutterwave_helpers.years_list(), 'sokofee': sokofee, 'total_amount':total_amount})
    return render(request, template_name, context_dict)