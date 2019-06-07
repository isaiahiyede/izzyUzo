try:
    from flutterwave import Flutterwave
except Exception as e:
    print 'e: ',e
    pass
from django.conf import settings
import random
from django.shortcuts import render, redirect
import ast
from django.contrib import messages
from django.core.urlresolvers import reverse
from sokopay.models import SokoPay, MarketerPayment
from general.custom_functions import marketingmember_costcalc
from general.encryption import value_decryption
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def keep_values(request, keys_list, data_dict):
    for key in keys_list:
        request.session[key] = data_dict[key]


def clear_values_from_session(request, keys_list):
    for key in keys_list:
        if request.session.has_key(key):
            del request.session[key]


api_key         = settings.FLUTTERWAVE_API_KEY
merchant_key    = settings.FLUTTERWAVE_MERCHANT_KEY

def initialize_flw(api_key, merchant_key):
    try:
        debug = settings.DEBUG
        options = {"debug": debug}
        if debug:
            flw    = Flutterwave(api_key, merchant_key, options)
        else:
            options.update({'baseUrl': 'https://prod1flutterwave.co:8181'})
            flw    = Flutterwave(api_key, merchant_key, options)

        return flw
    except Exception as e:
        print 'initialize_flw error: ',initialize_flw


flw  = initialize_flw(api_key, merchant_key)
def generate_ref_no():
    ref_no = ''
    digits = '1234567890'
    ref_no_length = 9
    for x in range(ref_no_length):
        ref_no += digits[random.randint(0, len(digits) - 1)]
    return ref_no

def return_data(data_dict):
    dataList = []
    for key, val in data_dict.iteritems():
        dataList.append({'code': key, 'name': val['name']})
    return dataList

def get_countries():
    data_dict = flw.util.countryList()
    return return_data(data_dict)

def get_currencies():
    data_dict = flw.util.currencyList()
    return return_data(data_dict)

def months_list():
    months = []
    for i in range(1, 13):
        months.append(str(i).zfill(2))
    return months

def years_list():
    years = []
    for i in range(6):
        years.append(str(2016+i))
    return years



local_markup_percentage    = round(1.4 / 100.00, 4)
intl_markup_percentage     = round(3 / 100.00, 4)

def get_markup_charge(request, cardNumber):
    cardBin6    = cardNumber[:6] #first 6 digits
    #print 'cardBin6: ',cardBin6
    country     = '' #optional
    verify      = flw.bin.check(cardBin6, country)
    lb_country  = request.session.get('lb_country')
    response_data       = verify.json()['data']
    responseMessage     = str(response_data['responseMessage']).lower()

    markup_percentage = markup_min_charge = 0
    is_nigerian_card = False
    if 'success' in responseMessage:
        is_nigerian_card    = response_data['nigeriancard']
        #print 'is_nigerian_card: ',is_nigerian_card
        if is_nigerian_card:
            markup_percentage    = local_markup_percentage
            markup_min_charge    = 0.2 #(Dollar)50#(Naira)
        else:
            markup_percentage    = intl_markup_percentage
            markup_min_charge    = 1
            # Minimum equivalent of $1
            # if request.session.has_key('lb_country'):
            #     lb_country  = request.session.get('lb_country')
            #     markup_min_charge    = marketingmember_costcalc(request,lb_country).dollar_exchange_rate
            # else:
            #     lb_country = request.user.useraccount.country
            #     if lb_country == "United States":
            #         markup_min_charge = 1
            #     else:
            #         markup_min_charge    = marketingmember_costcalc(request,lb_country).dollar_exchange_rate

    return markup_percentage, markup_min_charge, is_nigerian_card



