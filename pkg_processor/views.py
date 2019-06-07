from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import JsonResponse
from shipping.models import ShippingPackage
from itertools import chain
import ast

from general.image_helpers import convert_base64_to_image
from general.models import ActionHistory, UserAccount
from service_provider.models import Subscriber
from django.db.models import Q, Count, Sum
from django.contrib import messages
from base64 import b64decode
import json, random, datetime
from django.core.files.base import ContentFile
from sokohaliAdmin.views import get_counntry_from_short_code
from shipping.PackageCostCalculator import *
from shipping.CreateShipmentCostCalculator import *

from general.custom_functions import firstStringCharisI, get_marketing_member_users, marketing_member, sokohali_sendmail, sokohali_send_notification_email, get_marketing_member_user, shipment_history, generate_creditpurchase_ref
from sokohaliAdmin.forms import notifyUserForm, ShippingPackageForm
from shipping.forms import *
from sokopay.models import *
from sokohaliAdmin.models import *
from sokohaliAdmin.forms import *



#from general.models import UpdateHistory

max_sync_pkg_count = 400


def createHistory(update_by, status, pkg, created_on):
    barcode_id = pkg.gen_barcode_id()
    action = "Update package status to %s" %status

    if hasattr(pkg, "export"):
        ActionHistory.objects.get_or_create(user = update_by, created_on = created_on, obj_id = pkg.id,
                             obj_model_name = "ExportPackage", action = action, obj_description = "ExportPackage")
        # UpdateHistory.objects.get_or_create(user = update_by, created_on = created_on,
        #                                     defaults={'exportpackage': pkg, 'status': status})
    else:
        ActionHistory.objects.get_or_create(user = update_by, created_on = created_on, obj_id = pkg.id,
                             obj_model_name = "ShippingPackage", action = action, obj_description = "ShippingPackage")

def update_pkg_values(pkg, processed_pkg_dict):
    pkg.box_length      = processed_pkg_dict["box_length"]
    pkg.box_width       = processed_pkg_dict["box_width"]
    pkg.box_height      = processed_pkg_dict["box_height"]
    pkg.box_weight      = processed_pkg_dict["box_weight"]
    pkg.box_weight_K    = processed_pkg_dict["box_weight_K"]
    pkg.status          = processed_pkg_dict["status"]
    pkg.syncedStatus    = True
    pkg.save()


def upload_package_image(pkg, package_image_dict):
    print 'uploading package'
    filename = '%s.jpg' %package_image_dict['tracking_number']
    pkg.pkg_image           = convert_base64_to_image(package_image_dict['image_base64'], filename)
    pkg.save()


# Create your views here.
@csrf_exempt
def login(request):
    if request.method == "POST":

        rp = request.POST
        print "rp:",rp
        email = rp.get('email')
        password = rp.get('password')
        try:
            if "@" in email:
                #authenticate user
                print "i got here and saw email"
                email = email
            else:
                print "its not an email"
                try:
                    user_obj = User.objects.get(username=email)
                    print user_obj
                    email = user_obj.email
                    print email
                except Exception as e:
                    print "the authentication failed because of ", e
                    return JsonResponse({"success": 0, "error": 1, "error_message": "There is an error with the Email/Password combination!"})

            user = authenticate(email=email, password=password)
            print "me now",user
        except:
            return JsonResponse({"success": 0, "error": 1, "error_message": "There is an error with the Email/Password combination!"})
        
        if user is not None:
            if user.is_staff:
                try:
                    user.useraccount

                    user_info = {"user_id": user.id, "full_name": user.get_full_name(),
                                 "username": user.username, "email": email}

                    return JsonResponse({"success": 1, "error": 0, "user_info": user_info})

                except:
                    return JsonResponse({"success": 0, "error": 1, "error_message": "Access Denied!!! This app is for members of 'STAFF ONLY' with appropriate credentials!!!."})


                             #"authorization_key": auth_key}
                #return HttpResponse(json.dumps({"success": 1, "error": 0,
                #                                "user_info": user_info}),
                #                content_type="application/json")
                # return JsonResponse({"success": 1, "error": 0, "user_info": user_info})
            else:
                user_info = {"user_id": user.id, "full_name": user.get_full_name(),
                                 "username": user.username, "email": email}
                return JsonResponse({"success": 2, "error": 1, "user_info": user_info})
                #return HttpResponse(json.dumps({"success": 0, "error": 1, "error_message": "Access Denied!!! This app is meant for STAFF ONLY!!!."}),
                #                content_type="application/json")
        else:
            #return HttpResponse(json.dumps({"success": 0, "error": 1, "error_message": "There was an error with the Email/Password combination!"}),
            #                    content_type="application/json")
            return JsonResponse({"success": 0, "error": 1, "error_message": "There is an error with the Email/Password combination!"})
    else:
        #return HttpResponse(json.dumps({"success": 0, "error": 1}),
        #                    content_type="application/json")
        return JsonResponse({"success": 0, "error": 1})



