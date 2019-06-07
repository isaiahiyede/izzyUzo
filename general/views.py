from django.db import IntegrityError
from django.template.loader import get_template
from django.db.models import Q, Sum
from django.template.loader import render_to_string, get_template
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail, EmailMessage
from general.models import *
from forms import LoginForm, UserAccountForm, ComposeMessageForm, JoinWaitingListForm, UserForm
# from general.custom_functions import generate_suite_no, marketing_member, get_random_code
from general.custom_functions import *
from general.staff_access import *
from general import payment_helpers
from general.custom_passes_test import request_passes_test
from general.payment_helpers import generate_creditpurchase_ref, card_payment
from shipping.models import ShippingPackage, DomesticPackage, ShippingItem
from shipping.forms import AddCustomPackageForm
from shipping.views import get_office_pickup_locations
from service_provider.models import *
from service_provider.views import subscriber_marketer, request_subscriber
from shipping.pkg_charges import calculate_pickup_charge, calculate_last_mile_charges
from shoppingCenter.models import AddInventory, Cart, UserOrder

from django.utils import timezone
from sokopay.models import SokoPay, MarketerPayment
from sokohaliAdmin.models import FedExLocation, BatchPromo, CostCalcSettings
# from subscriber.models import SubscriberProfile
# from service_provider.models import MarketingMember

from itertools import chain
from cities_light import models as world_geo_data
from general.custom_functions import paginate_list, marketingmember_costcalc, get_local_freight_from_state,  generate_creditpurchase_ref, set_cookie
from general.image_helpers import convert_base64_to_image
import requests, json, urllib
import operator, math
from xml.etree import ElementTree as ET
from general.modelfield_choices import STATE
from service_provider.models import LocalDistributorLocation, Pricing
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from general.forms import CheckoutForm, InventoryForm
import random, datetime
from shipping.CreateShipmentCostCalculator import *
from shipping.PackageCostCalculator import *
from shipping.views import generate_local_tracking_no


''' Add useful tips for the benefit of all guys and number the tip
    The tip should be descriptive albeit breif with an example
'''

''' 1 .This can be used in django templates to loop through dictionaries
    for intance your context has a dictionary called - data to loop through the dictionary
    do this;

    {% for key, value in data.items %}
        {{ key }}: {{ value }}
    {% endfor %}
'''


def subdomain_check(request, redirect_to):
    try:
        if request.subdomain_name and not request.user.is_authenticated():
            return redirect(reverse('general:login'))
    except:
        #pass
        return redirect_to #render(request, 'index.html



def get_route_chains(request):
    route_chains = marketing_member(request).get_shipping_chains()
    # try:
    #     route_chains = marketing_member(request).get_shipping_chains()
    # except Exception as e:
    #     print 'get_route_chains: e | ',get_route_chains
    #     route_chains =  marketing_member(request).get_shipping_chains(service_type, direction)
    # origin_route_countries        =    set([chain.origin for chain in route_chains])
    # destination_route_countries   =    set([chain.destination for chain in route_chains])
    # return  origin_route_countries, destination_route_countries

    #print 'get_route_chains(route_chains): ',route_chains
    origin_route_countries = []
    destination_route_countries = []
    for route in route_chains:
        origin_route_countries.append(route.origin)
        destination_route_countries.append(route.destination)

    #print 'origin_route_countries = destination_route_countries: ',origin_route_countries, destination_route_countries
    return  set(origin_route_countries), set(destination_route_countries)
 
def get_route_countries(request):
    mrk = marketing_member(request)
    print mrk
    route_chains = marketing_member(request).get_shipping_chains()
    print "the chains: ",route_chains
    countries_list = []
    countries_origin = []
    countries_destination = []
    for route in route_chains:
        countries = {'origin': route.origin, 'destination': route.destination}
        countries_list.append(countries)
        countries_origin.append(route.origin)
        countries_destination.append(route.destination)
    print 'country_origin: ', countries_origin
    print 'country_destination: ', countries_destination
    return countries_list, set(countries_origin), set(countries_destination)


def check_avaliable_routes(request):
    countries_list,countries_origin,countries_destination = get_route_countries(request)
    marketers_routes = countries_list
    # print 'MR:',marketers_routes
    curr_selected_route = {'origin':request.GET.get('origin'), 'destination':request.GET.get('destination')}
    # print "CSR: ",curr_selected_route
    
    if curr_selected_route in marketers_routes:
        return JsonResponse({'result':'ok'})
    else:
        return JsonResponse({'result':'fail'})

    
def get_warehouse_address(request):
    mm = marketing_member(request)
    print "mm: ",mm
    WHM = mm.get_all_import_warehouses()
    WHaddress = []
    # if mm.storefront_name == "amezam" or mm.storefront_name == "albeemax" or mm.storefront_name == "skynetworldwideexpress":
    #     template_name = "zaposta_snippet/newWhAddress.html"
    # else:
    #     template_name = "zaposta_snippet/WHaddress.html"
    template_name = "zaposta_snippet/WHaddress.html"
    print "WHM:", WHM
    for location in WHM:
        warehouses = location.get_all_warehouses().filter(country=request.GET.get('origin'))
        for address in warehouses:
            if address in WHaddress:
                pass
            else:
                WHaddress.append(address)  
    # print "WHaddress:", WHaddress
    return render (request, template_name, {'WHaddress':WHaddress})


def get_dest_warehouse_add(request,value):
    mm = marketing_member(request)
    print "mm: ",mm
    WHM = mm.get_all_import_warehouses()
    WHaddress = []
    for location in WHM:
        warehouses = location.get_all_warehouses().filter(country=value)
        for address in warehouses:
            if address in WHaddress:
                pass
            else:
                WHaddress.append(address)  
    # print "WHaddress:", WHaddress
    return WHaddress

def iaai(request):
    template_name = 'vei2018html/iaai.html'
    context = {}
    return render(request,template_name,context)

def get_destination_addresses(request):
    mm = marketing_member(request)
    origin = str(request.GET.get('route').split(' - ')[0])
    destination = str(request.GET.get('route').split(' - ')[1])
    print "the destination:",destination
    print "mm: ",mm
    WHM = mm.get_all_import_warehouses()
    WHaddress = []
    WHaddress2 = []
    template_name = "zaposta_snippet/DWHaddress.html"

    for location in WHM:
        warehouses = location.get_all_warehouses().filter(country=destination)
        for address in warehouses:
            if address in WHaddress:
                pass
            else:
                WHaddress.append(address)

    for location in WHM:
        warehouses = location.get_all_warehouses().filter(country=origin)
        for address in warehouses:
            if address in WHaddress2:
                pass
            else:
                WHaddress2.append(address)

    first_warehouse = WHaddress2[0].pk
    first_warehouse_add = WHaddress2[0]
    # print "WHaddress:", WHaddress
    return render (request, template_name, {'WHaddress':WHaddress[0], 'first_warehouse':first_warehouse, 'first_warehouse_add':first_warehouse_add})


def homepage(request):
    mm = marketing_member(request)
    print 'the name',mm.storefront_name
    # template_name_lists = ['midasshipping.html', 'marketingmember_index.html','albeemax.html','zeroelectricac.html']
    template_name_lists = ['marketingmember_index.html','albeemax.html','zeroelectricac.html']
    template_name = mm.storefront_name + "." + 'html'
    
    if template_name in template_name_lists:
        template_name = mm.storefront_name + '/' + template_name
    elif mm.storefront_name  == 'zeroelectricac':
        template_name = 'zeroelectricac/zeroelectricac.html'
    elif mm.storefront_name  == 'volkmannexpress':
        try:
            shipping_item = ShippingItem.objects.filter(user=request.user)
            count_items = shipping_item.filter(ordered=False).count()
        except:
            count_items = 0
        template_name = 'vei2018html/index.html'
            # template_name = 'marketingmember_index.html'
    else:
        template_name = 'marketingmember_index.html'
    if request.GET.has_key('promo-shipment-type'):
        shipment_type  =  request.GET['promo-shipment-type']
        #current_promo  =  BatchPromo.objects.filter(shipment_type = shipment_type, is_active=True)
        return render(request, 'zaposta_snippet/promo-snippet.html', {'promo':current_promo,'shipment_type':shipment_type})
    try:
        countries_list,countries_origin,countries_destination = get_route_countries(request)
        #current_promo  =  BatchPromo.objects.filter(shipment_type = "Air Freight", is_active=True)
        
    except Exception as e:
        print 'homepage e: ',e
        pass
        # origin = destination = None
        # current_promo   =   []

    # try:
    #     item=Cart.objects.filter(client=request.user, ordered=False) 
    #     count = item.count()
    #     for i in item:
    #         payable += i.total()
        
    # except:
    #     item =[]
    #     count = 0
    #     payable = 0.0
    #     pass

    payable = 0

    if request.user.is_authenticated:
        payable=0
        count=0
        try:
            item=Cart.objects.filter(client=request.user, ordered=False)
            for i in item:
                payable += i.total()
                count += i.quantity
        except:
            item = []
            payable = 0.0
            count = 0
        
    else:
        item =[]
        count = 0
        payable = 0.0
        
    try:
        list_of_prices = Pricing.objects.filter(marketer=mm)
        # print "LOP: ",list_of_prices
        return render(request, template_name, {'countries_list': countries_list, 'countries_origin':countries_origin, 'countries_destination':countries_destination, 'count':count,'list_of_prices':list_of_prices,'item':item,'payable':payable, 'mm':mm,'count_items':count_items})#,'promo':current_promo})
    except:
        return render(request, template_name, {'countries_list': countries_list, 'countries_origin':countries_origin, 'countries_destination':countries_destination,'count':count, 'item':item,'payable':payable,'mm':mm})#,'promo':current_promo})

def domestic_shipping(request):
    return render(request, 'domestic_shipping.html')


def get_dropoff_locations(request):
    mm = marketing_member(request)
    rG = request.GET
    origin = rG.get('origin')
    destination = rG.get('destination')
    if rG.get('action') == 'get-locations':
        locations = mm.get_route_distributors_locations(origin, destination, 'origin')
    # elif rG.get('action') == 'get-locations':
    #     state = rG.get('state')
    #     locations = mm.get_route_distributors_locations('origin', origin, destination, origin, state)

    #print 'locations: ',locations
    return JsonResponse({'locations': json.dumps(list(locations), cls=DjangoJSONEncoder)})

def get_country_regions(request):
    regions = fetch_country_regions(request.GET.get('origin'))
    return JsonResponse({'regions': json.dumps(list(regions), cls=DjangoJSONEncoder)})

def get_location_address(request):
    location = LocalDistributorLocation.objects.get(pk = request.GET.get('id'))
    return JsonResponse({'location': location.full_address()})

def distributor_api_or_rates(request):
    #localdistr_member = LocalDistributionMember.objects.get(country__name = request.GET.get('origin'))
    origin      = request.GET.get('origin')
    destination = request.GET.get('destination')
    localdistr_member = marketing_member(request).get_route_shipping_distributor(origin, destination, 'origin')
    print 'localdistr_member: ',localdistr_member
    if localdistr_member:
        if localdistr_member.has_api:
            return JsonResponse({'response': 'has_api', 'other': 'has_configured_rates'})
    return JsonResponse({'response': 'has_configured_rates', 'other': 'has_api'})

# def homepage(request):
#     # try:
#     # origin, destination = get_route_chains(request)
#     # except:
#     #     origin = destination = None #remove this later
#     return render(request, 'marketingmember_index.html', {'origin_countries':origin, 'destination_countries':destination})



@csrf_exempt
def joinwaitinglist(request):
    rp = request.POST
    user_email = str(rp.get('email'))
    if request.method == "POST" and user_email:
        user_obj, created = JoinWaitingList.objects.get_or_create(email = user_email)
        if created:
            messages.success(request,"Thank you for joining our waiting list. Your E-mail has been received")
            return redirect(reverse('marketer_homepage'))
        messages.warning(request,"This email is already on our waiting list. Thank you.")

        return redirect(reverse('marketer_homepage'))
    return redirect(reverse('marketer_homepage'))



def legal(request):
    context={}
    mm = marketing_member(request)
    terms = mm.terms_and_cond
    return render(request, 'general_client/T&C.html', {'terms':terms})



def marketerFAQ(request):
    mm = marketing_member(request)
    faq = mm.faq
    return render(request, 'general_client/faq.html', {'faq': faq})



def sendmail(username, title, text):
    context = {}
    template_text = text
    user = User.objects.get(username=username)
    name = user.first_name
    to = user.email
    from_email = None
    subject = title
    msg_text = render_to_string(template_text)
    ctx= {
        'username': name,
        'body': msg_text
        }
    message = get_template('base/base_email.html').render(context(ctx))
    msg = EmailMessage(subject, message, "from_email", [to])
    msg.content_subtype = 'html'
    response = msg.send()
    return response



def suspension(request):
    return render(request, 'suspension.html', {} )

def userregistration_regular(request):
    # redirect_to = redirect (reverse ("homepage"))
    # return subdomain_check(request, redirect_to)

    # try:
    #     if request.subdomain_name and not request.user.is_authenticated():
    #         return redirect(reverse('general:login'))
    # except:
    #     return redirect (reverse ("homepage"))
    mm = marketing_member(request)

    rp = request.POST

    if request.user.is_authenticated():
        return redirect (reverse ("marketer_homepage"))

    form = UserAccountForm
    
    if request.method == 'POST':

        form = UserAccountForm(request.POST, marketer = mm)
        # form = UserAccountForm(request.POST)
        if form.is_valid():

            if User.objects.filter(username=rp.get('username')):
                # user_exist="The username is already taken, please select another."
                if mm.storefront_name  == 'volkmannexpress':
                    return render_to_response('vei2018html/register.html', {'form': form, 'user_exist':True}, context_instance=RequestContext(request))
                else:
                    return render_to_response('general_client/signup_regular.html', {'form': form, 'user_exist':True}, context_instance=RequestContext(request))

            else:

                try:
                    user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password = form.cleaned_data['password'],
                                                    first_name = form.cleaned_data['first_name'], last_name = form.cleaned_data['last_name'])

                except IntegrityError:

                    if mm.storefront_name  == 'volkmannexpress':
                        return render_to_response('vei2018html/register.html', {'form': form, 'user_exist':True}, context_instance=RequestContext(request))
                    else:
                        return render_to_response('general_client/signup_regular.html', {'form': form, 'user_exist':True}, context_instance=RequestContext(request))


            #user.is_active = False
            #user.save()

            #Part of the form that was excluded on the registration page
            registereduser  = form.save(commit=False)

            #registereduser.suite_no = generate_suite_no()

            registereduser.user = user

            registereduser.address_activated = False

            registereduser.registration_time = timezone.now()

            try:
                registereduser.marketer = mm #MarketingMember.objects.get(marketer = request.marketing_member)
            except:
                pass

            #Account Activation Code
            #registereduser.activation_code = ''#get_cart_id(request)#_generate_cart_id()


            registereduser.save()

            #send_activation_code(user)

            #request.session['registrant_name'] = user.get_full_name()

            # print "name:",mm.storefront_name
            text = 'email/Welcome_email.txt'
            user = registereduser.user
            try:
                subject = "Welcome to %s" %mm.storefront_name
                sokohali_sendmail(request, user, subject, text, None)
            except Exception as e:
                print 'reg email error: ',e
                pass

            if mm.storefront_name  == 'volkmannexpress':
                return redirect(reverse("successful_reg"))
            else:
                return redirect(reverse("reg_successful"))


        if mm.storefront_name  == 'volkmannexpress':
            return render_to_response('vei2018html/register.html', {'form': form, 'user_exist':True}, context_instance=RequestContext(request))
        else:
            return render_to_response('general_client/signup_regular.html', {'form': form}, context_instance=RequestContext(request))
    else:
        if mm.storefront_name  == 'volkmannexpress':
            return render_to_response('vei2018html/register.html', {'form': form, 'user_exist':True}, context_instance=RequestContext(request))
        else:
            return render_to_response('general_client/signup_regular.html', {'form': form}, context_instance=RequestContext(request))