#def initiate_charge_card(request, amount_N, txn_desc, txn_ref):
#@login_required
def initiate_charge_card(request, **kwargs):
    if request.method == "POST":

        txn_desc            = kwargs['txn_desc']
        txn_ref             = kwargs['txn_ref']
        #lb_country          = kwargs['lb_country']
        payload = request.POST.copy()
        print "payload",payload
        payload.pop('csrfmiddlewaretoken')
        print "kwargs", kwargs
        actual_amount_D                     = round(kwargs.get('actual_amount', 0), 2)
        cardNumber                          = request.POST.get('cardNumber')
        markup_percentage, markup_min_charge, is_nigerian_card = get_markup_charge(request, cardNumber)

        print 'markup_percentage, markup_min_charge: ',markup_percentage, markup_min_charge
        markup_charge_D      = round((float(actual_amount_D) * markup_percentage) + markup_min_charge, 2)
        
        #if markup_percentage == local_markup_percentage:
        if is_nigerian_card:
            max_markup_charge_D = 5
            if markup_charge_D > max_markup_charge_D:
                markup_charge_D = max_markup_charge_D

            #payload.update({'bvn': '12345678901'})
            #bvn = value_decryption(request.user.useraccount.bvn_no)
            #payload.update({'bvn': bvn})
            '''Adding default values'''
            payload.update({'country': 'NG'})
            payload.update({'currency': 'NGN'})
            payload.update({'authModel': 'VBVSECURECODE'})
            #payload.update({'responseUrl':  request.build_absolute_uri(reverse('soko_pay:user_transactions'))})
            # if 'lb_country' in kwargs:
            #     amount_D             = round(actual_amount_D + markup_charge_D, 2)
            #     cost_calc            = marketingmember_costcalc(request, lb_country)
            #     amount_N             = round(amount_D * float(cost_calc.dollar_exchange_rate), 2)
            # else:
            amount_D             = round(actual_amount_D + markup_charge_D, 2)
            cost_calc            = marketingmember_costcalc(request, 'Nigeria')
            amount_N             = format(amount_D * float(cost_calc.dollar_exchange_rate), '.2f')
                
            payload.update({'responseUrl':  request.build_absolute_uri(reverse('soko_pay:complete_intl_card'))+'?jejepay_ref='+txn_ref+'&actual_amount_D='+str(actual_amount_D)+'&amount_N='+str(amount_N)})
            #amount_N             = round(actual_amount_N + markup_charge_N, 2)
            payload.update({'amount': str(amount_N)})
            request.session['NGN_card'] = True

        else:
            
            if kwargs.has_key('lb_country'):
                cost_calc = marketingmember_costcalc(request, lb_country)
            '''Adding default values'''
            payload.update({'country': 'NG'})
            payload.update({'currency': 'USD'})
            payload.update({'authModel': 'VBVSECURECODE'})
            #payload.update({'responseUrl':  request.build_absolute_uri(reverse('soko_pay:user_transactions'))})
            if kwargs.has_key('lb_country'):
                amount_D             = format(actual_amount_D + markup_charge_D, '.2f')
                amount_N             = round(amount_D * float(cost_calc.dollar_exchange_rate), 2)
            else:
                amount_D = round(actual_amount_D + markup_charge_D, 2)
                cost_calc = marketingmember_costcalc(request, request.user.useraccount.country)
                amount_N = format(amount_D * float(cost_calc.dollar_exchange_rate), '.2f')
            payload.update({'amount': format(amount_D, '.2f')})
            payload.update({'responseUrl':  request.build_absolute_uri(reverse('soko_pay:complete_intl_card'))+'?jejepay_ref='+txn_ref+'&actual_amount_D='+str(actual_amount_D)+'&amount_N='+str(amount_N)})
            request.session['intl_card'] = True

        payload.update({'narration': txn_desc})

        #print 'payload: ',payload

        #payload.update({'responseUrl':  ''})

        #payload.update({'responseUrl':  request.build_absolute_uri(reverse('soko_pay:initiate_charge_card'))})

        print 'going to flutterwave to charge card'
        verify                  = flw.card.charge(payload)
        #print "verify:", verify
        # print "{}".format(verify.text)
        verify_json             = verify.json()
        response_data           = verify_json['data']
        #print "verify_json:", verify_json
        #print 'response_data: ',response_data

        response_dict = {'responsecode': response_data['responsecode'], 'responseMessage': response_data['responsemessage'], 'jejepay_ref': txn_ref,
                        'otptransactionidentifier': response_data['otptransactionidentifier'],
                        'transactionreference': response_data['transactionreference'], 'total_N': amount_N,
                        'actual_amount_D': actual_amount_D, 'markup_charge_D': markup_charge_D}

        '''Intl cards'''
        if response_data.has_key('responsehtml') and payload['authModel'] == 'VBVSECURECODE':
            if response_data['responsehtml'] != None:
                responsehtml = response_data['responsehtml']
                decoded_responsehtml = flw.util.decryptData(responsehtml)
                request.session['decoded_responsehtml'] = decoded_responsehtml
                #return render(request, )
                response_dict.update({'decoded_responsehtml': True,
                'intl_card_verification_url': request.build_absolute_uri(reverse('soko_pay:intl_card_verification')),
                })
            #return response_dict
            #return HttpResponse(decoded_responsehtml)


        #if response_data.has_key('responsemessage'):
        #print 'response_dict: ',response_dict
        return response_dict


def update_jejepay_obj(jejepay_ref, tranx_id, status):
    try:
        jejepay = SokoPay.objects.get(ref_no = jejepay_ref)
    except:
        jejepay = MarketerPayment.objects.get(ref_no = jejepay_ref)
    jejepay.status = status
    if tranx_id != None:
        jejepay.payment_gateway_tranx_id = tranx_id
    jejepay.save()
    return jejepay