@csrf_exempt
def find_user_obj(request):

    #print "i got here"
    ''' revisit this function '''
    # mm = marketing_member(request)
    # print request.POST
    if request.method == "POST":
        rp = request.POST
        try:
            user_acc = UserAccount.objects.get(user__email__iexact=rp.get('admin_user'))
        except:
            user_acc = UserAccount.objects.get(user__username__iexact=rp.get('admin_user'))
        mm = user_acc.marketer
        print "MM: ",mm
        query = rp['query']

        user_info = UserAccount.objects.filter(
                    (Q(suite_no = query)|
                    Q(first_name__icontains = query)|
                    Q(last_name__icontains = query)|
                    Q(user__email__iexact = query)), marketer=mm, user__is_staff=False).values()

        # print user_info


        print len(user_info)
        if len(user_info) != 0:
            return JsonResponse({"success": 1, "error": 0, "user_info": list(user_info)})
        else:
            return JsonResponse({"success": 0, "error": 1, "error_message": "No matching result found the query value supplied","user_info": list(user_info)})
    else:
        return JsonResponse({"success": 0, "error": 1, "error_message": "Oops something went wrong....Please contact the Engineers!!!","user_info": list(user_info)})


@csrf_exempt
def user_notify(request):
    if request.method == "POST":
        rp = request.POST
        rf = request.FILES
        # print 'rp:',rp
        get_user = UserAccount.objects.get(id=rp.get('user_id'))
        mm = get_user.marketer
        # suite_no = get_user.suite_no
        # print "suite_no: ",suite_no
        try:
            get_admin = User.objects.get(email=rp.get('email'))
        except:
            get_admin = User.objects.get(username=rp.get('email'))
        # print "marketer: ",get_admin
        form = notifyUserForm(request.POST, request.FILES)


        if form.is_valid():
            create_notify_form = form.save(commit=False)
            create_notify_form.name = rp.get('id_name')
            create_notify_form.address = get_user.user_address()
            create_notify_form.suite_no = get_user.suite_no 
            create_notify_form.item_description = rp.get('id_desc')
            create_notify_form.last_four_digits = rp.get('id_last_four_digits')     
            create_notify_form.created_by = get_admin
            create_notify_form.weight = rp.get('id_wgt')
            create_notify_form.user = get_user.user
            imageURL  = request.POST.get('id_file', '')
            # x = imageURL[23:]
            image_data = b64decode(imageURL)
            photo_code = ''
            characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
            photo_code_length = 20
            for x in range(photo_code_length):
                 photo_code += characters[random.randint(0, len(characters)-1)]
            photo_name = photo_code + '.jpeg'
            photo = ContentFile(image_data, photo_name)
            # print "photo:", photo
            create_notify_form.image_field = photo
            # print "photo", create_notify_form.image_field
            create_notify_form.save()

            pkg = create_notify_form
            # print 'desc:', pkg.item_description
            # print 'LFD:', pkg.last_four_digits
            user = get_user.user

            shipping_item = ShippingItem.objects.create(
                user=get_user.user,
                weight=create_notify_form.weight,
                courier_tracking_number=create_notify_form.last_four_digits,
                description=create_notify_form.item_description,
                status="Received",
                created_by=get_admin,
                notify=create_notify_form)
    
            # print user.username
            pkg = create_notify_form
            print 'desc:', pkg.item_description
            print 'LFD:', pkg.last_four_digits
            user = get_user.user
            print user.username
            title = "Package Creation Notification"
            text = 'email/notify_user.html'
            try:
                print "1"
                sokohali_send_notification_email(mm, user, title, text, pkg)
            except Exception as e:
                print "message was not sent because of ", e
            return JsonResponse({"success": 1, "error": 0})
        else:
            # print form.errors
            return JsonResponse({"success": 0, "error": 1})
    return JsonResponse({"success": 0, "error": 1})