class LoginRequest(TemplateView):
    form = LoginForm()

    template_name = 'general_client/login.html'

    def get_context_data(self, *args, **kwargs):
        context = super(LoginRequest, self).get_context_data(**kwargs)
        context["form"] = self.form
        return context

    def post(self, request, *args, **kwargs):
        # request.session['test_key']  = "test value"
        request = self.request

        if request.user.is_authenticated() and not request.GET.has_key('next'):
            return redirect ('/')
        elif request.user.is_authenticated() and request.GET.has_key('next'):
            return redirect (request.GET.get('next', '/'))

        categories = []

        #next = request.GET.get('next', '')
        if request.GET.has_key('next'):
            next_page = request.GET['next']
        #get next from cookies, if user is most likely a first timer
        elif request.COOKIES.has_key('next_page'):
            next_page = request.COOKIES["next_page"]
        else:
            next_page = ""

        error_msg = "There was an error with your E-Mail/Password combination. Please check and try again."

        form = LoginForm(request.POST)

        if form.is_valid():
            username_email  = form.cleaned_data['username_email']
            password        = form.cleaned_data['password']

            mm = marketing_member(request)
            kwargs = {'marketer': mm}
            user = authenticate(email = username_email, password=password, **kwargs)
            if not user:
                user = authenticate(username = username_email, password=password, **kwargs)

            # '''Check if user belongs to marketer'''
            # try:
            #     useraccount = UserAccount.objects.get(user__id = user.pk, marketer = mm)
            # except:
            #     useraccount = None
            if user is None:# or useraccount is None:
                messages.warning(request, error_msg)
                return redirect (request.META.get('HTTP_REFERER', '/'))

            else:
                redirect_to = next_page

                if user.is_active and not user.useraccount.deactivated:
                    ''' Retrieve values from session before login '''
                    shipping_origin           =    request.session.get('shipping_origin', "")
                    shipping_destination      =    request.session.get('shipping_destination', "")
                    pickup_location_key       =    request.session.get('pickup_location_key', "none")
                    has_promo                 =    request.session.get('has_promo', False)
                    promo_price               =    request.session.get('promo_rate', 0.0)
                    dropoff_state             =    request.session.get('dropoff_state')

                    #print 'before shipping_origin, shipping_destination: ',shipping_origin, shipping_destination

                    login(request, user)

                    '''set values in session after login'''
                    request.session['shipping_origin']              =   shipping_origin
                    request.session['shipping_destination']         =   shipping_destination
                    request.session['pickup_location_key']          =   pickup_location_key
                    request.session['has_promo']                    =   has_promo
                    request.session['promo_rate']                   =   promo_price
                    request.session['dropoff_state']                =   dropoff_state

                    #print 'after shipping_origin, shipping_destination: ',shipping_origin, shipping_destination

                    if user.is_staff:
                        if redirect_to == '':
                            response = redirect (reverse ("sokohaliAdmin:user-manager"))
                        else:
                            #return redirect(redirect_to)
                            response = redirect(redirect_to)

                        max_age_seconds = 3600
                        set_cookie(request, response, "admin_username", request.user.username, max_age_seconds)

                    else:
                        #del next_page from cookies
                        if redirect_to == '':
                            #response = redirect (reverse ("general:my_account"))
                            response = redirect (reverse ("marketer_homepage"))
                        else:
                            response = redirect(redirect_to)

                        if request.COOKIES.has_key('next_page'):
                            #remove cookie
                            response.delete_cookie("next_page")

                        if request.COOKIES.has_key('admin_username'):
                            #remove cookie
                            response.delete_cookie("admin_username")

                    return response

                        #return redirect(redirect_to)
                else:
                    error_msg = "Sorry, you need to activate your account before you can log-in.\
                                    Please contact customer service. Thank you."
                    messages.warning(request, error_msg)
                    return redirect (request.META.get('HTTP_REFERER', '/'))

        else:
            messages.warning(request, error_msg)
            return redirect (request.META.get('HTTP_REFERER', '/'))


    def get(self, request, *args, **kwargs):
        context = super(LoginRequest, self).get(request, *args, **kwargs)

        if request.user.is_authenticated():
            return redirect (reverse ("marketer_homepage"))
        return super(LoginRequest, self).get(request, *args, **kwargs)


    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(sensitive_post_parameters())
    def dispatch(self, *args, **kwargs):
        return super(LoginRequest, self).dispatch(*args, **kwargs)


class LoginRequestNew(TemplateView):
    form = LoginForm()

    template_name = 'vei2018html/login.html'

    def get_context_data(self, *args, **kwargs):
        context = super(LoginRequestNew, self).get_context_data(**kwargs)
        context["form"] = self.form
        return context

    def post(self, request, *args, **kwargs):
        # request.session['test_key']  = "test value"
        request = self.request

        if request.user.is_authenticated() and not request.GET.has_key('next'):
            return redirect ('/')
        elif request.user.is_authenticated() and request.GET.has_key('next'):
            return redirect (request.GET.get('next', '/'))

        categories = []

        #next = request.GET.get('next', '')
        if request.GET.has_key('next'):
            next_page = request.GET['next']
        #get next from cookies, if user is most likely a first timer
        elif request.COOKIES.has_key('next_page'):
            next_page = request.COOKIES["next_page"]
        else:
            next_page = ""

        error_msg = "There was an error with your E-Mail/Password combination. Please check and try again."

        form = LoginForm(request.POST)

        if form.is_valid():
            username_email  = form.cleaned_data['username_email']
            password        = form.cleaned_data['password']

            mm = marketing_member(request)
            kwargs = {'marketer': mm}
            user = authenticate(email = username_email, password=password, **kwargs)
            if not user:
                user = authenticate(username = username_email, password=password, **kwargs)

            # '''Check if user belongs to marketer'''
            # try:
            #     useraccount = UserAccount.objects.get(user__id = user.pk, marketer = mm)
            # except:
            #     useraccount = None
            if user is None:# or useraccount is None:
                messages.warning(request, error_msg)
                return redirect (request.META.get('HTTP_REFERER', '/'))

            else:
                redirect_to = next_page

                if user.is_active and not user.useraccount.deactivated:
                    ''' Retrieve values from session before login '''
                    shipping_origin           =    request.session.get('shipping_origin', "")
                    shipping_destination      =    request.session.get('shipping_destination', "")
                    pickup_location_key       =    request.session.get('pickup_location_key', "none")
                    has_promo                 =    request.session.get('has_promo', False)
                    promo_price               =    request.session.get('promo_rate', 0.0)
                    dropoff_state             =    request.session.get('dropoff_state')

                    #print 'before shipping_origin, shipping_destination: ',shipping_origin, shipping_destination

                    login(request, user)

                    '''set values in session after login'''
                    request.session['shipping_origin']              =   shipping_origin
                    request.session['shipping_destination']         =   shipping_destination
                    request.session['pickup_location_key']          =   pickup_location_key
                    request.session['has_promo']                    =   has_promo
                    request.session['promo_rate']                   =   promo_price
                    request.session['dropoff_state']                =   dropoff_state

                    #print 'after shipping_origin, shipping_destination: ',shipping_origin, shipping_destination

                    if user.is_staff:
                        if redirect_to == '':
                            response = redirect (reverse ("sokohaliAdmin:user-manager"))
                        else:
                            #return redirect(redirect_to)
                            response = redirect(redirect_to)

                        max_age_seconds = 3600
                        set_cookie(request, response, "admin_username", request.user.username, max_age_seconds)

                    else:
                        #del next_page from cookies
                        if redirect_to == '':
                            #response = redirect (reverse ("general:my_account"))
                            response = redirect (reverse ("general:my_mail_bag_volk"))
                        else:
                            response = redirect(redirect_to)

                        if request.COOKIES.has_key('next_page'):
                            #remove cookie
                            response.delete_cookie("next_page")

                        if request.COOKIES.has_key('admin_username'):
                            #remove cookie
                            response.delete_cookie("admin_username")

                    return response

                        #return redirect(redirect_to)
                else:
                    error_msg = "Sorry, you need to activate your account before you can log-in.\
                                    Please contact customer service. Thank you."
                    messages.warning(request, error_msg)
                    return redirect (request.META.get('HTTP_REFERER', '/'))

        else:
            messages.warning(request, error_msg)
            return redirect (request.META.get('HTTP_REFERER', '/'))


    def get(self, request, *args, **kwargs):
        context = super(LoginRequestNew, self).get(request, *args, **kwargs)

        if request.user.is_authenticated():
            return redirect (reverse ("general:my_mail_bag_volk"))
        return super(LoginRequestNew, self).get(request, *args, **kwargs)


    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(sensitive_post_parameters())
    def dispatch(self, *args, **kwargs):
        return super(LoginRequestNew, self).dispatch(*args, **kwargs)



def logoutRequest(request):
    logout(request)
    return HttpResponseRedirect(reverse ("marketer_homepage"))


'''USER ACCOUNT FUNCTIONS'''

@login_required
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(address_activated, login_url='/redirect_to_address_activation_new/', redirect_field_name=None )
def user_account_volk(request):
    mm = marketing_member(request)
    import_warehouses = request.user.useraccount.marketer.get_all_import_warehouses()
    #print 'warehouses:',import_warehouses
    put_location = []
    for warehouse in import_warehouses:
        whm = warehouse.get_all_warehouses()
        for WH in whm:
            if WH in put_location:
                pass
            else:
                put_location.append(WH)

    shipping_item = ShippingItem.objects.filter(user=request.user)
    count_items = shipping_item.filter(ordered=False).count()
    #print "locations:",put_location
    origin, destination = get_route_chains(request)
    return render(request, "user_account/user_account.html", {'origin_countries':origin, 'destination_countries':destination, 'warehouses':put_location,'count':count_items})



@login_required
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/admin/my-account/')
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None )
def user_account(request):
    mm = marketing_member(request)
    import_warehouses = request.user.useraccount.marketer.get_all_import_warehouses()
    #print 'warehouses:',import_warehouses
    put_location = []
    for warehouse in import_warehouses:
        whm = warehouse.get_all_warehouses()
        for WH in whm:
            if WH in put_location:
                pass
            else:
                put_location.append(WH)

    shipping_item = ShippingItem.objects.filter(user=request.user)
    count_items = shipping_item.filter(ordered=False).count()
    #print "locations:",put_location
    origin, destination = get_route_chains(request)
    return render(request, "user_account/user_account.html", {'origin_countries':origin, 'destination_countries':destination, 'warehouses':put_location,'count':count_items})


def export_landing_page(request):
    return render(request, 'general_client/export_landing_page.html', {'source':'export_booking'} )



@login_required
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None)
def view_delivery_addresses(request):
    mm = marketing_member(request)
    import_warehouses = request.user.useraccount.marketer.get_all_import_warehouses()
    put_location = []
    for warehouse in import_warehouses:
        whm = warehouse.get_all_warehouses()
        for WH in whm:
            if WH in put_location:
                pass
            else:
                put_location.append(WH)
        # print "locations:",put_location
    # print "locations:",put_location
    origin,destination = get_route_chains(request)
    if mm.storefront_name == "volkmannexpress":
        template_name = "volkmann/my_addresses.html"
    else:
        template_name = "user_account/view_delivery_addresses.html"
    return render(request, template_name, {'warehouses':put_location,'origin_countries':origin, 'destination_countries':destination})


@login_required(login_url='/volk/login/')
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(address_activated_new, login_url='/redirect_to_address_activation_new/', redirect_field_name=None)
def view_delivery_addresses_volk(request):

    mm = marketing_member(request)
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    import_warehouses = request.user.useraccount.marketer.get_all_import_warehouses()
    put_location = []
    
    for warehouse in import_warehouses:
        whm = warehouse.get_all_warehouses()
        for WH in whm:
            if WH in put_location:
                pass
            else:
                put_location.append(WH)
        # print "locations:",put_location
    # print "locations:",put_location
    origin,destination = get_route_chains(request)
    if mm.storefront_name == "volkmannexpress":
        template_name = "volkmann/my_addresses.html"
    else:
        template_name = "user_account/view_delivery_addresses.html"
    return render(request, template_name, {'warehouses':put_location,'origin_countries':origin, 'destination_countries':destination, 'count_items':count_items})

@login_required
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/admin/my-account/')
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None)
def my_mail_bag(request):

    try:
        mm = marketing_member(request)
        subscriber = mm.subscriber
        print "subscriber:",subscriber
        marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
    except:
        subscriber = request_subscriber(request)
        marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)

    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    addresses = DeliveryAddress.objects.filter(user=request.user)
    template_name = "user_account/mail_bag.html"
    return render(request, template_name, {'items':shipping_item,'count_items':count_items,'marketer_routes':marketer_routes,'addresses':addresses})
    # return render(request, template_name, {'warehouses':put_location,'origin_countries':origin, 'destination_countries':destination})


@login_required(login_url='/volk/login/')
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(address_activated_new, login_url='/redirect_to_address_activation_new/', redirect_field_name=None)
def my_mail_bag_volk(request):

    try:
        mm = marketing_member(request)
        subscriber = mm.subscriber
        print "subscriber:",subscriber
        marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
    except:
        subscriber = request_subscriber(request)
        marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
        
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
        count_processed = shipping_item.filter(ordered=True).count()
        count_total = count_items + count_processed
    except:
        count_items = 0

    addresses = DeliveryAddress.objects.filter(user=request.user)
    template_name = "volkmann/mailbag.html"
    return render(request, template_name, {'count_p':count_processed,'count_t':count_total,'items':shipping_item,'count_items':count_items,'marketer_routes':marketer_routes,'addresses':addresses})
    # return render(request, template_name, {'warehouses':put_location,'origin_countries':origin, 'destination_countries':destination})