#@login_required
def verify_otp(request):
    rp = request.POST
    jejepay_ref = rp['jejepay_ref']
    payload = {'country': 'NG', 'otpTransactionIdentifier': rp['otpTransactionIdentifier'],
               'otp': rp['otp']}

    #print 'going to flutterwave to verify otp'
    response = flw.card.validate(payload).json()
    #print 'response: ',response
    response_data = response['data']
    response_data.update({'jejepay_ref': jejepay_ref})

    response_msg = response_data['responsemessage'].lower()
    #if 'success' in response_msg or 'approved' in response_msg:
    '''Update jejepay record status'''
        # jejepay = SokoPay.objects.get(ref_no = jejepay_ref)
        # jejepay.status = 'Approved'
        # jejepay.payment_gateway_tranx_id = response_data['transactionreference']
        # jejepay.save()

    tranx_id = response_data['transactionreference']
    update_jejepay_obj(jejepay_ref, tranx_id, response_msg)

    return response_data


@login_required
def intl_card_verification(request):
    decoded_html = request.session['decoded_responsehtml']
    return HttpResponse(decoded_html)

#resp={"batchno":"20161015","merchtransactionreference":"SOKO/PT-FLW00982294","orderinfo":"OPT-FLW00982294","receiptno":"628902385186","transactionno":"475","responsetoken":"PdiWi85Ljt05TNg0943","responsecode":"0","responsemessage":"Approved","responsehtml":""}

@login_required
def complete_intl_card(request):
    rG              = request.GET
    #amt = rG.get('amount_D')
    #print "rG:"
    respo = rG.get('resp')
    #print type(resp)
    resp =  ast.literal_eval(respo)
    print resp['responsemessage']
    # resp_val_split  = rG.get('amount_D').split('?')[1]
    # resp            = ast.literal_eval(resp_val_split.split('=')[1])

    tranx_id        = resp["merchtransactionreference"]
    jejepay_ref     = rG.get('jejepay_ref')
    amount_D        = rG.get('actual_amount_D')
    amount_N        = rG.get('amount_N')

    try:
        jejepay         = update_jejepay_obj(jejepay_ref, tranx_id, resp['responsemessage'])
        jejepay.amount  = amount_D
        jejepay.save()
    except:
        request.session['tranx_id']= tranx_id
        pass
    if request.session.has_key('intl_card') or request.session.has_key('NGN_card'):
        if request.session.has_key('intl_card'):
            del request.session['intl_card']
        else:
            del request.session['NGN_card']
        go_to_url = request.session['dest_namespace_1']
        if go_to_url == None:
            go_to_url = request.session['dest_namespace_2']
            del request.session['dest_namespace_2']
        print "go url:", go_to_url
        del request.session['dest_namespace_1']

        messages.info(request, resp['responsemessage'])
        if go_to_url == 'soko_pay:buy_jejepay_credit_card':
            return redirect(request.build_absolute_uri(reverse(go_to_url)))
        #print "url:", request.build_absolute_uri(reverse(go_to_url)+'?jejepay_ref='+jejepay_ref+'&actual_amount_D='+str(amount_D)+'&amount_N='+str(amount_N)+'&resp='+respo)
        return redirect(request.build_absolute_uri(reverse(go_to_url)+'?jejepay_ref='+jejepay_ref+'&actual_amount_D='+str(amount_D)+'&amount_N='+str(amount_N)+'&resp='+respo))
        #return redirect(reverse('soko_pay:user_transactions'))

    msg_info = "You have successfully paid $%s" %(str(amount_D))
    messages.info(request, msg_info)
    return redirect(reverse('soko_pay:user_transactions'))


'''For authModel=PIN'''
# def initiate_charge_card(request, **kwargs):
#     if request.method == "POST":
#         amount_N   = kwargs['actual_amount']
#         txn_desc   = kwargs['txn_desc']
#         txn_ref    = kwargs['txn_ref']
#
#         payload = request.POST.copy()
#         payload.pop('csrfmiddlewaretoken')
#         payload.update({'amount': str(amount_N)})
#
#         '''Adding default values'''
#         payload.update({'country': 'NG'})
#         payload.update({'currency': 'NGN'})
#         payload.update({'authModel': 'PIN'})
#         payload.update({'narration': txn_desc})
#
#         print 'going to flutterwave charge card'
#         verify                  = flw.card.charge(payload)
#
#         verify_json             = verify.json()
#         response_data           = verify_json['data']
#
#         if response_data.has_key('responsemessage'):
#             responseMessage         = response_data['responsemessage']
#
#             if 'success' in responseMessage.lower():
#                 '''Update jejepay record status'''
#                 jejepay = SokoPay.objects.get(ref_no = txn_ref)
#                 jejepay.status = 'Approved'
#                 jejepay.save()
#
#             return {'responseMessage': responseMessage, 'jejepay_ref': txn_ref}