@csrf_exempt
def create_job(request):
    print request.POST
    rp = request.POST

    pick_up_time = str(rp.get('pick_up_time')).split(".")[::-1]
    drop_off_time = str(rp.get('drop_off_time')).split(".")[::-1]

    pick_up_time = '-'.join(pick_up_time)
    drop_off_time = '-'.join(drop_off_time)

    form = TruckingForm(request.POST, request.FILES)
    if form.is_valid():
        truckForm = form.save(commit=False)
        truckForm.created_by = request.POST.get('email')
        truckForm.status = "New"
        truckForm.drop_off_time = drop_off_time
        truckForm.pick_up_time = pick_up_time
        truckForm.save()
        return JsonResponse({"success": 1, "error": 0})
    else:
        print form.errors
        return JsonResponse({"success": 0, "error": 1})


@csrf_exempt
def accept_job(request):
    rp = request.POST
    print "i want to accept this job"

    truck_obj = Trucking.objects.get(job_number=rp.get('job_number'))
    truck_obj.cargo_decsription = rp.get('description')
    truck_obj.done_by = rp.get('email')
    truck_obj.actual_cargo_weight = rp.get("actual_weight")
    truck_obj.total_cargo_weight = rp.get("total_weight")
    truck_obj.bol_number = rp.get("bol_number")
    truck_obj.origin = rp.get('job_origin')
    truck_obj.destination = rp.get("job_destination")
    truck_obj.status = "ongoing"
    truck_obj.save()
    
    return JsonResponse({"success": 1, "error": 0})


@csrf_exempt
def complete_job(request):
    rp = request.POST
    print "i want to complete this job"

    try:
        user_acc = UserAccount.objects.get(user__email__iexact=rp.get('email'))
        userName = user_acc.user.username
    except:
        user_acc = UserAccount.objects.get(user__username__iexact=rp.get('email'))
        userName = user_acc.user.username
    
    truck_obj = Trucking.objects.get(job_number=rp.get('job_number'))
    truck_obj.cargo_decsription = rp.get('description')
    truck_obj.done_by = rp.get('email')
    truck_obj.actual_cargo_weight = rp.get("actual_weight")
    truck_obj.total_cargo_weight = rp.get("total_weight")
    truck_obj.bol_number = rp.get("bol_number")
    truck_obj.origin = rp.get('job_origin')
    truck_obj.destination = rp.get("job_destination")
    truck_obj.status = "completed"
    truck_obj.done_by = userName

    imageURL  = rp.get('id_file', '')
    # x= imageURL[23:]
    image_data = b64decode(imageURL)
    photo_code = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    photo_code_length = 20
    for x in range(photo_code_length):
         photo_code += characters[random.randint(0, len(characters)-1)]
    photo_name = photo_code + '.jpeg'
    photo = ContentFile(image_data, photo_name)
    truck_obj.bol_image = photo
    truck_obj.save()

    return JsonResponse({"success": 1, "error": 0})
    


@csrf_exempt
def decline_job(request):
    rp = request.POST
    print "i want to decline this job"

    truck_obj = Trucking.objects.get(job_number=rp.get('job_number'))
    truck_obj.status = "New"
    truck_obj.save()

    return JsonResponse({"success": 1, "error": 0})


@csrf_exempt
def get_packages(request):
    # print request.POST
    if request.method == "POST":
        rp = request.POST
        try:
            user_acc = UserAccount.objects.get(user__email__iexact=rp.get('email'))
        except:
            user_acc = UserAccount.objects.get(user__username__iexact=rp.get('email'))
        mm = user_acc.marketer
        # print "MM: ",mm


        packages_list = ShippingPackage.objects.filter(prepared_for_shipping=False, user__useraccount__marketer=mm, shipment_type="Regular")
        packages_info = packages_list.values()
        packages_count= packages_list.count()


        print len(packages_info)
        if len(packages_info) != 0:
            print "got here"
            return JsonResponse({"success": 1, "error": 0, "packages_info": list(packages_info), "packages_count":packages_count})
        else:
            return JsonResponse({"success": 0, "error": 1, "error_message": "No unprocessed packages found","packages_info": list(packages_info), "packages_count":packages_count})
    else:
        return JsonResponse({"success": 0, "error": 1, "error_message": "Oops something went wrong....Please contact the Engineers!!!","packages_info": list(packages_info), "packages_count":packages_count})