@login_required
@csrf_exempt
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/admin/my-account/')
@user_passes_test(flagged_check, login_url='/bank-deposit-verification/', redirect_field_name = None)
def my_shipments(request):

    origin, destination = get_route_chains(request)

    try:
        mm = marketing_member(request)
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    context_dict = {}
    context_dict.update({'origin_countries':origin, 'destination_countries':destination})

    if request.method == "GET" or 'track' in request.GET.keys():
        package = None
        if request.GET.has_key('print_label'):
            try:
                # try:
                #     package =  get_object_or_404(ExportPackage, tracking_number = request.GET['pkg_id'])
                # except:
                package =  get_object_or_404(ShippingPackage, tracking_number = request.GET['pkg_id'])
            except:
                message = "No records found for package number %s" %(request.GET['pkg_id'])
                messages.info(request, message)
            return render(request, 'export_snippet/package_label_modal.html',{'package': package})

        template_name = "user_account/user_shipments.html"

        if request.GET.has_key('tracking_number'):
            try:
                # try:
                #     package =  get_object_or_404(ExportPackage, tracking_number = request.GET['tracking_number'])
                # except:
                package =  get_object_or_404(ShippingPackage, tracking_number = request.GET['tracking_number'])
            except:
                context_dict.update({'no_record_found':True})
                message = "No records found for tracking number %s" %(request.GET['tracking_number'])
                messages.info(request, message)

            context_dict.update({'package': package})

        shipping_packages = ShippingPackage.objects.filter(Q(user = request.user), Q(deleted = False), Q(is_estimate = False), Q(ordered = True)) # add condition to remove estimate packages

        packages = paginate_list(request, list(reversed(sorted(shipping_packages, key=lambda instance: instance.created_on))), 10)

    if request.method == 'POST':
        # if not request.session.has_key('fedExLocs'):
        #    fedExLocs = FedExLocation.objects.all()
        #    request.session['fedExLocs'] = fedExLocs
        #
        # if not request.session.has_key('addresses'):
        #    addresses = ExportAddressBook.objects.filter(user = request.user)
        #    request.session['addresses'] = addresses
        #
        # #print "fedExLocs: ",fedExLocs
        # #print "fedExLocs: ",request.session["fedExLocs"]
        # fedExLocs = request.session['fedExLocs']
        # addresses = request.session['addresses']
        #
        # # pkg_statuses = ['Prepared for Shipping', 'Assigned to batch',
        # # 'Delivered to Carrier', 'Departed', 'Clearing Customs', 'Processing for Delivery',
        # # 'Prepared for Delivery', 'Enroute to Delivery', 'Ready for Collection', 'Delivered']
        #
        # #pkg_statuses = ['Delivered', 'Ready for Collection', 'Enroute to Delivery', 'Prepared for Delivery',
        # #                 'Processing for Delivery', 'Clearing Customs', 'Departed', 'Delivered to Carrier',
        # #                'Assigned to batch', 'Prepared for Shipping']
        # form_vars = ['edit_address', 'add_address']
        # response_dict = {'fedExLocs': fedExLocs, 'addresses': addresses, 'form_vars': form_vars}
        #response_dict = {'fedExLocs': fedExLocs, 'addresses': addresses}#, 'pkg_statuses': pkg_statuses}
        rp = request.POST
        response_dict = {}
        if 'track' in rp:
            tracking_number = rp["tracking_number"]
            #response_dict = {'exports': exports}#{'shipments': shipments}
            try:
                # try:
                #     package = Export.objects.get(tracking_number = tracking_number)
                # except:
                package = ShippingPackage.objects.get(tracking_number = tracking_number)
            except:
                messages.info(request, "No matching record found for tracking number: %s" %tracking_number)

            response_dict.update({'package': package})
            return render(request, template_name, response_dict)

          #print rp
        # if 'edit_shipment' in rp:
        #     shipment_id = rp['id']
        #     shipment = get_object_or_404(Shipment, pk=shipment_id)
        #     #packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)
        #     packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
        #                                                                                    approved = True, deleted = False)
        #     #unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)
        #     #fedExLocs           = []
        #     response_dict.update({'shipment': shipment, 'packages': packages})
        #     return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
                          #{'shipment': shipment, 'packages': packages, 'fedExLocs': fedExLocs})

        if 'collapse_shipment' in rp:
            #pkg = object()
            #if rp['is_export'] == 'True':
            #print rp
            # if rp['shipment_type'] == 'export':
            #     pkg = get_object_or_404(ExportPackage, pk = rp['obj_id'])
            # else:
            pkg = get_object_or_404(ShippingPackage, pk = rp['obj_id'])
            lb_country = pkg.costcalc_instance.country
            # if pkg.shipping_chain.origin == "United States":
            #     lb_country = pkg.shipping_chain.destination
            # else:
            #     lb_country = pkg.shipping_chain.origin
            response_dict.update({'pkg': pkg,'lb_country':lb_country})
            return render(request, 'zaposta_snippet/collapse_shipment.html', response_dict)
                        #{'shipment': shipment})

        #if 'shipment_id' in request.POST:
        # if 'edit_address' in rp.values() or 'add_address' in rp.values():
        #     try:
        #         shipment_id = rp['shipment_id']
        #         shipment = Shipment.objects.get(pk = shipment_id)
        #
        #         if 'edit_address' in rp.values():
        #             history_status = "Package Destination Edited"
        #
        #             shipment.full_name  = rp.get('full_name', '')
        #             shipment.address    = rp.get('address', '')
        #             shipment.city       = rp.get('city', '')
        #             shipment.state      = rp.get('state', '')
        #             shipment.telephone  = rp.get('telephone', '')
        #             tracking_number     = shipment.tracking_number
        #             shipment.save()
        #
        #         else:
        #             history_status = "New Package Destination Added"
        #
        #             shipment_address            = AddressBook()
        #             shipment_address.user       = request.user
        #             shipment_address.full_name  = rp.get('full_name', '')
        #             shipment_address.address    = rp.get('address', '')
        #             shipment_address.city       = rp.get('city', '')
        #             shipment_address.state      = rp.get('state', '')
        #             shipment_address.telephone  = rp.get('telephone', '')
        #             shipment_address.country    = rp.get('country', '')
        #             shipment_address.save()
        #
        #
        #         history = ShipmentEditHistory()
        #         history.user = request.user
        #         history.status = history_status
        #         history.shipment = shipment
        #         history.save()
        #
        #         addresses = AddressBook.objects.filter(user = request.user)
        #         request.session['addresses'] = addresses
        #
        #
        #         if 'edit_address' in rp.values():
        #             shipment = Shipment.objects.get(pk = shipment_id)
        #             packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
        #                                                                                            approved = True, deleted = False)
        #             #unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)
        #             response_dict.update({'shipment': shipment, 'packages': packages})
        #             return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
        #                       #{'shipment': shipment, 'packages': packages})
        #         else:
        #             new_address_div = '<div class="col-md-12 item adds select" style="margin-top:15px;" address-id="'+str(shipment_address.id)+'"><p><strong>'+shipment_address.full_name+'</strong>'+shipment_address.delivery_address()+'</p></div>'
        #             return JsonResponse({'result': 'success', 'new_address_div': new_address_div})
        #     except:
        #         return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})

        # if 'edit_item' in rp.values():
        #     try:
        #        item_id = rp['item_id']
        #        item = ShipmentItem.objects.get(pk = item_id)
        #        #print item
        #
        #        exchange_rate = country_exchange_rate(item.country, item.shipment.costcalc_instance)
        #
        #        description = item.description
        #        item.courier_tracking_number  = rp.get('courier_tracking_number', '')
        #        item.description              = rp.get('description', '')
        #        item.quantity                 = rp.get('quantity', '')
        #        total_value                   = rp.get('total_value', '')
        #        item.total_value              = total_value
        #        if total_value != '':
        #             item.total_value_N = float(total_value) * exchange_rate #dollarNairaRate
        #        item.save()
        #
        #        history = ShipmentEditHistory()
        #        history.user = request.user
        #        history.status = "Edited"
        #        history.shipment = item.shipment
        #        history.item = item
        #        history.save()
        #
        #        shipment = item.shipment
        #        tracking_number =  shipment.tracking_number #item.shipment.tracking_number
        #        alert = '%s successfully updated' %description
        #        messages.success(request, alert)
        #
        #        packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
        #                                                                                       approved = True, deleted = False)
        #
        #        response_dict.update({'shipment': shipment, 'packages': packages})
        #        return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
        #     except:
        #         return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})
        if 'delete_item' in rp:

             item                = ShipmentItem.objects.get(pk = rp['item_id'])

             tracking_number     =  item.shipment.tracking_number
             description         = item.description


             history = ShipmentEditHistory()
             history.user = request.user
             history.status = "Deleted"
             history.shipment = item.shipment
             history.item = item
             history.save()

             item.deleted = True
             item.save()

             alert = '%s successfully deleted' %description
             messages.success(request, alert)

             shipment = Shipment.objects.get(pk = rp['shipment'])
             packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
                                                                                            approved = True, deleted = False)

             response_dict.update({'shipment': shipment, 'packages': packages})
             return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)

        if 'add_item' in rp.values():
            try:
                shipment_id = rp['shipment']
                shipment = Shipment.objects.get(pk = shipment_id)
                exchange_rate = country_exchange_rate(shipment.country, shipment.costcalc_instance)
                item = ShipmentItem()
                item.user = request.user
                item.shipment = shipment

                item.courier_tracking_number = rp.get('courier_tracking_number', '')
                item.description = rp.get('description', '')
                item.quantity = rp.get('quantity', '')
                total_value = rp.get('total_value', '')
                item.total_value = total_value
                if total_value != '':
                     item.total_value_N = float(total_value) * exchange_rate #dollarNairaRate
                item.save()

                history = ShipmentEditHistory()
                history.user = request.user
                history.status = "Added"
                history.shipment = shipment
                history.item = item
                history.save()

                alert = '%s successfully added' %rp['description']
                messages.success(request, alert)

                shipment = Shipment.objects.get(pk = shipment_id)
                packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)

                response_dict.update({'shipment': shipment, 'packages': packages})
                return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
                              #{'shipment': shipment, 'packages': packages})
            except:
                return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})


        if 'send_invoice' in rp:
            id = request.POST['shipment']
            s = Shipment.objects.get(pk = id)
            user = s.user

            alert = 'Invoice Successfully sent to your E-mail address'
            shipments = Shipment.objects.filter(user=request.user)
            #user_details = request.user.get_profile
            user_details = get_object_or_404(UserAccount, user = request.user)
            status3 = PackageStatusSettings.objects.get(pk = 1).status3

            send_confirmation_mail(user, s)
            return redirect (request.META.get('HTTP_REFERER', '/'))

        if 'view_handling_options' in rp:
            id = request.POST['shipment']
            shipment = Shipment.objects.get(pk = id)

            return render_to_response('tags/edit_handling_options.html',
                                      {'shipment': shipment}, context_instance=RequestContext(request))

        if 'edit_handling' in rp.values():
            shipment_id = request.POST['shipment']
            shipment = Shipment.objects.get(pk = shipment_id)

            #print request.POST

            if not shipment.if_pkg_prepared_for_shipping():

                 if request.POST.has_key('insure'):
                      shipment.insure = True
                 else:
                      shipment.insure = False

                 if request.POST.has_key('consolidate'):
                      shipment.consolidate = True
                 else:
                      shipment.consolidate = False

                 if request.POST.has_key('strip'):
                      shipment.strip_my_package = True
                 else:
                      shipment.strip_my_package = False

                 int_freight = request.POST["int_freight"]
                 dm_freight = request.POST["dm_freight"]

                 dm = "%s-%s"  %(int_freight, dm_freight)

                 #print "dm: ",dm
                 #if request.POST.has_key('dm'):
                 #     dm = request.POST['dm']
                 update_delivery_option(dm, shipment)

                 dvm = "%s - %s" %(int_freight, dm_freight)
                 dvm = dvm.upper()

                 delivery_city = request.POST["hidden_dm_location"]
                 if delivery_city != '':
                     address_id = selected_delivery_address_id(request.user, dvm, delivery_city)
                 else:
                     address_id = request.POST["address_book"]

                 destination = AddressBook.objects.get(pk = address_id)
                 shipment.full_name = "%s %s" %(destination.first_name, destination.last_name)
                 shipment.address   = destination.address
                 shipment.city      = destination.city
                 shipment.state     = destination.state
                 #shipment.postal_code = destination.postal_code
                 shipment.telephone   = destination.telephone

                 shipment.save()

                 history = ShipmentEditHistory()
                 history.user = request.user
                 history.status = "Handling and Delivery Options Changed"
                 history.shipment = shipment
                 history.save()

            alert = "Booking %s Handling and Delivery Option successfully changed" %shipment.tracking_number
            messages.success(request, alert)

            # #Update the cost calc for the shipment
            ShipmentCostCalc(request, shipment, shipment.country)

            #calling the shipment back to get it's current state
            shipment = Shipment.objects.get(pk = shipment_id)
            packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)
            #unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)

            response_dict.update({'shipment': shipment, 'packages': packages})
            return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
                          #{'shipment': shipment, 'packages': packages})


               # #Update the cost calc for the shipment
               # ShipmentCostCalc(request, shipment, shipment.country)
               #
               # alert = "Booking %s Handling and Delivery Option successfully changed" %shipment.tracking_number
               # messages.success(request, alert)
               #
               # return redirect (request.META.get('HTTP_REFERER', '/'))


    else:
          #user = request.user
          if mm.storefront_name == "volkmannexpress":
            template_name = "volkmann/accountpage.html"
          #shipments = Shipment.objects.prefetch_related('shipmentpackage_set').filter(user = request.user, cancelled = False)
          shipments = ShippingPackage.objects.filter(user = request.user, deleted=False)
          context_dict.update({'packages': packages,'count_items':count_items,'shipments':shipments})
          return render_to_response(template_name,
                                   context_dict,#, 'user_details': user_details, 'status3': status3,
                                    #'user_credit_amount_N': user_credit_amount_N},
                                   context_instance=RequestContext(request))


