try:
    from flutterwave import Flutterwave
except:
    pass
#from flutterwave import Flutterwave
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from general.flutterwave_helpers import api_key, merchant_key, initialize_flw, flw
from general.user_profile import is_bvn_used
from django.contrib import messages

def verify(request):
    if request.method == "POST":
        bvn                     = request.POST.get('bvn_no')
        if is_bvn_used(request,bvn):
            return JsonResponse({'result': 'Used'})
        else:
            firstname               = request.POST.get('firstname')
            lastname                = request.POST.get('lastname')
            verifyUsing             = 'Voice'
            country                 = 'NGN'
            verify                  = flw.bvn.verify(bvn, verifyUsing, country)
            verify_json             = verify.json()
            #print 'verify_json: ',verify_json
            responseMessage         = verify_json['data']['responseMessage']
            if responseMessage   == 'Successful, pending OTP validation':
                transactionReference    = verify_json['data']['transactionReference']
            
                '''Keep important variables in session, for later use'''
                request.session['api_key']              = api_key
                request.session['merchant_key']         = merchant_key
                request.session['verifyUsing']          = verifyUsing
                request.session['country']              = country
                request.session['transactionReference'] = transactionReference
                request.session['bvn']                  = bvn
                request.session['firstname']            = firstname
                request.session['lastname']             = lastname
                
                return redirect(reverse('general:enter_otp'))
    
    else:
        return redirect(request.META['HTTP_REFERER'])
          


def enter_otp(request):
    if request.session.has_key('bvn') and request.session.has_key('verifyUsing'):
        #print "i got here"
        context = {'bvn': request.session['bvn'], 'verifyUsing': request.session['verifyUsing']}
        return render(request, 'bvn/enter_otp_for_bvn.html', context)
        #return JsonResponse({'result': 'Ok'})
    return redirect(reverse('general:verify_bvn'))

def resend_otp(request):
    '''Resend OTP'''
    
    '''Retrieve saved values from session'''
    api_key, merchant_key, verifyUsing, country, transactionReference, bvn, firstname, lastname  = retrieve_values(request)
        
    #flw                                     = initialize_flw(api_key, merchant_key)
    resend_otp                              = flw.bvn.resendOtp(verifyUsing, transactionReference, country)
    resend_otp_json                         = resend_otp.json()
    #print 'resend_otp_json: ',resend_otp_json
    
    return JsonResponse({'status': resend_otp_json['status']})

def retrieve_values(request):
    '''Retrieve saved values from session'''
    api_key                                 = request.session['api_key']              
    merchant_key                            = request.session['merchant_key']
    verifyUsing                             = request.session['verifyUsing']
    country                                 = request.session['country']
    transactionReference                    = request.session['transactionReference'] 
    bvn                                     = request.session['bvn']
    firstname                               = request.session['firstname']
    lastname                                = request.session['lastname']
    
    return api_key, merchant_key, verifyUsing, country, transactionReference, bvn, firstname, lastname

def clear_values_from_session(request, keys_list):
    for key in keys_list:
        if request.session.has_key(key):
            del request.session[key]
            

def validation_result(request):
    context = {}
    '''Validate BVN'''
    if request.method == "POST":
        otp = request.POST.get('otp')
        
        '''Retrieve saved values from session'''
        api_key, merchant_key, verifyUsing, country, transactionReference, bvn, firstname, lastname  = retrieve_values(request)           
        
        #flw                                     = initialize_flw(api_key, merchant_key)
        validate                                = flw.bvn.validate(bvn, otp, transactionReference, country)
        validate_json                           = validate.json()
        #print "validate_json",validate_json
        
        # print 'validate_json: ',validate_json
        data =  validate_json['data']
        #print data['firstName']
        #print firstname
        if data['firstName'] != None and data['lastName'] != None:
            firstName = data['firstName'].lower()
            lastName = data['lastName'].lower()
            firstname = firstname.lower()
            lastname = lastname.lower()
            if ((firstName == firstname) and (lastName == lastname)):
                #context.update({'data': validate_json['data']})
            
            # '''Clear saved values from session'''
                keys_list = ['api_key', 'merchant_key', 'verifyUsing', 'country', 'transactionReference', 'bvn', 'firstname', 'lastname']
                clear_values_from_session(request, keys_list)
                return JsonResponse({'result': 'Ok'})
            else:
                return JsonResponse({'result': 'error'})
            #return render(request, 'bvn/bvn_verification_result.html', context)
        else:
            return JsonResponse({'result': 'error'})
    return redirect(reverse('general:enter_otp'))