@csrf_exempt
def get_trucking(request):
    print request.POST
    if request.method == "POST":
        rp = request.POST
        try:
            user_acc = UserAccount.objects.get(user__email__iexact=rp.get('email'))
            userName = user_acc.user.username
        except:
            user_acc = UserAccount.objects.get(user__username__iexact=rp.get('email'))
            user = user_acc.user.username
        mm = user_acc.marketer
        # print "MM: ",mm


        if request.POST.get('status') == 'new':
            packages_list = Trucking.objects.filter(status="New")
            packages_info = packages_list.values()
            packages_count= packages_list.count()
            print "new count",packages_count
        elif request.POST.get('status') == 'ongoing':
            packages_list = Trucking.objects.filter(status="ongoing",done_by=userName)
            packages_info = packages_list.values()
            packages_count= packages_list.count()
            print "ongoing count",packages_count
        else:
            packages_list = Trucking.objects.filter(status="completed",done_by=userName)
            packages_info = packages_list.values()
            packages_count= packages_list.count()
            print "completed count",packages_count


        print len(packages_info)
        if len(packages_info) != 0:
            print "got here"
            return JsonResponse({"success": 1, "error": 0, "packages_info": list(packages_info), "packages_count":packages_count})
        else:
            return JsonResponse({"success": 0, "error": 1, "error_message": "No unprocessed packages found","packages_info": list(packages_info), "packages_count":packages_count})
    else:
        return JsonResponse({"success": 0, "error": 1, "error_message": "Oops something went wrong....Please contact the Engineers!!!","packages_info": list(packages_info), "packages_count":packages_count})