@login_required(login_url='/volk/login/')
@csrf_exempt
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(flagged_check, login_url='/bank-deposit-verification/', redirect_field_name = None)
def my_shipments_volk(request):

    origin, destination = get_route_chains(request)

    try:
        mm = marketing_member(request)
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    context_dict = {}
    context_dict.update({'origin_countries':origin, 'destination_countries':destination})

    if request.method == "GET" or 'track' in request.GET.keys():
        package = None
        if request.GET.has_key('print_label'):
            try:
                # try:
                #     package =  get_object_or_404(ExportPackage, tracking_number = request.GET['pkg_id'])
                # except:
                package =  get_object_or_404(ShippingPackage, tracking_number = request.GET['pkg_id'])
            except:
                message = "No records found for package number %s" %(request.GET['pkg_id'])
                messages.info(request, message)
            return render(request, 'export_snippet/package_label_modal.html',{'package': package})

        template_name = "user_account/user_shipments.html"

        if request.GET.has_key('tracking_number'):
            try:
                # try:
                #     package =  get_object_or_404(ExportPackage, tracking_number = request.GET['tracking_number'])
                # except:
                package =  get_object_or_404(ShippingPackage, tracking_number = request.GET['tracking_number'])
            except:
                context_dict.update({'no_record_found':True})
                message = "No records found for tracking number %s" %(request.GET['tracking_number'])
                messages.info(request, message)

            context_dict.update({'package': package})

        shipping_packages = ShippingPackage.objects.filter(Q(user = request.user), Q(deleted = False), Q(is_estimate = False), Q(ordered = True)) # add condition to remove estimate packages


        packages = paginate_list(request, list(reversed(sorted(shipping_packages, key=lambda instance: instance.created_on))), 10)

    if request.method == 'POST':
        # if not request.session.has_key('fedExLocs'):
        #    fedExLocs = FedExLocation.objects.all()
        #    request.session['fedExLocs'] = fedExLocs
        #
        # if not request.session.has_key('addresses'):
        #    addresses = ExportAddressBook.objects.filter(user = request.user)
        #    request.session['addresses'] = addresses
        #
        # #print "fedExLocs: ",fedExLocs
        # #print "fedExLocs: ",request.session["fedExLocs"]
        # fedExLocs = request.session['fedExLocs']
        # addresses = request.session['addresses']
        #
        # # pkg_statuses = ['Prepared for Shipping', 'Assigned to batch',
        # # 'Delivered to Carrier', 'Departed', 'Clearing Customs', 'Processing for Delivery',
        # # 'Prepared for Delivery', 'Enroute to Delivery', 'Ready for Collection', 'Delivered']
        #
        # #pkg_statuses = ['Delivered', 'Ready for Collection', 'Enroute to Delivery', 'Prepared for Delivery',
        # #                 'Processing for Delivery', 'Clearing Customs', 'Departed', 'Delivered to Carrier',
        # #                'Assigned to batch', 'Prepared for Shipping']
        # form_vars = ['edit_address', 'add_address']
        # response_dict = {'fedExLocs': fedExLocs, 'addresses': addresses, 'form_vars': form_vars}
        #response_dict = {'fedExLocs': fedExLocs, 'addresses': addresses}#, 'pkg_statuses': pkg_statuses}
        rp = request.POST
        response_dict = {}
        if 'track' in rp:
            tracking_number = rp["tracking_number"]
            #response_dict = {'exports': exports}#{'shipments': shipments}
            try:
                # try:
                #     package = Export.objects.get(tracking_number = tracking_number)
                # except:
                package = ShippingPackage.objects.get(tracking_number = tracking_number)
            except:
                messages.info(request, "No matching record found for tracking number: %s" %tracking_number)

            response_dict.update({'package': package})
            return render(request, template_name, response_dict)

          #print rp
        # if 'edit_shipment' in rp:
        #     shipment_id = rp['id']
        #     shipment = get_object_or_404(Shipment, pk=shipment_id)
        #     #packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)
        #     packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
        #                                                                                    approved = True, deleted = False)
        #     #unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)
        #     #fedExLocs           = []
        #     response_dict.update({'shipment': shipment, 'packages': packages})
        #     return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
                          #{'shipment': shipment, 'packages': packages, 'fedExLocs': fedExLocs})

        if 'collapse_shipment' in rp:
            #pkg = object()
            #if rp['is_export'] == 'True':
            #print rp
            # if rp['shipment_type'] == 'export':
            #     pkg = get_object_or_404(ExportPackage, pk = rp['obj_id'])
            # else:
            pkg = get_object_or_404(ShippingPackage, pk = rp['obj_id'])
            lb_country = pkg.costcalc_instance.country
            # if pkg.shipping_chain.origin == "United States":
            #     lb_country = pkg.shipping_chain.destination
            # else:
            #     lb_country = pkg.shipping_chain.origin
            response_dict.update({'pkg': pkg,'lb_country':lb_country})
            return render(request, 'zaposta_snippet/collapse_shipment.html', response_dict)
                        #{'shipment': shipment})

        #if 'shipment_id' in request.POST:
        # if 'edit_address' in rp.values() or 'add_address' in rp.values():
        #     try:
        #         shipment_id = rp['shipment_id']
        #         shipment = Shipment.objects.get(pk = shipment_id)
        #
        #         if 'edit_address' in rp.values():
        #             history_status = "Package Destination Edited"
        #
        #             shipment.full_name  = rp.get('full_name', '')
        #             shipment.address    = rp.get('address', '')
        #             shipment.city       = rp.get('city', '')
        #             shipment.state      = rp.get('state', '')
        #             shipment.telephone  = rp.get('telephone', '')
        #             tracking_number     = shipment.tracking_number
        #             shipment.save()
        #
        #         else:
        #             history_status = "New Package Destination Added"
        #
        #             shipment_address            = AddressBook()
        #             shipment_address.user       = request.user
        #             shipment_address.full_name  = rp.get('full_name', '')
        #             shipment_address.address    = rp.get('address', '')
        #             shipment_address.city       = rp.get('city', '')
        #             shipment_address.state      = rp.get('state', '')
        #             shipment_address.telephone  = rp.get('telephone', '')
        #             shipment_address.country    = rp.get('country', '')
        #             shipment_address.save()
        #
        #
        #         history = ShipmentEditHistory()
        #         history.user = request.user
        #         history.status = history_status
        #         history.shipment = shipment
        #         history.save()
        #
        #         addresses = AddressBook.objects.filter(user = request.user)
        #         request.session['addresses'] = addresses
        #
        #
        #         if 'edit_address' in rp.values():
        #             shipment = Shipment.objects.get(pk = shipment_id)
        #             packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
        #                                                                                            approved = True, deleted = False)
        #             #unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)
        #             response_dict.update({'shipment': shipment, 'packages': packages})
        #             return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
        #                       #{'shipment': shipment, 'packages': packages})
        #         else:
        #             new_address_div = '<div class="col-md-12 item adds select" style="margin-top:15px;" address-id="'+str(shipment_address.id)+'"><p><strong>'+shipment_address.full_name+'</strong>'+shipment_address.delivery_address()+'</p></div>'
        #             return JsonResponse({'result': 'success', 'new_address_div': new_address_div})
        #     except:
        #         return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})

        # if 'edit_item' in rp.values():
        #     try:
        #        item_id = rp['item_id']
        #        item = ShipmentItem.objects.get(pk = item_id)
        #        #print item
        #
        #        exchange_rate = country_exchange_rate(item.country, item.shipment.costcalc_instance)
        #
        #        description = item.description
        #        item.courier_tracking_number  = rp.get('courier_tracking_number', '')
        #        item.description              = rp.get('description', '')
        #        item.quantity                 = rp.get('quantity', '')
        #        total_value                   = rp.get('total_value', '')
        #        item.total_value              = total_value
        #        if total_value != '':
        #             item.total_value_N = float(total_value) * exchange_rate #dollarNairaRate
        #        item.save()
        #
        #        history = ShipmentEditHistory()
        #        history.user = request.user
        #        history.status = "Edited"
        #        history.shipment = item.shipment
        #        history.item = item
        #        history.save()
        #
        #        shipment = item.shipment
        #        tracking_number =  shipment.tracking_number #item.shipment.tracking_number
        #        alert = '%s successfully updated' %description
        #        messages.success(request, alert)
        #
        #        packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
        #                                                                                       approved = True, deleted = False)
        #
        #        response_dict.update({'shipment': shipment, 'packages': packages})
        #        return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
        #     except:
        #         return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})
        if 'delete_item' in rp:

             item                = ShipmentItem.objects.get(pk = rp['item_id'])

             tracking_number     =  item.shipment.tracking_number
             description         = item.description


             history = ShipmentEditHistory()
             history.user = request.user
             history.status = "Deleted"
             history.shipment = item.shipment
             history.item = item
             history.save()

             item.deleted = True
             item.save()

             alert = '%s successfully deleted' %description
             messages.success(request, alert)

             shipment = Shipment.objects.get(pk = rp['shipment'])
             packages = ShipmentPackage.objects.prefetch_related('shipmentitem_set').filter(shipment = shipment,
                                                                                            approved = True, deleted = False)

             response_dict.update({'shipment': shipment, 'packages': packages})
             return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)

        if 'add_item' in rp.values():
            try:
                shipment_id = rp['shipment']
                shipment = Shipment.objects.get(pk = shipment_id)
                exchange_rate = country_exchange_rate(shipment.country, shipment.costcalc_instance)
                item = ShipmentItem()
                item.user = request.user
                item.shipment = shipment

                item.courier_tracking_number = rp.get('courier_tracking_number', '')
                item.description = rp.get('description', '')
                item.quantity = rp.get('quantity', '')
                total_value = rp.get('total_value', '')
                item.total_value = total_value
                if total_value != '':
                     item.total_value_N = float(total_value) * exchange_rate #dollarNairaRate
                item.save()

                history = ShipmentEditHistory()
                history.user = request.user
                history.status = "Added"
                history.shipment = shipment
                history.item = item
                history.save()

                alert = '%s successfully added' %rp['description']
                messages.success(request, alert)

                shipment = Shipment.objects.get(pk = shipment_id)
                packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)

                response_dict.update({'shipment': shipment, 'packages': packages})
                return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
                              #{'shipment': shipment, 'packages': packages})
            except:
                return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})


        if 'send_invoice' in rp:
            id = request.POST['shipment']
            s = Shipment.objects.get(pk = id)
            user = s.user

            alert = 'Invoice Successfully sent to your E-mail address'
            shipments = Shipment.objects.filter(user=request.user)
            #user_details = request.user.get_profile
            user_details = get_object_or_404(UserAccount, user = request.user)
            status3 = PackageStatusSettings.objects.get(pk = 1).status3

            send_confirmation_mail(user, s)
            return redirect (request.META.get('HTTP_REFERER', '/'))

        if 'view_handling_options' in rp:
            id = request.POST['shipment']
            shipment = Shipment.objects.get(pk = id)

            return render_to_response('tags/edit_handling_options.html',
                                      {'shipment': shipment}, context_instance=RequestContext(request))

        if 'edit_handling' in rp.values():
            shipment_id = request.POST['shipment']
            shipment = Shipment.objects.get(pk = shipment_id)

            #print request.POST

            if not shipment.if_pkg_prepared_for_shipping():

                 if request.POST.has_key('insure'):
                      shipment.insure = True
                 else:
                      shipment.insure = False

                 if request.POST.has_key('consolidate'):
                      shipment.consolidate = True
                 else:
                      shipment.consolidate = False

                 if request.POST.has_key('strip'):
                      shipment.strip_my_package = True
                 else:
                      shipment.strip_my_package = False

                 int_freight = request.POST["int_freight"]
                 dm_freight = request.POST["dm_freight"]

                 dm = "%s-%s"  %(int_freight, dm_freight)

                 #print "dm: ",dm
                 #if request.POST.has_key('dm'):
                 #     dm = request.POST['dm']
                 update_delivery_option(dm, shipment)

                 dvm = "%s - %s" %(int_freight, dm_freight)
                 dvm = dvm.upper()

                 delivery_city = request.POST["hidden_dm_location"]
                 if delivery_city != '':
                     address_id = selected_delivery_address_id(request.user, dvm, delivery_city)
                 else:
                     address_id = request.POST["address_book"]

                 destination = AddressBook.objects.get(pk = address_id)
                 shipment.full_name = "%s %s" %(destination.first_name, destination.last_name)
                 shipment.address   = destination.address
                 shipment.city      = destination.city
                 shipment.state     = destination.state
                 #shipment.postal_code = destination.postal_code
                 shipment.telephone   = destination.telephone

                 shipment.save()

                 history = ShipmentEditHistory()
                 history.user = request.user
                 history.status = "Handling and Delivery Options Changed"
                 history.shipment = shipment
                 history.save()

            alert = "Booking %s Handling and Delivery Option successfully changed" %shipment.tracking_number
            messages.success(request, alert)

            # #Update the cost calc for the shipment
            ShipmentCostCalc(request, shipment, shipment.country)

            #calling the shipment back to get it's current state
            shipment = Shipment.objects.get(pk = shipment_id)
            packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)
            #unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)

            response_dict.update({'shipment': shipment, 'packages': packages})
            return render(request, 'zaposta_snippet/edit_shipment.html', response_dict)
                          #{'shipment': shipment, 'packages': packages})


               # #Update the cost calc for the shipment
               # ShipmentCostCalc(request, shipment, shipment.country)
               #
               # alert = "Booking %s Handling and Delivery Option successfully changed" %shipment.tracking_number
               # messages.success(request, alert)
               #
               # return redirect (request.META.get('HTTP_REFERER', '/'))


    else:
          #user = request.user
          if mm.storefront_name == "volkmannexpress":
            template_name = "volkmann/accountpage.html"
          #shipments = Shipment.objects.prefetch_related('shipmentpackage_set').filter(user = request.user, cancelled = False)
          shipments = ShippingPackage.objects.filter(user = request.user, deleted=False)
          shipments_processed = shipments.filter(status="Prepared for shipping").count()
          shipments_unprocessed = shipments.filter(status="New").count()
          shipments_total = shipments.count()
          context_dict.update({'packages': packages,'count_items':count_items,'shipments':shipments,
            'shipments_un':shipments_unprocessed, 'shipments_p':shipments_processed,'shipments_t':shipments_total})
          return render_to_response(template_name,
                                   context_dict,#, 'user_details': user_details, 'status3': status3,
                                    #'user_credit_amount_N': user_credit_amount_N},
                                   context_instance=RequestContext(request))


