from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
import requests
import json
from sokopay.models import SokoPay

import random

secret_key = 'Bearer sk_live_f01aa6eefc33918ceb59eaf7f6d0789cac72c93c'


def initialize_transaction(request, **kwargs):
    '''Verify'''
    print 'rG: ', request.GET
    print 'rP: ', request.POST

    if request.method == "POST":
        print request.POST
        print 'posting to paystack'

        reference                       = kwargs.get('reference')
        amount                          = kwargs.get('markedup_amount')
        email                           = kwargs.get('email')
        callback_url                    = kwargs.get('callback_url')

        return go_to_paystack(request, secret_key, reference, amount, email, callback_url)


def go_to_paystack(request, secret_key, reference, amount, email, callback_url):
    print 'going to paystack'
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {'Authorization': secret_key, 'Content-Type': 'application/json'}
    data = {'reference': reference, 'amount': amount, 'email': email, 'callback_url': callback_url}
    r = requests.post(url, json = data, headers = headers, verify = True)
    r_json = r.json()
    #print 'r_json.json(go_to_paystack): ',r_json

    if r_json['status']  == True:
        r_json_data = r_json['data']
        authorization_url = r_json_data['authorization_url']
        return redirect(authorization_url)
    else:
        messages.error(request, r_json['message'])
        return redirect(request.META.get('HTTP_REFERER'))



def verify_transaction(request, jejepay_ref, dest_namespace):
    print 'verifying transaction at paystack'
    reference = request.GET.get('trxref')
    #secret_key = request.session['secret_key']
    # print 'jejepay_ref: ',jejepay_ref
    # print 'reference: ',reference
    # print 'secret_key: ',secret_key

    url = 'https://api.paystack.co/transaction/verify/%s' %reference
    headers = {'Authorization': secret_key, 'Content-Type': 'application/json'}
    r = requests.get(url, headers = headers, verify = True)
    r_json = r.json()
    #print 'r_json.json(verify_transaction) :',r_json

    rjson_data = r_json['data']
    if rjson_data['status'] == 'success':
        jejepay                             = SokoPay.objects.get(ref_no = jejepay_ref)
        jejepay.payment_gateway_tranx_id    = rjson_data['authorization']['authorization_code']
        jejepay.status                      = 'Approved'
        jejepay.message                     = r_json['message']
        jejepay.save()

        return redirect(reverse(dest_namespace)+'?trxref=%s&jejepay_ref=%s' %(reference, jejepay_ref))
        # # url = request.build_absolute_uri(reverse(dest_namespace))
        # # data = {'trxref': reference, 'jejepay_ref': jejepay_ref}
        # # requests.post(url, json = data)
        #return redirect(reverse('soko_pay:user_transactions'))

    messages.error(request, r_json['message'])
    return redirect(request.META.get('HTTP_REFERER'))