@csrf_exempt
def mobile_packages_process(request):
    # print request.POST

    rp = request.POST
    
    tracking_number = str(rp.get('tracking_number'))
    quantity = 1

    post = get_object_or_404(ShippingPackage, tracking_number=tracking_number)

    try:
        mm = UserAccount.objects.get(user__username__iexact=rp.get('email')).marketer
    except:
        mm = UserAccount.objects.get(user__email__iexact=rp.get('email')).marketer


    # print "marketer: ", mm

    request.session['package'] = post
    # print model_to_dict(post)
    previous ={"height":post.box_height, "length":post.box_length, "width":post.box_width, "weight":post.box_weight, "weight_k":post.box_weight_K, "insurance":post.insure, "Shipping-method":post.shipping_method}
    # print "previous:", previous
    costcalc = post.costcalc_instance
    weightFactor   = costcalc.dim_weight_factor
    # print "weight_factor: ",weightFactor
    lb_kg_factor   = costcalc.lb_kg_factor
    kg_lb_factor   = costcalc.kg_lb_factor
    exchange_rate  = costcalc.dollar_exchange_rate

    costcalc       = post.costcalc_instance

    weightFactor   = costcalc.dim_weight_factor
    lb_kg_factor   = costcalc.lb_kg_factor
    kg_lb_factor   = costcalc.kg_lb_factor
    exchange_rate  = costcalc.dollar_exchange_rate

    # for field,value in post._meta.get_all_field_names():
    #     print field

    weight_unit = str(rp.get("unit"))

    # post_values = model_to_dict(post)

    new_tracking_number = post.tracking_number[15:].split('-')

    ship_origin = new_tracking_number[0]
    ship_destination = new_tracking_number[1]

    shipping_origin = country = get_counntry_from_short_code(ship_origin)
    # print 'shipping_origin:',shipping_origin
    shipping_destination = get_counntry_from_short_code(ship_destination)
    # print "shipping_destination:",shipping_destination
    
    check_exp_sea_or_air_freight = str(post.shipping_method)
    check_home_or_ofice = str(post.delivery_method)
    # print "Exp_Air_Sea - Home_Office: ",check_exp_sea_or_air_freight,check_home_or_ofice

    if check_exp_sea_or_air_freight == "Air Freight" and post.delivery_method == "Home delivery":
        request.session['dvm'] = "AF - HD"
    elif check_exp_sea_or_air_freight == "Air Freight" and post.delivery_method == "Office pickup":
        request.session['dvm'] = "AF - OP"
    elif check_exp_sea_or_air_freight == "Sea Freight" and post.delivery_method == "Office pickup":
        request.session['dvm'] = "SF - OP"
    elif check_exp_sea_or_air_freight == "Sea Freight" and post.delivery_method == "Home delivery":
        request.session['dvm'] = "SF - HD"
    elif check_exp_sea_or_air_freight == "Express" and post.delivery_method == "Home delivery":
        request.session['dvm'] = "EX - HD"
    elif check_exp_sea_or_air_freight == "Express" and post.delivery_method == "Office pickup":
        request.session['dvm'] = "EX - OP"

    request.session['handling_option'] = post.handling_option

    freight_VAT_SC_D = PSDG_D = VAT_D = coverage_amount_D = 0
    pick_up_charge_D = pick_up_charge_N = 0.0

    if request.method == "POST":
            
        form = ShippingPackageForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.box_length = float(str(rp.get('lenght')))
            post.box_width  = float(str(rp.get('width')))
            post.box_height = float(str(rp.get('height')))
            post.box_weight = float(str(rp.get('weight')))
            # post.pkg_image  =  truncateCharacters(str(rp.get('contact_image_1')))
            imageURL  = rp.get('id_file', '')
            # x= imageURL[23:]
            image_data = b64decode(imageURL)
            photo_code = ''
            characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
            photo_code_length = 20
            for x in range(photo_code_length):
                 photo_code += characters[random.randint(0, len(characters)-1)]
            photo_name = photo_code + '.jpeg'
            photo = ContentFile(image_data, photo_name)
            post.pkg_image = photo
            # print "photo", photo
            if weight_unit == "lbs":
                post.box_weight_Dim = quantity * (post.box_length * post.box_width * post.box_height) / weightFactor
                post.box_weight_Dim_K = post.box_weight_Dim * lb_kg_factor
                # print "lbs wgt_d - wgt_k: ",post.box_weight_Dim,post.box_weight_Dim_K
                post.box_weight_K = post.box_weight * lb_kg_factor
                post.box_weight_Actual = post.box_weight * quantity
                post.box_weight_Actual_K = post.box_weight * lb_kg_factor * quantity
                post.shipping_method = check_exp_sea_or_air_freight
            else:
                post.box_weight_Dim = quantity * (post.box_length * post.box_width * post.box_height) / weightFactor
                post.box_weight_Dim_K = post.box_weight_Dim * lb_kg_factor
                # print "kgs wgt_d - wgt_k: ",post.box_weight_Dim,post.box_weight_Dim_K
                post.box_weight_K = post.box_weight * lb_kg_factor
                post.box_weight_Actual = post.box_weight * 2.20462 * quantity
                post.box_weight_Actual_K = post.box_weight * lb_kg_factor * quantity


            try:
                user = User.objects.get(username=rp.get('email'))
            except:
                user = User.objects.get(email=rp.get('email'))

            
            post.updated_by =  user.username
            post.updated_on =  timezone.now()
            # post.delivery_method = request.POST.get('pkg_delivery_method')
            post.approved = True

            post.prepared_for_shipping = True
            post.status = "Prepared for shipping"

            linked_items = post.item_packages()
            cart_value = linked_items.aggregate(value = Sum('total_value'))['value']
            item_count = linked_items.count()
                
            new_post = []
            new_post.append(post)

            shipping_weight = post.box_weight_higher()

            # region = location.region

            # local_freight_cost_D, local_freight_cost_N = region_local_freight_costs(request,region, shipping_weight)

            local_freight_cost_D = post.local_freight_D

            # print "local_freight_cost_N , local_freight_cost_D:",local_freight_cost_D

            delivery_intl_freight_D, delivery_local_freight_D, delivery_total_freight_D  = get_freight_costs(request, new_post, shipping_origin[0], shipping_destination[0], costcalc)

            total_freight_D  = delivery_intl_freight_D + local_freight_cost_D

            # print "total_freight_D = delivery_intl_freight_D + local_freight_cost_D :",delivery_intl_freight_D + local_freight_cost_D
            # print "shipping_weight: ", post.box_weight_higher()

            pkg_info = {'pkg_count': post.box_quantity, 'item_count': item_count,
                                             'shippingWeight': shipping_weight, 'cart_value': cart_value, 'total_freight_D': delivery_total_freight_D}

            total_freight_D_val, VAT_D_val, totalServiceCharge_D_val, \
                CON_D_val, PSDG_D_val, SMP_D_val, freight_VAT_SC_D_val, coverage_amount_D_val, exchange_rate = CreateShipmentCostCalc(request, pkg_info, country, post.costcalc_instance)

            freight_VAT_SC_D   += freight_VAT_SC_D_val
            PSDG_D             += PSDG_D_val
            VAT_D              += VAT_D_val
            coverage_amount_D  += coverage_amount_D_val

            post.insurance_fee_D = PSDG_D_val
            post.insurance_fee_N = PSDG_D_val * exchange_rate

            post.VAT_charge_D = VAT_D_val
            post.VAT_charge_N = VAT_D_val * exchange_rate

            post.service_charge_D = totalServiceCharge_D_val
            post.service_charge_N = totalServiceCharge_D_val * exchange_rate

            if post.discount_percentage:
                post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val
                post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val) * exchange_rate
                post.discount_D = (post.discount_percentage * post.admin_total_payable_D) / 100
                post.discount_N = (post.discount_percentage * post.admin_total_payable_N) / 100
            else:
                post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val
                post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val) * exchange_rate

            post.coverage_amount_D = coverage_amount_D_val
            post.coverage_amount_N = coverage_amount_D_val * exchange_rate

            # post.pick_up_charge_D = pick_up_charge_D
            # post.pick_up_charge_N = pick_up_charge_N

            if not post.balance_paid_D > post.admin_total_payable_D:
                if post.discount_percentage:
                    post.balance_D = (post.user_total_payable_D - post.balance_paid_D) - post.discount_D
                    post.balance_N = (post.user_total_payable_N - post.balance_paid_N) - post.discount_N
                else:
                    post.balance_D = (post.user_total_payable_D - post.balance_paid_D)
                    post.balance_N = (post.user_total_payable_N - post.balance_paid_N)

            else:
                user = UserAccount.objects.get(user=post.user)
                user_country = user.country
                #print "balance_D", post.balance_D
                #print "balance_paid_D", post.balance_paid_D
                if user_country == "United States" or user_country == "USA":
                    amount = post.balance_paid_D - post.admin_total_payable_D
                else:
                    amount = post.balance_paid_N - post.admin_total_payable_N
                #print "amount", amount
                post.balance_paid_D = post.admin_total_payable_D
                post.balance_paid_N = post.admin_total_payable_N
                post.balance_D = post.balance_N = 0.00
                jejepay_obj = SokoPay.objects.create(user=post.user,purchase_type_1="Refund", purchase_type_2="Add", status = "Approved", ref_no = creditpurchase_ref(request),
                amount=amount,bank="Admin", message="Excess amount added to customer Vei wallet" )
                #print "jeje", jejepay_obj
                # post.balance_D = 0.00
                # post.balance_N = 0.00

            post.intl_freight_D = delivery_intl_freight_D
            post.intl_freight_N = delivery_intl_freight_D * exchange_rate

            post.local_freight_D = local_freight_cost_D
            post.local_freight_N = local_freight_cost_D * exchange_rate

            post.save()

            for item in linked_items:
                item.status = "Received"
                item.save()

            edit ={"height":post.box_height, "length":post.box_length, "width":post.box_width, "weight":post.box_weight, "weight_k":post.box_weight_K, "insurance":post.insure, "Shipping-method":post.shipping_method}
            pkg_model = "ShippingPackage"
            # print "edit:", edit
            
            status = post.status
            action = "This package was prepared for shipping"
                #pkg_status_list(post.pk,pkg_model,request.user,status)
            shipment_history(user,post.pk,pkg_model,status,action)
            # del request.session['pkg_location_id']

            try:
                del request.session['dvm']
            except:
                pass


            if post.user.useraccount.marketer.storefront_name == "volkmannexpress":
                marketer = marketing_member(request)
                print "the marketer is %s" %(marketer)
                user_client = UserAccount.objects.get(user = post.user)
                payment_channel = 'Bank Deposit'
                message = 'Being Payment for package balance'
                amount = post.admin_total_payable_D
                ref_no = generate_creditpurchase_ref()
                bank = None
                teller_no = None
                local_package = None
                payment = MarketerPayment.objects.create(user=user_client,payment_channel=payment_channel,created_at=datetime.now(),message=message,
                                                         amount=amount,package=post,ref_no=ref_no,marketer=marketer,bank=bank,teller_no=teller_no,local_package=local_package)
                payment.save()

            del request.session['handling_option']
            del request.session['package']

            try:
                #user = User.objects.get(email=post.user.email)
                user = get_marketing_member_user(request, post.user.username)
                pkg = post
                subject = "%s Package-%s Invoice" %(mm.storefront_name.title(), pkg.tracking_number)
                # sokohali_sendmail(request, user, subject, "email/package_invoice_email_template.html", pkg)
                print 'email was sent to',user
            except Exception as e:
                print "email not sent because:  %s" %(str(e))
                pass
            return JsonResponse({"success": 1, "error": 0})
        else:
            print form.errors
            return JsonResponse({"success": 0, "error": 1})

    else:
        return JsonResponse({"success": 0, "error": 1})

    return JsonResponse({"success": 0, "error": 1})