@login_required
@csrf_exempt
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/admin/my-account/')
def my_orders(request):
    template_name = 'zaposta_snippet/edit_order.html'

    if request.method == "GET":
        orders = Order.objects.prefetch_related('orderpackage_set').filter(Q(user = request.user), ~Q(status = "cancelled")).distinct().order_by('-updated_on')

    if request.method == 'POST':
        if not request.session.has_key('fedExLocs'):
            fedExLocs = FedExLocation.objects.all()
            request.session['fedExLocs'] = fedExLocs

        if not request.session.has_key('addresses'):
            addresses = AddressBook.objects.filter(user = request.user)
            request.session['addresses'] = addresses

         #print "fedExLocs: ",fedExLocs
         #print "fedExLocs: ",request.session["fedExLocs"]
        fedExLocs = request.session['fedExLocs']
        addresses = request.session['addresses']

        form_vars = ['edit_address', 'add_address']
        response_dict = {'fedExLocs': fedExLocs, 'addresses': addresses, 'form_vars': form_vars}

        rp = request.POST
        #print rp
        if 'edit_shipment' in rp:
            order_id = rp['id']
            order = get_object_or_404(Order, pk=order_id)
            #packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)
            packages = OrderPackage.objects.prefetch_related('orderproduct_set').filter(order = order,
                                                                                           approved = True, deleted = False)
            #unlinked_items    = OrderProduct.objects.filter(order = order, package=None, deleted =False)
            response_dict.update({'order': order, 'packages': packages})
            return render(request, template_name,
                          response_dict)

        if 'collapse_shipment' in rp:
            order = get_object_or_404(Order, pk = rp['obj_id'])
            response_dict.update({'order': order})
            return render(request, 'zaposta_snippet/collapse_order.html',
                            response_dict)

         # if 'filter_objs' in rp:
         #    print rp
         #    user = request.user
         #    select_type = rp['select_type']
         #    select_val = rp['select_val']
         #    filter_dict = {select_type: select_val, 'user': user}
         #    print filter_dict
         #    #orders = Order.objects.prefetch_related('orderpackage_set').filter(user = user).distinct()
         #    orders = Order.objects.prefetch_related('orderpackage_set').filter(**filter_dict).distinct()
         #    #objs_tracking_numbers = list(map(str, orders.values_list('tracking_number', flat=True)))
         #    #print orders_tracking_numbers
         #    return render(request, 'user_account/user_orders.html', {'orders': orders})


         #if 'shipment_id' in request.POST:
        if 'edit_address' in rp.values() or 'add_address' in rp.values():
            try:
                order_id = rp['shipment_id']

                if 'edit_address' in rp.values():
                    order_address = get_object_or_404(OrderDeliveryAddress, order__id = order_id)
                    order_address.street    = rp.get('street', '')
                    order_address.town_area    = rp.get('town_area', '')

                    history_status = "Package Destination Edited"
                else:
                    order_address = AddressBook()
                    order_address.user = request.user
                    order_address.address    = "%s %s" %(rp.get('street', ''), rp.get('town_area', ''))
                    #order_address.town_area    = rp.get('town_area', '')

                    history_status = "New Package Destination Added"

                order_address.full_name  = rp.get('full_name', '')

                order_address.city       = rp.get('city', '')
                order_address.state      = rp.get('state', '')
                order_address.country    = rp.get('country', '')
                order_address.telephone  = rp.get('telephone', '')
                #tracking_number = shipment.tracking_number
                order_address.save()

                order = get_object_or_404(Order, pk=order_id)
                history = OrderHistory()
                history.user = request.user
                history.status = history_status
                history.order = order
                history.save()

                addresses = AddressBook.objects.filter(user = request.user)
                request.session['addresses'] = addresses

                if 'edit_address' in rp.values():
                    #order = Order.objects.get(pk = order_id)
                    packages = OrderPackage.objects.prefetch_related('orderproduct_set').filter(order = order,
                                                                                                   approved = True, deleted = False)
                    #unlinked_items    = OrderProduct.objects.filter(order=order, package=None, deleted =False)
                    response_dict.update({'order': order, 'packages': packages})
                    return render(request, template_name,
                                  response_dict)
                else:
                    new_address_div = '<div class="col-md-12 item adds select" style="margin-top:15px;" address-id="'+str(order_address.id)+'"><p><strong>'+order_address.full_name+'</strong>'+order_address.delivery_address()+'</p></div>'
                    return JsonResponse({'result': 'success', 'new_address_div': new_address_div})
            except:
                return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})

              # shipments = Shipment.objects.filter(user=request.user)
              # #user_details = request.user.get_profile
              # user_details = get_object_or_404(UserAccount, user = request.user)
              # status3 = PackageStatusSettings.objects.get(pk = 1).status3
              #
              # alert = 'Delivery Address for booking ' + tracking_number + ' successfully updated'
              # messages.success(request, alert)
              # return redirect (request.META['HTTP_REFERER'])

              #return render_to_response("client/track-shipment.html",
              #                         {'alert': alert, 'shipments': shipments, 'user_details': user_details, 'status3': status3},
              #                         context_instance=RequestContext(request))

        if 'edit_item' in rp.values():
            try:
                item_id = rp['item_id']
                item = OrderProduct.objects.get(pk = item_id)
                #print item

                exchange_rate = country_exchange_rate(item.country, item.order.costcalc_instance)

                description = rp.get('description', '')
                #item.courier_tracking_number  = rp.get('courier_tracking_number', '')
                item.description            = description#rp.get('description', '')
                item.quantity               = rp.get('quantity', '')
                item.link                   = rp.get('link', '')
                item.listed_price_D              = rp.get('listed_price_D', '')
                item.size                   = rp.get('size', '')
                item.colour                 = rp.get('colour', '')
                #if total_value != '':
                 # item.total_value_N = float(total_value) * exchange_rate #dollarNairaRate
                item.save()

                history = OrderHistory()
                history.user = request.user
                history.status = "Edited"
                history.order = item.order
                history.item = item
                history.save()

                order = item.order
                #tracking_number =  shipment.tracking_number #item.shipment.tracking_number

                #shipments = Shipment.objects.filter(user=request.user)
                #user_details = request.user.get_profile
                #user_details = get_object_or_404(UserAccount, user = request.user)
                #status3 = PackageStatusSettings.objects.get(pk = 1).status3
                alert = '%s successfully updated' %description
                messages.success(request, alert)

                #shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
                packages = OrderPackage.objects.prefetch_related('orderproduct_set').filter(order = order,
                                                                                               approved = True, deleted = False)
                #unlinked_items    = OrderProduct.objects.filter(order=order, package=None, deleted =False)
                response_dict.update({'order': order, 'packages': packages})
                return render(request, template_name,
                              response_dict)

                  # packages = shipment.shipmentpackage_set.filter(approved = True, deleted = False)
                  # unlinked_items    = ShipmentItem.objects.filter(shipment=shipment, package=None, deleted =False)
                  # return render(request, template_name,
                  #               {'shipment': shipment, 'packages': packages, 'unlinked_items': unlinked_items})
            except:
                return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields except for size and color (optional)'})


        if 'delete_item' in rp:

            product                = OrderProduct.objects.get(pk = rp['item_id'])
            description         = product.description


            product.deleted = True
            product.save()

            order = Order.objects.get(pk = rp['shipment'])

            ##create product edit history
            status_update = "deleted"
            order_history(request, status_update, product, None, order)

            #return JsonResponse({'result': 'ok'})

            alert = '%s successfully deleted' %description
            messages.success(request, alert)


            packages = OrderPackage.objects.prefetch_related('orderproduct_set').filter(order = order,
                                                                                           approved = True, deleted = False)
            #unlinked_items    = OrderProduct.objects.filter(order=order, package=None, deleted =False)
            response_dict.update({'order': order, 'packages': packages})
            return render(request, template_name,
                          response_dict)

              # shipments = Shipment.objects.filter(user=request.user)
              # #user_details = request.user.get_profile
              # user_details = get_object_or_404(UserAccount, user = request.user)
              # status3 = PackageStatusSettings.objects.get(pk = 1).status3
              # alert = description + ' in booking ' + tracking_number + ' successfully deleted'
              #
              # #check if all items but one have been received and the given item has not been received
              # #if ifAllItemsReceivedButOne(item):
              # #     pass
              # #
              # messages.success(request, alert)
              # return redirect (request.META.get('HTTP_REFERER', '/'))


        if 'add_item' in rp.values():
            try:
                order_id = rp['shipment']
                order = Order.objects.get(pk = order_id)

                exchange_rate = country_exchange_rate(order.country, order.costcalc_instance)

                item = OrderProduct()
                item.user = request.user
                item.order = order


                description = rp.get('description', '')
                #item.courier_tracking_number  = rp.get('courier_tracking_number', '')
                item.description          = description#rp.get('description', '')
                item.quantity             = rp.get('quantity', '')
                item.listed_price_D       = rp.get('listed_price_D', '')
                item.size                 = rp.get('size', '')
                item.colour                = rp.get('colour', '')
                item.save()

                history = OrderHistory()
                history.user = request.user
                history.status = "Added"
                history.order = order
                history.item = item
                history.save()

                alert = '%s successfully added' %description#rp['description']
                messages.success(request, alert)

                order = Order.objects.get(pk = order_id)
                packages = OrderPackage.objects.prefetch_related('orderproduct_set').filter(order = order,
                                                                                               approved = True, deleted = False)
                #unlinked_items    = OrderProduct.objects.filter(order=order, package=None, deleted =False)
                response_dict.update({'order': order, 'packages': packages})
                return render(request, template_name,
                              response_dict)
            except:
                return JsonResponse({'result': 'fail', 'alert': 'Please complete all form fields'})



        if 'send_invoice' in rp:
            id = request.POST['shipment']
            s = Shipment.objects.get(pk = id)
            user = s.user

            alert = 'Invoice Successfully sent to your E-mail address'
            shipments = Shipment.objects.filter(user=request.user)
            #user_details = request.user.get_profile
            user_details = get_object_or_404(UserAccount, user = request.user)
            status3 = PackageStatusSettings.objects.get(pk = 1).status3

            send_confirmation_mail(user, s)
            #return render_to_response("client/track-shipment.html",
            #                         {'alert': alert, 'shipments': shipments, 'user_details': user_details, 'status3': status3},
            #                         context_instance=RequestContext(request))
            return redirect (request.META.get('HTTP_REFERER', '/'))

        if 'view_handling_options' in rp:
            id = request.POST['shipment']
            shipment = Shipment.objects.get(pk = id)

            return render_to_response('tags/edit_handling_options.html',
                                      {'shipment': shipment}, context_instance=RequestContext(request))

        if 'edit_handling' in rp.values():
            order_id = request.POST['shipment']
            order = Order.objects.get(pk = order_id)

            if order.status == "new":

                if request.POST.has_key('insure'):
                     order.insure = True
                else:
                     order.insure = False

                if request.POST.has_key('consolidate'):
                     order.consolidate = True
                else:
                     order.consolidate = False

                if request.POST.has_key('strip'):
                     order.strip_my_package = True
                else:
                     order.strip_my_package = False

                # if request.POST.has_key('dm'):
                #      dm = request.POST['dm']
                #      update_delivery_option(dm, order)
                int_freight = request.POST["int_freight"]
                dm_freight = request.POST["dm_freight"]

                dm = "%s-%s"  %(int_freight, dm_freight)

                #print "dm: ",dm
                #if request.POST.has_key('dm'):
                #     dm = request.POST['dm']
                update_delivery_option(dm, order)

                dvm = "%s - %s" %(int_freight, dm_freight)
                dvm = dvm.upper()

                order.shipping_method = dvm

                delivery_city = request.POST["hidden_dm_location"]
                if delivery_city != '':
                    address_id = selected_delivery_address_id(request.user, dvm, delivery_city)
                else:
                    address_id = request.POST["address_book"]

                destination = AddressBook.objects.get(pk = address_id)

                order_address = get_object_or_404(OrderDeliveryAddress, order__id = order_id)

                order_address.full_name     = "%s %s" %(destination.first_name, destination.last_name)
                order_address.street        = destination.address
                #order_address.town_area     = rp.get('town_area', '')
                order_address.city          = destination.city
                order_address.state         = destination.state
                order_address.telephone     = destination.telephone
                #tracking_number = shipment.tracking_number
                order_address.save()



                # #Update the cost calc for the shipment
                orderproducts = order.orderproduct_set.filter(deleted = False)
                OrderCostCalc(request, order.total_weight, orderproducts, order)
                order.save()

                history = OrderHistory()
                history.user = request.user
                history.status = "Handling and Delivery Options Changed"
                history.order = order
                history.save()

                alert = "Booking %s Handling and Delivery Option successfully changed" %order.tracking_number
                messages.success(request, alert)



            #calling the shipment back to get it's current state
            order = Order.objects.get(pk = order_id)
            packages = OrderPackage.objects.prefetch_related('orderproduct_set').filter(order = order,
                                                                                           approved = True, deleted = False)
            #unlinked_items    = OrderProduct.objects.filter(order=order, package=None, deleted =False)
            response_dict.update({'order': order, 'packages': packages})
            return render(request, template_name,
                          response_dict)


              # #Update the cost calc for the shipment
              # ShipmentCostCalc(request, shipment, shipment.country)
              #
              # alert = "Booking %s Handling and Delivery Option successfully changed" %shipment.tracking_number
              # messages.success(request, alert)
              #
              # return redirect (request.META.get('HTTP_REFERER', '/'))


    else:
         #user = request.user
         #orders = Order.objects.prefetch_related('orderpackage_set').filter(Q(user = user), ~Q(status = "cancelled")).distinct().order_by('-updated_on')
         #objs_tracking_numbers = list(map(str, orders.values_list('tracking_number', flat=True)))
         #print orders_tracking_numbers
         return render(request, 'user_account/user_orders.html', {'orders': orders})
                                                                  #'objs_tracking_numbers': objs_tracking_numbers})


@login_required
def my_soko_pay_info(request):
    origin, destination = get_route_chains(request)
    user = request.user
    useraccount = UserAccount.objects.get(user=user)
    country = useraccount.country
    #credit_purchases = SokoPay.objects.filter(user = user)
    card_payments = MarketerPayment.objects.card_payments(useraccount)

    soko_pay_log = MarketerPayment.objects.sokopay_payments(useraccount)

    bank_deposits = MarketerPayment.objects.bank_payments(useraccount)

    try:
        mm = marketing_member(request)
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    #template_name = "shopping_client/jeje-pay.html"
    template_name = "user_account/user_soko_pay.html"
    return render_to_response(template_name, {'card_payments': card_payments, 'soko_pay_log': soko_pay_log, 'country': country,'count':count_items,
                                             'bank_deposits': bank_deposits, 'origin_countries':origin, 'destination_countries':destination},
                              context_instance = RequestContext(request))


@login_required(login_url='/volk/login/')
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(address_activated_new, login_url='/redirect_to_address_activation_new/', redirect_field_name=None )
def my_soko_pay_info_volk(request):
    origin, destination = get_route_chains(request)
    user = request.user
    useraccount = UserAccount.objects.get(user=user)
    country = useraccount.country
    #credit_purchases = SokoPay.objects.filter(user = user)
    card_payments = MarketerPayment.objects.card_payments(useraccount)

    soko_pay_log = MarketerPayment.objects.sokopay_payments(useraccount)

    bank_deposits = MarketerPayment.objects.bank_payments(useraccount)

    bank_approved_payments = bank_deposits.filter(status="Approved").count()
    bank_declined_payments = bank_deposits.filter(status="declined").count()
    bank_pending_payments = bank_deposits.filter(status="pending").count()


    try:
        mm = marketing_member(request)
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    #template_name = "shopping_client/jeje-pay.html"
    template_name = "volkmann/payment.html"
    return render_to_response(template_name, {'card_payments': card_payments, 'soko_pay_log': soko_pay_log, 'country': country,'count':count_items,
                                             'bank_deposits': bank_deposits, 'origin_countries':origin,
                                              'destination_countries':destination, 'bank_a':bank_approved_payments,
                                               'bank_d':bank_declined_payments, 'bank_p':bank_pending_payments},
                              context_instance = RequestContext(request))


@login_required
@csrf_exempt
@user_passes_test(flagged_check, login_url='/bank-deposit-verification/', redirect_field_name = None)
def my_messages(request):

    origin, destination = get_route_chains(request)
    form = ComposeMessageForm()
    shipment_type = str(request.POST.get("booking_ref"))
    message_ids = str(request.POST.get("message_ids")).split(",")
    booking_ref = str(request.POST.get("booking_ref"))
    print "booking_ref:",booking_ref

    try:
        mm = marketing_member(request)
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0


    #export_packages = ExportPackage.objects.filter(Q(user = request.user), Q(deleted = False))
    #import_packages = ShippingPackage.objects.filter(Q(user = request.user), Q(deleted = False))

    packages = ShippingPackage.objects.filter(Q(user = request.user), Q(deleted = False))

    #packages = list(reversed(sorted(chain(import_packages, export_packages), key=lambda instance: instance.created_on)))
    # packages = paginate_list(sorted_packages, 2)
    # print "packages:",packages

    if request.method == "POST":

        if 'compose_msg' in request.POST:
            form = ComposeMessageForm(request.POST)
            if form.is_valid():
                form.save()
                message = form.save(commit=False)
                message.user = request.user
                message.full_name = request.user.get_full_name()
                message.last_name = request.user.last_name#request.user.get_profile().last_name
                message.email = request.user.email
                # shipment = Shipment.objects.get(tracking_number = form.cleaned_data['booking_ref'])
                try:
                    #if booking_ref[0] == "I":
                    shipment = ShippingPackage.objects.get(tracking_number = form.cleaned_data['booking_ref'])
                    # else:
                    #     shipment = ExportPackage.objects.get(tracking_number = form.cleaned_data['booking_ref'])
                    #     message.shipment = shipment
                except Exception as e:
                    print 'my_messages e: ',e
                message.save()
                shipment.message_received = True
                shipment.save()

                comment             = MessageCenterComment()#Comment()
                comment.message     = message.message
                comment.message_obj = message
                comment.user        = request.user
                comment.last_name   = request.user.last_name
                comment.full_name   = request.user.get_full_name()
                comment.save()

                messages.info(request, "Message successfully sent")
                return redirect (request.META.get('HTTP_REFERER', '/'))

        if 'view_comment_msgs' in request.POST:
            message = MessageCenter.objects.get(pk = request.POST['message_id'])
            return render(request, 'zaposta_snippet/view_msg_comments.html',
                            {'message': message})

        if 'add_comment_to_message' in request.POST:
            message_content = request.POST['message_body']
            if message_content == "":
                return JsonResponse({'result': 'fail', 'alert_msg': 'Please add a comment before clicking the submit button'})
            else:
                message_id = request.POST['message_id']
                message = MessageCenter.objects.get(pk = message_id)
                print "the message:",message

                comment             = MessageCenterComment()#Comment()
                comment.message     = message_content
                comment.message_obj = message
                comment.user        = request.user
                comment.last_name   = request.user.last_name
                comment.full_name   = request.user.get_full_name()
                comment.save()

                message.new     = True
                message.replied = False
                message.replied_on = timezone.now() #present_time()
                message.save()

                if message:
                     shipment_id = booking_ref
                     # shipment = Shipment.objects.get( pk = shipment_id)
                     # if booking_ref[0] == "I":
                     shipment = ShippingPackage.objects.get(tracking_number = shipment_id)
                     # else:
                     #    shipment = ExportPackage.objects.get(tracking_number = shipment_id)
                     shipment.message_received = True
                     shipment.save()

                message = MessageCenter.objects.get(pk = message_id)
                return render(request, 'zaposta_snippet/view_msg_comments.html',
                                {'message': message})

        if "archive" in request.POST:
            if message_ids > 1:
                for messages_id in message_ids:
                    MessageCenter.objects.filter(id=messages_id,user=request.user).update(new=False,archive=True)
                    return redirect (request.META.get('HTTP_REFERER', '/'))

            else:
                MessageCenter.objects.filter(id=messages_id).update(new=False,archive=True)
                return redirect (request.META.get('HTTP_REFERER', '/'))


        if "delete" in request.POST:
            if message_ids > 1:
                for messages_id in message_ids:
                    message = MessageCenter.objects.filter(id=messages_id,user=request.user)
                    message.delete()
                    return redirect (request.META.get('HTTP_REFERER', '/'))

            else:
                message = MessageCenter.objects.filter(id=messages_id,user=request.user)
                message.delete()
                return redirect (request.META.get('HTTP_REFERER', '/'))

    else:
        #shipments = Shipment.objects.filter(user = request.user, cancelled = False, completed
        shipments = packages
        all_messages = MessageCenter.objects.filter(user = request.user).order_by('-replied_on')
        new_messages = all_messages.filter(new = True)
        replied_messages = all_messages.filter(replied = True)
        archive_messages = all_messages.filter(archive = True)
        #messages = MessageCenter.objects.filter(user = request.user, new = True).order_by('-replied_on')

        return render(request, "user_account/user_messages.html",
                                   {'form': form,
                                    'new_messages': new_messages, 'replied_messages': replied_messages,
                                    'archive_messages': archive_messages,'count':count_items,
                                    'shipments': shipments,'origin_countries':origin, 'destination_countries':destination})


@login_required(login_url='/volk/login/')
@csrf_exempt
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(address_activated_new, login_url='/redirect_to_address_activation_new/', redirect_field_name=None)
@user_passes_test(flagged_check, login_url='/bank-deposit-verification/', redirect_field_name = None)
def my_messages_volk(request):

    origin, destination = get_route_chains(request)
    form = ComposeMessageForm()
    shipment_type = str(request.POST.get("booking_ref"))
    message_ids = str(request.POST.get("message_ids")).split(",")
    booking_ref = str(request.POST.get("booking_ref"))
    print "booking_ref:",booking_ref

    try:
        mm = marketing_member(request)
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0


    #export_packages = ExportPackage.objects.filter(Q(user = request.user), Q(deleted = False))
    #import_packages = ShippingPackage.objects.filter(Q(user = request.user), Q(deleted = False))

    packages = ShippingPackage.objects.filter(Q(user = request.user), Q(deleted = False))

    #packages = list(reversed(sorted(chain(import_packages, export_packages), key=lambda instance: instance.created_on)))
    # packages = paginate_list(sorted_packages, 2)
    # print "packages:",packages

    if request.method == "POST":

        if 'compose_msg' in request.POST:
            form = ComposeMessageForm(request.POST)
            if form.is_valid():
                form.save()
                message = form.save(commit=False)
                message.user = request.user
                message.full_name = request.user.get_full_name()
                message.last_name = request.user.last_name#request.user.get_profile().last_name
                message.email = request.user.email
                # shipment = Shipment.objects.get(tracking_number = form.cleaned_data['booking_ref'])
                try:
                    #if booking_ref[0] == "I":
                    shipment = ShippingPackage.objects.get(tracking_number = form.cleaned_data['booking_ref'])
                    # else:
                    #     shipment = ExportPackage.objects.get(tracking_number = form.cleaned_data['booking_ref'])
                    #     message.shipment = shipment
                except Exception as e:
                    print 'my_messages e: ',e
                message.save()
                shipment.message_received = True
                shipment.save()

                comment             = MessageCenterComment()#Comment()
                comment.message     = message.message
                comment.message_obj = message
                comment.user        = request.user
                comment.last_name   = request.user.last_name
                comment.full_name   = request.user.get_full_name()
                comment.save()

                messages.info(request, "Message successfully sent")
                return redirect (request.META.get('HTTP_REFERER', '/'))

        if 'view_comment_msgs' in request.POST:
            message = MessageCenter.objects.get(pk = request.POST['message_id'])
            return render(request, 'zaposta_snippet/view_msg_comments.html',
                            {'message': message})

        if 'add_comment_to_message' in request.POST:
            message_content = request.POST['message_body']
            if message_content == "":
                return JsonResponse({'result': 'fail', 'alert_msg': 'Please add a comment before clicking the submit button'})
            else:
                message_id = request.POST['message_id']
                message = MessageCenter.objects.get(pk = message_id)
                print "the message:",message

                comment             = MessageCenterComment()#Comment()
                comment.message     = message_content
                comment.message_obj = message
                comment.user        = request.user
                comment.last_name   = request.user.last_name
                comment.full_name   = request.user.get_full_name()
                comment.save()

                message.new     = True
                message.replied = False
                message.replied_on = timezone.now() #present_time()
                message.save()

                if message:
                     shipment_id = booking_ref
                     # shipment = Shipment.objects.get( pk = shipment_id)
                     # if booking_ref[0] == "I":
                     shipment = ShippingPackage.objects.get(tracking_number = shipment_id)
                     # else:
                     #    shipment = ExportPackage.objects.get(tracking_number = shipment_id)
                     shipment.message_received = True
                     shipment.save()

                message = MessageCenter.objects.get(pk = message_id)
                return render(request, 'zaposta_snippet/view_msg_comments.html',
                                {'message': message})

        if "archive" in request.POST:
            if message_ids > 1:
                for messages_id in message_ids:
                    MessageCenter.objects.filter(id=messages_id,user=request.user).update(new=False,archive=True)
                    return redirect (request.META.get('HTTP_REFERER', '/'))

            else:
                MessageCenter.objects.filter(id=messages_id).update(new=False,archive=True)
                return redirect (request.META.get('HTTP_REFERER', '/'))


        if "delete" in request.POST:
            if message_ids > 1:
                for messages_id in message_ids:
                    message = MessageCenter.objects.filter(id=messages_id,user=request.user)
                    message.delete()
                    return redirect (request.META.get('HTTP_REFERER', '/'))

            else:
                message = MessageCenter.objects.filter(id=messages_id,user=request.user)
                message.delete()
                return redirect (request.META.get('HTTP_REFERER', '/'))

    else:
        #shipments = Shipment.objects.filter(user = request.user, cancelled = False, completed
        shipments = packages
        all_messages = MessageCenter.objects.filter(user = request.user).order_by('-replied_on')
        new_messages = all_messages.filter(new = True)
        replied_messages = all_messages.filter(replied = True)
        archive_messages = all_messages.filter(archive = True)
        #messages = MessageCenter.objects.filter(user = request.user, new = True).order_by('-replied_on')

        return render(request, "user_account/user_messages.html",
                                   {'form': form,
                                    'new_messages': new_messages, 'replied_messages': replied_messages,
                                    'archive_messages': archive_messages,'count':count_items,
                                    'shipments': shipments,'origin_countries':origin, 'destination_countries':destination})
'''USER ACCOUNT FUNCTIONS'''

def fun_cancel_shipment(request, shipment):
     if not shipment.active and not shipment.completed:
          user = shipment.user

          #refund customer
          if shipment.credit_balance_paid_N > 0 or shipment.shipping_credit_applied_N > 0:
               balance_paid_N = shipment.shipping_credit_applied_N + shipment.credit_balance_paid_N
               create_jejepay_record(request.user, balance_paid_N, creditpurchase_ref(request, shipment.id), shipment)

          #if shipment.shipping_credit_applied_D is not None:
          #    shipment_applied_credit = shipment.shipping_credit_applied_D
          #else:
          #    shipment_applied_credit = 0
          #if shipment.credit_balance_D is not None:
          #    shipment_credit_balance = shipment.credit_balance_D
          #else:
          #    shipment_credit_balance = 0
          #shipment_credit_balance_paid = shipment.credit_balance_paid_D
          #accountToUpdate = UserAccount.objects.get(user = user)
          #prev_user_shipping_credit = accountToUpdate.credit_amount
          #return shipping credit applied to shipment to user's account
          #new_user_shipping_credit = prev_user_shipping_credit + shipment_credit_balance + shipment_applied_credit + shipment_credit_balance_paid
          #accountToUpdate.credit_amount = new_user_shipping_credit
          #accountToUpdate.save()
          #reset shipment's credit applied and credit balance details to zero
          shipment.shipping_credit_applied_D = 0
          shipment.shipping_credit_applied_N = 0
          shipment.credit_balance_D = 0
          shipment.credit_balance_N = 0
          shipment.credit_balance_paid_D = 0
          shipment.credit_balance_paid_N = 0


          #shipment.updated_on = present_time()

          shipment.save()
          #shipmentedithistory3(request, shipment)

          messages.info(request, "Shipment %s has been successfully cancelled" %shipment.tracking_number)

     else:
          messages.info(request, "Sorry! You can only cancel a booking that has not started processing.")

def cancel_shipment(request, id):
     shipment = get_object_or_404(Export, pk=id)

     fun_cancel_shipment(request, shipment)

     return redirect(reverse("general:my_shipments"))

def encrypt_bank_accounts(request):
    shipments = Shipment.active_shipments.filter(credit_balance_D__lte = 5)
    for shipment in shipments:
        if isShipmentCompleted(shipment):
            shipment.active = False
            shipment.completed = True
            shipment.save()
    return HttpResponse("Success")


def random_code(length):
    pass

def get_local_distributor_locations(request):
    rg = request.GET
    locations  =  get_office_pickup_locations(request, "shipping", rg['service_type'], rg['origin'], rg['destination'], rg['destination'])
    return render(request, 'zaposta_snippet/office_pickup_locations.html', {'locations':locations})


def get_estimate_pkgs(request):
    estimate_packages = []
    if request.user.is_authenticated():
        estimate_packages = ShippingPackage.objects.filter(is_estimate = True,  user = request.user)  #fix for anonymous user
    else:
        estimate_packages = ShippingPackage.objects.filter(is_estimate = True,  tracking_number = request.session.get('annonymous_user', "")) # attempt fetching packages
    return estimate_packages



def quickEstimate(request):
    # if request.GET.has_key('action') and request.GET['action'] == 'fetch_states':
    #     rg = request.GET
    #     locations  =  get_office_pickup_locations(request, "shipping", rg['service_type'], rg['origin'], rg['destination'], rg['destination'])
    #     return render(request, 'zaposta_snippet/office_pickup_locations.html', {'locations':locations})
    print 'rp:', request.POST
    total_weight   = 0.0
    local_rates    = 0.0
    total_estimate = 0.0
    context = {}
    tracking_code = None
    estimate_packages = get_estimate_pkgs(request)
    total_weight = estimate_packages.aggregate(total_weight = Sum('box_weight_Actual'))['total_weight']
    countries_list,countries_origin,countries_destination = get_route_countries(request)
    print countries_origin
    print countries_destination
    marketer = marketing_member(request)  # delete this after confirmation
    # costcalc = marketingmember_costcalc(request,)
    # lb_kg_factor   =  costcalc.lb_kg_factor
    # exchange_rate  =  costcalc.dollar_exchange_rate
    # weightFactor   =  costcalc.dim_weight_factor
    template_name  =  "general_client/quick-estimate.html"
    dimension_form = AddCustomPackageForm()
    if request.GET.has_key('q') and request.GET['q'] == "clear_all":
        # try:
        if not request.user.is_authenticated():
            ShippingPackage.objects.filter(is_estimate = True, tracking_number = request.session.get('annonymous_user', "")).delete()
        else:
        # except:
            ShippingPackage.objects.filter(is_estimate = True, user = request.user).delete()
        return redirect('/quick-estimate')

    if request.GET.has_key('delete_pkg'):
        try:
            ShippingPackage.objects.filter(pk = request.GET['delete_pkg']).delete()
        except:
            ShippingPackage.objects.filter(pk = request.GET['delete_pkg']).delete()
        return redirect('/quick-estimate')
    # delete entries
    if request.method == "POST":
        rp = request.POST
        service_type = rp['estimate_type']
        weight_unit  = rp['weight_unit']
        form2 = AddCustomPackageForm(request.POST)
        if form2.is_valid():
             added_box = form2.save(commit=False)
             if request.user.is_authenticated():
                  added_box.user      = request.user
             quantity = 1
             dim_weight = quantity * (float(form2.cleaned_data['box_length']) * float(form2.cleaned_data['box_width']) * float(form2.cleaned_data['box_height'])/ weightFactor)
             entered_weight  = float(form2.cleaned_data['box_weight_Actual'])

             added_box.box_weight_Dim = dim_weight #* quantity
             added_box.box_weight_Dim_K = dim_weight * lb_kg_factor # * quantity

             if weight_unit == "lbs":
                  added_box.box_weight_Actual = entered_weight * quantity
                  # request.session['actual_box_weight'] =
                  added_box.box_weight_Actual_K = entered_weight * lb_kg_factor * quantity
             else:
                  added_box.box_weight_Actual = entered_weight * 2.20462 * quantity
                  added_box.box_weight_Actual_K = entered_weight * quantity
             added_box.is_estimate         =   True
             estimate_packages = get_estimate_pkgs(request)
             if not request.user.is_authenticated() and estimate_packages.count() == 0: # assign random code to annonymous user
                tracking_code = code = get_random_code(45)
                request.session['annonymous_user'] = tracking_code
             if request.session.get('annonymous_user', None) != None:
                # print "annonymous user ", request.session['annonymous_user']
                added_box.tracking_number = request.session['annonymous_user']
             added_box.save()
             #  try to refetch packages
             estimate_packages = get_estimate_pkgs(request)

             total_weight = estimate_packages.aggregate(total_weight = Sum('box_weight_Actual'))['total_weight']
             # print "total weight ", total_weight

             # print "box weight actual ", added_box.box_weight_Actual
             intl_rate = marketer.get_route_delivery_method_range_rate("shipping", service_type, rp['country_from'], rp['country_to'], rp['shipping_method'], added_box.box_weight_Actual) # fix maximum weight limit exceeded
             # print "international rate", intl_rate
             if service_type == "export":
                # print "box weight actual ", added_box.box_weight_Actual
                # if float(added_box.box_weight_Actual) > 70.0:
                # # if float(total_weight) > 70.0:
                #     # print "greater than 70"
                #     ShippingPackage.objects.filter(pk = added_box.pk).delete()
                #     messages.info(request, "You cannot export more than 70lbs in a single package. Try a lesser value.")
                #     return redirect('/quick-estimate')

                # print "connecting usps . . ."
                # usps_shipping_charge = usps_estimate(request, added_box.box_weight_Actual)
                dollar_local_rate, naira_local_rate =   get_local_freight_from_state(request, float(total_weight), rp['state'], rp['country_to']) # pick up charge from dropoff location to warehouse
                weight_estimate_D =  float(total_weight) * float(intl_rate)
                # print "total weight of item", total_weight
                total_estimate_D  =  weight_estimate_D + float(dollar_local_rate) # + float(usps_shipping_charge)
                request.session['total_D']  =  total_estimate_D
                weight_estimate_N  =  float(intl_rate) * float(exchange_rate) * float(total_weight)
                # total_estimate_N = weight_estimate_N + float(usps_shipping_charge * exchange_rate)
                total_estimate_N = weight_estimate_N + float(naira_local_rate)
                request.session['total_N']  =  total_estimate_N
             else:
                try:
                    dollar_local_rate, naira_local_rate =   get_local_freight_from_state(request, float(total_weight), rp['state'], rp['country_to'])
                except Exception as e:
                    messages.info(request, "Ooops! could not fetch estimate at this time. Please reload the page and try again")
                    return redirect('/quick-estimate')
                # print "dollar naira rate", dollar_local_rate, naira_local_rate
                weight_estimate_D =  float(total_weight) * float(intl_rate)
                total_estimate_D  =  weight_estimate_D + float(dollar_local_rate)
                request.session['total_D']  =  total_estimate_D

                weight_estimate_N  =  float(intl_rate) * float(exchange_rate) * float(total_weight)
                total_estimate_N = weight_estimate_N + float(naira_local_rate)
                request.session['total_N']  =  total_estimate_N

             context.update({'dim_form': dimension_form,'origin_countries':origin,'destination_countries':destination,'states':STATE, 'packages':estimate_packages,
              'total_weight':total_weight, 'total_estimate_N':request.session.get('total_N',0.0), 'total_estimate_D':request.session.get('total_D', 0.0)})
             return render(request, template_name, context)

    context.update({'dim_form': dimension_form,'packages':estimate_packages,'countries_list': countries_list, 'countries_origin':countries_origin, 'countries_destination':countries_destination,
     'total_weight':total_weight, 'rate_per_lb':local_rates, 'states':STATE, 'total_estimate_N':request.session.get('total_N', 0.0), 'total_estimate_D':request.session.get('total_D', 0.0)})
    return render(request, template_name, context)



# -------------------------------------------------------------------
#  TEST LABEL PRINTING

def process_error_response(request, xml_response):
    root = ET.fromstring(xml_response)
    try:
        error_msg = root.findall(".//Error/Description")[0].text
    except Exception as e:
        error_msg = 'Oops! Something went wrong. Please try again'
    print 'error_msg: ',error_msg
    return JsonResponse({'error_msg': error_msg})



def extract_image_string(xml_response):
    root = ET.fromstring(xml_response)
    img_str = root.findall(".//SignatureConfirmationLabel")[0].text
    return img_str



def test_label_printing(request):
    xml = '''https://secure.shippingapis.com/ShippingAPI.dll?API=SignatureConfirmationV4&XML=<?xml version="1.0" encoding="UTF-8" ?>
    <SignatureConfirmationV4.0Request USERID="250CIRCU3854">
      <Option>1</Option>
      <ImageParameters>
        <LabelSequence>
          <PackageNumber>1</PackageNumber>
          <TotalPackages>1</TotalPackages>
        </LabelSequence>
      </ImageParameters>
      <FromName>James Ikechukwu</FromName>
      <FromFirm> </FromFirm>
      <FromAddress1>8</FromAddress1>
      <FromAddress2>Wildwood Drive</FromAddress2>
      <FromCity>Greenbelt</FromCity>
      <FromState>CT</FromState>
      <FromZip5>06371</FromZip5>
      <FromZip4></FromZip4>
      <ToName>smatpost</ToName>
      <ToFirm>Hydrant Tech</ToFirm>
      <ToAddress1>Apt. 3C</ToAddress1>
      <ToAddress2> 6406 Ivy Lane</ToAddress2>
      <ToCity>Greenbelt</ToCity>
      <ToState>MD</ToState>
      <ToZip5>20770</ToZip5>
      <ToZip4></ToZip4>
      <WeightInOunces>36.8</WeightInOunces>
      <ServiceType>PRIORITY</ServiceType>
      <InsuredAmount></InsuredAmount>
      <SeparateReceiptPage></SeparateReceiptPage>
      <POZipCode></POZipCode>
      <ImageType>PDF</ImageType>
      <LabelDate></LabelDate>
      <CustomerRefNo></CustomerRefNo>
      <AddressServiceRequested></AddressServiceRequested>
      <SenderName>James Ikechukwu</SenderName>
      <SenderEMail>jameseze.ca@gmail.com</SenderEMail>
      <RecipientName></RecipientName>
      <RecipientEMail></RecipientEMail>
      <Container>Variable</Container>
      <Size>Regular</Size>
      <CommercialPrice>True</CommercialPrice>
    </SignatureConfirmationV4.0Request>'''

    r = requests.post(xml, headers = {'Content-Type': 'application/xml'})
    img_str  = ""
    if r.status_code == 200:
        print r.content
        try:
            img_str =  extract_image_string(r.content)
        except Exception as e:
            return process_error_response(request, r.content) # attempt error processing
    image = convert_base64_to_image(img_str, str(12345678) + ".pdf")
    return HttpResponse(image, content_type = "application/pdf")



@login_required
def confirm_ebiz_payment(request):
    print "got here ebiz"
    print "session keys: ", request.session.values()

    if request.user.is_authenticated:
        ref_no = request.GET['UMrefNum']        
        status = request.GET['UMstatus']
                  
        if status == "Approved":       
            params =  urllib.urlencode({"status":status,"ref_no":ref_no})
            raw_url = '/shipping/payment/'
            url = raw_url + "?" + params
            response = (url)
            return redirect(response)        
             
    return HttpResponse("Export Coming Soon")



def confirm_paypal_payment(request):
    marketer = marketing_member(request)
    # print "got here"
    # print "session keys: ", request.session.values()

    if request.user.is_authenticated:

        if str(request.GET.get('st')) == "Completed":
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
                status="Approved",
                amount=amount,
                purchase_type_3="veiwallet",
                ref_no=tx,
                marketer=marketer,
                bank=None,
                teller_no=tx)


            all_cost = CostCalcSettings.objects.get(marketer=marketer,country="Nigeria")
            dollarNairaRate = all_cost.dollar_exchange_rate
            request.user.useraccount.credit_amount_D += (float(amount))
            request.user.useraccount.credit_amount_N += (float(dollarNairaRate) * float(amount))
            request.user.useraccount.save()
            messages.success(request,"You have sucessfully funded your VEI Wallet")
        messages.success(request,"Oops Something went wrong...Please try again")
        return redirect(reverse('wallet:wallet'))
       
    return render(request,'payment/done.html')




def marketer_addons(request,action):
    context = {}
    mm = marketing_member(request)
    template_name = mm.storefront_name + "/" + mm.storefront_name + action + "." + "html"
    # print "template_name: ",template_name
    return render(request,template_name,context)



def contact_us(request):
    context = {}
    if request.method =='POST':
        first_name = request.POST.get('first_name')
        # print "first_name ",first_name
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        msg_title = request.POST.get('msg_title')
        message = str(request.POST.get('message')).strip()
        # print "message: ",message
        name = first_name +" "+ last_name
        # print "name :",name

    else:
        print "You didn't fill all the details"

    try:
        subject = msg_title
        user = name
        email = email
        text = message
        # print "text: ",text
        # mrt_mail = mrt_mail
        subscriber_contactus_mail(request, user, subject, text, email)
    except Exception as e:
        print'error: ',e
        pass

    return redirect (request.META.get('HTTP_REFERER', '/'))



def contact_us_volk(request):
    context = {}
    if request.method =='POST':
        name = request.POST.get('name')
        # print "first_name ",first_name
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        msg_title = request.POST.get('msg_title')
        message = str(request.POST.get('description')).strip()
        # print "message: ",message
        # print "name :",name

    else:
        print "You didn't fill all the details"

    try:
        subject = "Trucking Enquiry"
        user = name
        email = email
        text = message
        phone_number = phone_number
        # print "text: ",text
        subscriber_contactus_mail(request, user, subject, text, email, phone_number)
    except Exception as e:
        print'error: ',e
        pass

    return redirect (request.META.get('HTTP_REFERER', '/'))



def product_view(request):
    context = {}
    mm = marketing_member(request)
    if request.user.is_anonymous:
        pass
    else:
        get_user_cart_items = Cart.objects.filter(client=request.user,ordered=False)
        context['cart_items'] = get_user_cart_items

    products = AddInventory.objects.filter(marketer=mm)
    print products
    if products:
        itemDetail = products[0]
        brief_desc = itemDetail.description.split(',')
    else:
        itemDetail = []
        brief_desc = ""
        
    context['products'] = products
    context['itemDetail'] = itemDetail
    context['brief_desc'] = brief_desc

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 10)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    template_name = "zeroelectricac/product_view.html"

    payable=0
    count=0
    try:
        item=Cart.objects.filter(client=request.user, ordered=False)
        context['item']=item
        for i in item:
            payable += i.total()
            count += i.quantity
        context['payable'] = payable
        context['count'] = count
    except:
        item = []
        payable = 0.0
        count = 0
   

    return render(request,template_name, context)



def detail_view(request,item_id):
    context = {}
    mm = marketing_member(request)
    products = AddInventory.objects.filter(marketer=mm)
    itemDetail = get_object_or_404(AddInventory, pk=item_id, marketer=mm)
    # print "each item: ",itemDetail.description
    context['itemDetail'] = itemDetail
    context['products'] = products
    template_name = "zeroelectricac/detail-view.html"

    brief_desc = itemDetail.description.split(',')
    print brief_desc
    context['brief_desc'] = brief_desc
    # To get the total amount the client is to pay for the item bought
    payable=0
    count=0
    try:
        item=Cart.objects.filter(client=request.user, ordered=False)
        context['item']=item
        for i in item:
            payable += i.total()
            count += i.quantity
        context['payable'] = payable
        context['count'] = count
    except:
        item = []
        payable = 0.0
        count = 0

    return render(request,template_name, context)



@login_required
def cart_view(request):    # Client View
    request_user = request.user
    context = {}

    # template_name="zeroelectricac/cart-view.html"
    template_name="zeroelectricac/order.html"

    items = Cart.objects.filter(client=request_user, ordered=False)
    context['items']=items
    # print "Items ", items

    # To get the total amount the client is to pay for the item bought
    payable=0
    count=0
    #item=Cart.objects.filter(client=request.user, ordered=False)
    for item in items:
        payable += item.total()
        count += item.quantity
    context['payable']=payable
    context['count']=count

    # To get the total amount the client is to pay for the item bought
    # count=0
    # item=Cart.objects.filter(client=request.user, ordered=False)
    # for i in item:
    #     count += i.quantity
    

    return render(request, template_name, context)



@login_required
def checking_out(request):
    request_user = request.user
    context={}
    addresses = DeliveryAddress.objects.filter(user=request.user)
    print 'addresses:',addresses
    # items = Cart.objects.filter(client=request_user).filter(ordered=False)
    # To get the total amount the client is to pay for the item bought
    count=0
    payable=0
    items=Cart.objects.filter(client=request.user, ordered=False)
    for i in items:
        count += i.quantity
        payable += i.total()
    context['count']=count
    context['items']=items
    context['payable']=payable
    context['addresses']=addresses

    # To get the total amount the client is to pay for the item bought
    template_name="zeroelectricac/order2.html"
    return render(request,template_name, context)



@login_required
def add_to_cart(request):
    if request.user.is_staff:
        response = redirect (reverse ("general:user_manager"))
        return response
    else:
        rp=request.POST
        # print "i got here", rp
        try:
            get_product = AddInventory.objects.get(id=rp.get('item_id'))
            print get_product
        except:
            return redirect(reverse('general:product_view'))
        item = AddInventory.objects.get(id=rp.get('item_id'))
        get_user_cart, created = Cart.objects.get_or_create(
            client=request.user,item=item,item__item_type="shopping")
        print get_user_cart, created
        if created:
            get_user_cart.quantity=rp.get('item_qty')
        else:
            get_user_cart.quantity +=int(rp.get('item_qty'))
           # get_user_cart.save()
            # docfile = rp.get('item_image'),
            # description=get_product.description,
            # price=get_product.price,
            #quantity=rp.get('item_qty'),
            # details=get_product.title
            #item = AddInventory.objects.get(id=rp.get('item_id')))
        get_user_cart.save()
        print "cart", get_user_cart
        # print "i got here again"
        messages.success(request,"Item has been successfully added to your cart")
        return redirect(reverse('general:product_view'))
    return redirect(reverse('general:product_view'))



@login_required
def delete_item(request, item_id):
    contect={}
    get_item = Cart.objects.get(pk=item_id)
    # print"Id", get_item
    get_item.delete()
    # template_name="zeroelectricac/cart-view.html"
    # return render(request,template_name)
    return redirect (request.META['HTTP_REFERER'])



def LenOf(value):     # Client View
    if len(value) == 2:
        return str(value)
    else:
        return '0' + str(value)



def create_id():    # Client View
    ids = ""
    ids += str(datetime.today().year)[2:]
    ids += LenOf(str(datetime.today().month))
    ids += LenOf(str(datetime.today().second))
    for i in range (0,3):
        ids += str(random.randint(0,9))
    return "AE" + ids



@login_required
def checkout(request):
    request_user=request.user

    checkout_form = CheckoutForm()
    items = Cart.objects.filter(client=request_user).filter(ordered=False)

    # To get the total amount the client is to pay for the item bought
    payable=0
    count=0
    try:
        for i in items:
            payable += i.total()
            count += i.quantity
    except:
        item = []
        payable = 0.0
        count = 0

    
    template_name="zeroelectricac/checkout.html"
    return render(request,template_name, {'checkout_form': checkout_form, 'items':items, 'count':count,'payable':payable})


@login_required
def order_summary(request):
    request_user=request.user
    all_items = Cart.objects.filter(client=request_user, ordered=False)
    if request.method == "POST":
        # print "rp ", request.POST
        client = request.user
        order_number = create_id()
        payable = request.POST['payable']
        # print "PAyable", payable
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address1 = request.POST['address1']
        address2 = request.POST['address2']
        city = request.POST['city']
        email = request.POST['email']
        zip_code = request.POST['zip_code']
        country = request.POST['country']
        state = request.POST['state']

        item, created = Order.objects.get_or_create(client=client, order_number=order_number, payable=payable, first_name=first_name,
            last_name=last_name, address1=address1, city=city, email=email, zip_code=zip_code, country=country, state=state)
        item.save()

        order = Order.objects.filter(order_number = order_number)
        # print "ORDER", order
        all_items.update(ordered = True, order = order[0])
        # my_order = Order.objects.filter(client=request_user).filter(order_number=order_number) #Populate client's Order to template

        my_order = Order.objects.filter(client=request_user)
        # print "TIED ORDER", my_order

    template_name ="zeroelectricac/order-summary.html"
    return render(request,template_name, {'my_order':my_order})


def get_estimate(request):
    rG = request.GET
    unit = rG.get('unit')
    print "unit",unit
    if unit == "sqm":
        select = float(rG.get('select')) * 10.7639
        print "select here:",select
    else:
        select = rG.get('select')
    print "select:",select
    radiovalue = rG.get('radiovalue')
    if radiovalue == "rooms":
        print "rooms"
        quantity = select
        # print quantity
        size = "zeAC 9-Classic"
        price = float(quantity) * float(700)
        # print price
    else:
        # print "surface"
        quantity = int(math.ceil(float(select)/350))
        # print "qty", quantity
        if quantity == 0:
            quantity = 1
        size = "9/12 inch zeAC classic"
        quantity = int(math.ceil(float(select)/350))
        price = float(quantity * 700)
        # print "qty", quantity
            
    return render(request, 'zeroelectricac/get_estimate.html', {'quantity':quantity,'size':size, 'price':price})
        
 
@login_required
@csrf_exempt
def pay_options(request):
    
    context = {}
    count=0
    payable=0
    total_weight = 0
    items = Cart.objects.filter(client=request.user, ordered=False)
    #print "items", items
    # for item in items:
    #     print item.size
    context['items']=items

    # To get the total amount the client is to pay for the item bought
    # count=0
    # item=Cart.objects.filter(client=request.user, ordered=False)

    for i in items:
        count += i.quantity
        payable += i.total()
        total_weight += i.total_weight()
    context['count']=count

    # To get the total amount the client is to pay for the item bought
    # payable=0
    # item=Cart.objects.filter(client=request.user, ordered=False)

    # for i in item:
    #     payable += i.total()
    context['payable']=payable
    context['payable_amt'] = float(payable * 100)
    print "weight",total_weight

    lb_country = "Nigeria"
   
    if request.method == "GET" and (request.GET.has_key('resp')):
        if (request.GET.get('resp') == 'success' or request.GET.get('resp') =='Approved'):
            return redirect(reverse('general:order_confirmation'))
        else:
            shipping_cost = request.session.get['shipping_cost']
            context['total_payable']=shipping_cost + float(payable)
            template_name = 'zeroelectricac/order3.html'
            messages.warning(request, 'Your Transaction was not Successful, please try again later')
            return render(request,template_name,context)

    elif request.method == "POST" and not request.POST.has_key('get_page'):
        amount_paid_D = payable

        # msg_info = "You have successfully paid $%s for package %s" %(str(amount_paid_D), tracking)
        print request.POST
        amount_paid_D = float(request.POST.get('amount'))
        #print request.POST
        #print amt
        # msg_info = "You have successfully paid $%s for package %s" %(str(amount_paid_D), tracki)

        dest_namespace_2 = 'general:pay_options'
        #dest_namespace_2 = 'soko_pay:pay_balance'
        #return call_initiate_payment(request, amount_paid_N, dest_namespace)
        lb_country = "Nigeria"
        # dest_namespace = 'soko_pay:pay_balance'
        kwargs_dict = {'actual_amount_D': amount_paid_D, 'dest_namespace_1': None, 'lb_country':lb_country,
                                   'dest_namespace_2': dest_namespace_2, 'txn_desc': 'Payment for shopping items'}
        return payment_helpers.card_payment(request, **kwargs_dict)
    else:
        print "rp", request.POST
        saved_address_selected = str(request.POST.get('saved_address_selected'))
        selection = str(request.POST.get('selected_add'))
        if selection == "on":
            address = DeliveryAddress.objects.get(pk=saved_address_selected)
            
        else:
            address = DeliveryAddress.objects.create(
            user          = request.user,
            address_line1 = request.POST.get('address1'),
            address_line2 = request.POST.get('address2'),
            city          = request.POST.get('city'),
            state         = request.POST.get('state'),
            country       = request.POST.get('country')
            )
            address.save()
        country = address.country
        print 'country:',country
        state = address.state
        city = address.city
        print "state:",state
        print "city:",city
        request.session['address'] = address
        request.session['requestPOST'] = request.POST
        request.session['item_count'] = count
        request.session['cart_value'] = payable
        request.session['country'] = country
        mm = marketing_member(request)
        subscriber = mm.subscriber
        costcalc = float(marketingmember_costcalc(request, 'Nigeria').dollar_exchange_rate)
        shipping_chain = ShippingChain.objects.get(subscriber=subscriber, origin=country)
        region = LocalDistributorLocation.objects.get(name=shipping_chain.origin_distributor.courier_name,city=city,state=state)
        shipping_price = LocalDistributorPrice.objects.get(region=region.region,weight=total_weight)
        shipping_cost_N = shipping_price.price + (shipping_price.price * shipping_price.mark_up_value/100)
        shipping_cost = round(shipping_cost_N / costcalc, 2)
        context['shipping_cost']= shipping_cost
        context['total_payable']=shipping_cost + float(payable)
        request.session['shipping_cost'] = shipping_cost
        request.session['shipping_chain'] = shipping_chain
        request.session['weight']= total_weight
    template_name = 'zeroelectricac/order3.html'
    return render(request,template_name,context)       


@login_required
def inv_history(request, item_id):
    history = ActionHistory.objects.filter(obj_id=item_id)
    return render (request, 'sokohaliAdmin/userhistory.html', {'history': history})


@login_required
def add_inventory(request):
    context = {}

    mm = marketing_member(request)
    # print "MM", mm
    user = request.user
    print "User :", user

    rp=request.POST
    print "ID :", rp
    if request.POST:
        # print ("REQEST", request.POST)
        add_inventory_form = InventoryForm(request.POST, request.FILES)

        # if add_inventory_form.is_valid():
        #     add_inventory = add_inventory_form.save(commit=False)
            # add_inventory.docfile = AddInventory(docfile = request.FILES['docfile'])
        category=rp.get('category')
        sub_sub_cat=rp.get('sub_sub_cat')
        # print "SUB SUB CAT :", sub_sub_cat
        add_inventory = AddInventory.objects.create(
            item_image=request.FILES['fileupload'],
            title = rp.get('title'),
            description=rp.get('description'),
            price=rp.get('price'),
            colour=rp.get('colour'),
            brand=rp.get('brand'),
            size=rp.get('size'),
            weight=rp.get('weight'),
            quantity=rp.get('quantity'),
            marketer=mm,
            category=Category.objects.get(cat_name = category),
            sub_sub_cat=SubCategory.objects.get(sub_cat_name = sub_sub_cat)
            # sold=rp.get('sold')
            )

        add_inventory.save()

        # user_model="AddInventory"
        # action="New Inventory"
        # status="Inventory successfully added!"
        # user_manager_history(request.user,  item_id=None, user_model, action ,status)


        return HttpResponseRedirect(reverse('general:add_inventory'))
        # else:
        #     print (add_inventory_form.errors)

    else:
        print "Nothing was Posted"
    add_inventory_form = InventoryForm()
    context['form'] = add_inventory_form

    # Load items for the add_inventory page
    all_items = AddInventory.objects.filter(marketer = mm)
    # print "All Items :",all_items
    context['all_items'] = all_items

    itemcount = AddInventory.objects.filter(marketer = mm).count()
    # print "All Items :",all_items
    context['itemcount']=itemcount

    # cat_list = Category.objects.values_list('cat_name', flat=True).distinct()
    cat_list = Category.objects.filter(marketer = mm)
    print "Distinct Item List :",cat_list
    context['cat_list']=cat_list

    dist_itm = SubCategory.objects.values_list('sub_cat_name', flat=True)#.distinct()
    # dist_itm = SubCategory.objects.filter(sub_cat__marketer = mm)
    print "Distinct Item :",dist_itm
    context['dist_itm']=dist_itm


    template_name ="zeroelectricac/add-inventory.html"
    return render(request, template_name, context)


@login_required
def del_inv(request, item_id):
    contect={}
    get_inv = AddInventory.objects.get(pk=item_id)
    # print"Id", get_item
    get_inv.delete()
    # template_name="zeroelectricac/cart-view.html"
    # return render(request,template_name)
    return redirect (request.META['HTTP_REFERER'])


@login_required
def edit_inv(request):
    context = {}

    if request.method == "POST":
        item_id = request.POST.get('item_id')
        print "item_id :", item_id
        itmdetail = get_object_or_404(AddInventory, id=item_id)
    else:
        print "Error"

    context['itmdetail'] = itmdetail

    cat_list = Category.objects.values_list('cat_name', flat=True).distinct()
    print "Distinct Item List :",cat_list
    context['cat_list']=cat_list

    dist_itm = SubCategory.objects.values_list('sub_cat_name', flat=True).distinct()
    print "Distinct Item :",dist_itm
    context['dist_itm']=dist_itm

    template_name ="zeroelectricac/add-inventory.html"
    return render(request, template_name, context)


@login_required
def inv_edited(request):
    context={}
    rp = request.POST
    print "rp", rp
    if request.method == "POST":
        item_id=rp.get('id')
        print "item_id :",item_id

        itemToEdit=get_object_or_404(AddInventory , id=item_id)

        if request.FILES:
            itemToEdit.item_image = request.FILES['fileupload']
            # print "MMM :", mmm

        # itemToEdit.item_image=request.FILES['picture']
        itemToEdit.title=rp.get('title')
        itemToEdit.description=rp.get('description')
        itemToEdit.price=rp.get('price')
        itemToEdit.colour=rp.get('colour')
        itemToEdit.brand=rp.get('brand')
        itemToEdit.size=rp.get('size')
        itemToEdit.weight=rp.get('weight')
        category=rp.get('category')
        itemToEdit.category=Category.objects.get(cat_name =category)
        sub_sub_cat=rp.get('sub_sub_cat')
        itemToEdit.sub_sub_cat=SubCategory.objects.get(sub_cat_name =sub_sub_cat)
        itemToEdit.quantity=rp.get('quantity')
        itemToEdit.item_remaining=rp.get('item_remaining')
        itemToEdit.sold=rp.get('sold')

        itemToEdit.save()
    user_model="AddInventory"
    action="Edited Inventory"
    status="Inventory successfully edited!"
    user_manager_history(request.user,  item_id, user_model, action ,status)

    return redirect(request.META['HTTP_REFERER'])


@login_required
def view_item(request):
    context = {}

    if request.method == "POST":
        item_id = request.POST.get('item_id')
        print "item_id :", item_id
        itmdetail = get_object_or_404(AddInventory, id=item_id)
        mmm = itmdetail.title
        # print "Title :", mmm
    else:
        print "Error"

    context['itmdetail'] = itmdetail

    template_name ="zeroelectricac/add-inventory.html"
    return render(request, template_name, context)


@login_required
def inv_sidebar_category(request):
    context = {}

    mm = marketing_member(request)

    items = AddInventory.objects.filter(marketer = mm)
    item = items.count()
    return render(request, 'zeroelectricac/add-inventory.html', {'item': item})


def order_confirmation(request):
    context = {}
    tracking_no = generate_local_tracking_no(request)
    chain = request.session['shipping_chain']
    address = request.session['address']
    shipper = chain.origin_distributor
    mm = marketing_member(request)
    weight = request.session['weight']
    shipping_cost = request.session['shipping_cost']
    cart_value = request.session['cart_value']
    todaysdate  = timezone.now()
    local_pkg = DomesticPackage.objects.create(
        user=request.user,
        tracking_number=tracking_no,
        weight_kg=weight,
        amount=shipping_cost,
        balance_paid=shipping_cost,
        marketer=mm,
        shipper=shipper,
        created_on=todaysdate,
        weight_lb = float(weight) * 2.2,
        dropoff_address=address)
    local_pkg.save()
    user_cart = Cart.objects.filter(client=request.user, ordered=False)
    order_number = create_id()
    payable = float(cart_value) + shipping_cost
    order = UserOrder.objects.create(
        client=request.user,
        order_number=order_number,
        payable=payable,
        local_pkg=local_pkg,
        created_on=todaysdate)
    order.save()
    for item in user_cart:
        item.item.user_order = order
        item.ordered = True
        item.save()

    context['item'] = []
    context['payable'] = 0.0
    context['count'] = 0

    context['address']=address
    context['payment_method']= 'Card'
    context['cart_items']=user_cart
    context['cart_value']=cart_value
    context['shipping_cost']=shipping_cost
    context['payable']=payable
    context['weight']=weight
    template_name = 'zeroelectricac/order4.html'

    del request.session['address']
    del request.session['requestPOST']
    del request.session['item_count']
    del request.session['cart_value']
    del request.session['country']
    del request.session['shipping_cost']
    del request.session['shipping_chain']
    del request.session['weight']

    return render(request, template_name, context)

def track_shipments(request):
    context = {}
    template_name = "user_account/trackShipments.html"
    return render(request,template_name,context)


@login_required(login_url='/volk/login')
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
def shipment_detail_volk(request):
    context = {}
    try:
        shipping_item = ShippingPackage.objects.get(pk=request.GET.get('item_id'))
        context['shipping_item'] = shipping_item
        context['items'] = shipping_item.item_packages()
    except:
        context['shipping_item'] = None
        context['items'] = None
    template_name = "zaposta_snippet/shipment_details.html"
    return render(request,template_name,context)

    
@login_required(login_url='/volk/login')
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
def shipment_detail_number_volk(request):
    context = {}
    try:
        shipping_item = ShippingPackage.objects.get(tracking_number=request.GET.get('item_id'))
        context['shipping_item'] = shipping_item
        context['items'] = shipping_item.item_packages()
    except:
        context['shipping_item'] = None
        context['items'] = None
    template_name = "zaposta_snippet/shipment_details.html"
    return render(request,template_name,context)


@login_required(login_url='/volk/login')
@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/backend/user-manager/')
@user_passes_test(address_activated_new, login_url='/redirect_to_address_activation_new/', redirect_field_name=None )
def my_tracker_volk(request):
    context = {}
    template_name = "volkmann/trackshipments.html"
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0
    context['count_items'] = count_items
    return render(request,template_name,context)


@login_required
def vei_shopper(request):
    try:
        mm = marketing_member(request)
        subscriber = mm.subscriber
        print "subscriber:",subscriber
        marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
    except:
        subscriber = request_subscriber(request)
        marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
        
    addresses = DeliveryAddress.objects.filter(user=request.user)

    context = {}
    shipping_obj = ShippingItem.objects.filter(user=request.user,tag="Shopping",deleted=False)
    template_name = 'volkmann/userShopping.html'
    context['shipments'] = shipping_obj
    context['marketer_routes'] = marketer_routes
    context['addresses'] = addresses

    if request.method == "POST":
        rp = request.POST
        shipping_obj = ShippingItem.objects.create(
            user=request.user,
            link=rp.get('link'),
            status_2='New',
            description=rp.get('description'),
            quantity=rp.get('quantity'),
            tag="Shopping",
            marketer=mm,
            balance=float(rp.get('amount')),
            total_value=rp.get('amount'),
            courier_tracking_number=get_random_code(20))
        messages.success(request,"Your shopping request was successfully submitted. Please wait patiently as a company representative will get back to you within 12 hours")

    else:
        return render(request,template_name,context)
    return redirect (request.META.get('HTTP_REFERER', '/'))

def generate_purchaseRef():
    rand = ''.join(
             [random.choice(
                 string.ascii_letters + string.digits) for n in range(16)]) 
    return rand


def purchase_ref():
    ref = generate_purchaseRef()#+ "|%s" %obj_id
    return ref


@login_required
def crud_pay_for_shop(request,action,item_id,amount):
    mm = marketing_member(request)
    shipping_obj = ShippingItem.objects.get(id=item_id)
    if action == 'delete':
        shipping_obj.deleted = True
        shipping_obj.save()
        messages.warning(request, "Order has been successfully removed.")
    elif action == 'pay':
        userAccountBalance = UserAccount.objects.get(user=request.user)
        if userAccountBalance.credit_amount_D <= 0:
            messages.warning(request, "Insufficient wallet balance. Please fund your VEI Wallet.")
            return redirect (request.META.get("HTTP_REFERER", "/"))
        elif userAccountBalance.credit_amount_D <= float(amount):
            messages.warning(request, "Insufficient wallet balance. Please fund your VEI Wallet.")
            return redirect (request.META.get("HTTP_REFERER", "/"))
        else:
            shipping_obj.balance = 0.0
            shipping_obj.amount_paid = float(shipping_obj.amount_paid) + float(amount)
            shipping_obj.status_2 = "paid"
            shipping_obj.save()
            userAccountBalance.credit_amount_D = userAccountBalance.credit_amount_D - float(amount)
            userAccountBalance.save()

            payment = MarketerPayment.objects.create(
                user=request.user.useraccount,
                payment_channel=None,
                purchase_type_2="Remove",
                purchase_type_3="veiwallet",
                created_at=timezone.now(),
                message="Payment for shopping order",
                status="Approved",
                amount=amount,
                ref_no=purchase_ref(),
                marketer=mm,
                bank=None,
                teller_no=None)

            messages.success(request, "You have successfully paid for this order. Please note that this price may be updated due to fluctuations in dollar exchange rates.")
    return redirect (request.META.get('HTTP_REFERER', '/'))

@csrf_exempt
def view_edit_shopping_item_order(request):
    context = {}
    print "pk", request.GET.get('data')
    shipping_obj = ShippingItem.objects.get(pk=request.GET.get('data'))
    context['shop_obj'] = shipping_obj
    template_name = 'volkmann/view_edit_shop_order.html'
    return render(request,template_name,context)

@login_required
def edit_shop_request(request):
    shipping_obj = ShippingItem.objects.get(pk=request.POST.get('item_id'))
    shipping_obj.link = request.POST.get('link')
    shipping_obj.description = request.POST.get('description')
    shipping_obj.quantity = request.POST.get('quantity')
    shipping_obj.total_value = request.POST.get('amount')
    shipping_obj.balance = request.POST.get('amount')
    shipping_obj.save()
    messages.success(request, "Your edit was successful. Please note that this price may be updated due to fluctuations in dollar exchange rates.")
    return redirect (request.META.get('HTTP_REFERER', '/'))


def zeac_contct_us(request):
    context = {}
    rp= request.POST
    print "RP ",rp
    if request.method =='POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
    else:
        print "You didn't fill all the details"
    try:
        subject = subject
        user = name
        message = message
        email = email
        marketer_contactus_mail(request, user, subject, message, email)
    except Exception as e:
        print'error: ',e
        pass
    return redirect (request.META.get('HTTP_REFERER', '/'))