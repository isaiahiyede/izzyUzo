from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from models import ShippingItem, ShippingPackage, DeliveryAddress, CourierLabel
from forms import AddCustomPackageForm, BillMeLaterForm, DeliveryMethodForm, AddressBookForm
from django.contrib import messages
from django.forms.models import model_to_dict
from django.template.context import RequestContext
from django.shortcuts import redirect, get_object_or_404, render, get_list_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from service_provider.models import WarehouseMember,LocalDistributorLocation, LocalDistributorPrice, MarketingMember, WarehouseLocation
from shipping.models import PickupLocation, DropOffPostOffice, ShippingPackageInvoice, DockReceipt, DomesticPackage#, USPSLabel
from general.custom_functions import costcalc_settings, country_exchange_rate, country_freight_costs, get_packages, get_no_of_packages, \
																		get_cart_items, selected_delivery_address_id, get_customer_addresses, shipping_Weight, cartWorth, TrackingNumber, create_obj_costcalc,\
																		pkg_Actual_Dim_Weights, update_pkg_values, update_pkg_total_value, marketing_member, marketingmember_costcalc, \
																		get_local_freight_from_state, region_local_freight_costs,get_office_pickup_locations, format_num,get_context_dicts, sokohali_sendmail, form_errors, \
																		initialize_paypal_payment,pkg_status_list, fetch_country_regions, shipment_history, generate_creditpurchase_ref
from general.forms import paymentTypeForm
from general.templatetags.currency import country_currency_v1
from general.keywordShippingWeight import suggestedWeightAndInfo
import time
#from SelectPackageCostCalculator import SelectPackageCostCalc, get_freight_costs
from CreateShipmentCostCalculator import CreateShipmentCostCalc

from PackageCostCalculator import PackageCostCalc, get_freight_costs

from sokopay.templatetags.account_standing import account_standing
from sokopay.models import SokoPay, MarketerPayment
from sokohaliAdmin.models import PreDefinedBoxes
import json, ast
from django.db.models import Sum, F, Q
from general.staff_access import *
import math
import pycountry
from general.payment_helpers import creditpurchase_ref, initiate_payment, call_initiate_payment,\
	apply_shipping_credit, update_payment_record_for_packages, call_verify_payment,\
	card_payment, create_paypal_instance, update_paypal_payment_record_for_packages
from general.image_helpers import convert_base64_to_image
import os
from general import flutterwave_helpers
from sokohaliv2.settings import PAYPAL_RECEIVER_EMAIL
from general.barcode_generator import generate_package_barcode
from general.models import ActionHistory, AddressBook
from cities_light import models as world_geo_data

from pkg_charges import calculate_pickup_charge, calculate_last_mile_charges
from sokopay.views import select_payment_option
from generate_pkg_label import origin_distributor_access
from datetime import datetime
from usps_helpers import print_label
from shipping.forms import *
from sokohaliAdmin.forms import *
import random, datetime
import hashlib





@csrf_exempt
#@ajax_request
def get_user_items(request, *args):
		 country = request.COOKIES.get('country', 'us')
		 items = get_cart_items(request)   #ShippingItem.objects.filter(user = request.user, shipment = None)
		 total_Value = 0
		 total_Value_N = 0
		 currency = country_currency_v1(country)
		 res = []
		 items_count = items.count()
		 if items_count > 0:
				 for i in items:
							 item_val = i.total_value
							 item_val_N = i.total_value_N
							 total_Value += item_val
							 total_Value_N += item_val_N
							 res.append({
										'id' : i.id,
										#'user_id' : i.user.user_id,
										#'full_name' : i.user.user.get_full_name(),
										'courier_tracking_number' : i.courier_tracking_number,
										#'vendor_name' : i.vendor_name,
										'description' : i.description,
										'quantity' : i.quantity,
										'total_value' : i.total_value,
										#'total_value_N': i.total_value_N,
										# 'invoice' : i.invoice,
										# 'filename': i.filename,
										# #'currency': country_currency_v1(country),
										# 'type': i.type,
							 })
		 return JsonResponse({'items':res, 'currency': currency, 'items_count': items_count,
						 'total_Value': total_Value, 'total_Value_N': total_Value_N}) 



def get_transc_no():
    numbers = "1234567890"
    alph = "abcdefghijklmnopqrstuvwxyz".upper()
    num_part_ref_no = ""
    alph_part_ref_no = ""
    transc_num_length = 5
    transc_alph_length = 5
    for i in range(transc_num_length):
        num_part_ref_no += numbers[random.randint(0, len(numbers)-1)]
    for j in range(transc_alph_length):
        alph_part_ref_no += alph[random.randint(0, len(alph)-1)]
    ref_no = num_part_ref_no + alph_part_ref_no
    return ref_no



@csrf_exempt
#@ajax_request
@login_required
def save_item_data(request, *args):
		 country = request.COOKIES.get('country', 'us')
		 print 'rP:',request.POST
		 #exchange_rate = country_exchange_rate(country, costcalc_settings())
		#  exchange_rate = marketingmember_costcalc(request).dollar_exchange_rate

		 shipping_origin        = request.session['shipping_origin']
		 shipping_destination   = request.session['shipping_destination']

		 """
				 save/upadte item data
		 """
		 # save each item to db
		# #print "obj"
		 try:
					#obj = json.loads(request.raw_post_data)
					obj = json.loads(request.body)

					item = obj['data']
					print item
					if ('id' in item.keys()):
							 itm = ShippingItem.objects.get(pk = item['id'])
							 itm.__dict__.update(item)
							 #if ('invoice' in item.keys()):
									 #itm.type = 'I'
							 itm.save()
					else:
							 #if ('invoice' in item.keys()):
									 #item_type.type = 'I'

							 itm = ShippingItem(user=request.user
											# cart_id = _cart_id(request),
											# type=item['type']
											#total_value_N = item['total_value_D'],
											#type='T',
											)
							 if ('description' in item.keys()):
										itm.description=item['description']
							 if ('courier_tracking_number' in item.keys()):
										itm.courier_tracking_number = item['courier_tracking_number']
							 else:
									itm.courier_tracking_number = "N/A"
							 if ('quantity' in item.keys()):
									 itm.quantity=item['quantity']
							 if ('vendor_name' in item.keys()):
									 itm.vendor_name=item['vendor_name']
							 if ('total_value' in item.keys()):
									 itm.total_value=item['total_value']#.strip(',').strip('$')
									 #total_value = item['total_value']
							 itm.country      = country
							 itm.origin       = shipping_origin
							 itm.destination  = shipping_destination
							 #itm.save()
							 itm.status = "Not yet received" # ItemStatus(status="Not yet received", item = itm)
							 itm.save()
					# update item data
					print "tracking_number_of_item:",itm.courier_tracking_number
					unordered_items =  ShippingItem.objects.filter(Q(user = request.user), Q(item_type="Regular"), ~Q(total_value = None))
				#   unordered_items.update(total_value_N = F('total_value') * exchange_rate)

					return JsonResponse({ 'data' : 'ok',
								 'id' : itm.id,'courier_tracking_number':itm.courier_tracking_number,
								 'type': 'itm.type'})
		 except Exception as e:
					#print e
					return JsonResponse({ 'data' : 'fail'})





@csrf_exempt
#@ajax_request
@login_required
def del_item_data(request, *args):
		 """
				 del item data
		 """
		 # save each item to db
		 try:
					obj = json.loads(request.body)
					id = obj['data']
					ShippingItem.objects.get(pk=id).delete()
		 except Exception as e:
					# #print e
					pass
		 return JsonResponse({'data': 'ok'})





def retrieve_modal_values(request):
		 if request.method == "POST":
					rp = request.POST
					print "rP:",rp
					print "WHaddress:",rp['WHaddress']
					#print 'retrieve_modal_values: rp: ',rp
					#if rp.has_key('import-options'): # implement import options modal form selections
					if rp.has_key('shipping_option'):
						#handling_option = rp['import-handling-option']
						handling_option = rp['shipping_option']
						if handling_option == "":
							messages.warning(request, "you have not selected any shipping option for your import, select one to proceed")
							return redirect(request.META['HTTP_REFERER'])
						else:
							request.session['handling_option']        =   handling_option

						request.session['shipping_origin']          =   rp['country_from']
						request.session['shipping_destination']     =   rp['country_to']
						request.session['WHaddress']                =   rp['WHaddress']

						# if rp.has_key('has_promo') and rp['has_promo'] != "":
						#   request.session['has_promo']  =  True
						#   request.session['promo_rate']  =   rp['has_promo']
						user = None
						if request.user.is_authenticated():
								user = request.user

						if handling_option  ==  "drop-at-postoffice":  #change option name to "I have the package with me"
							# print "current user ...", request.user
							# pickup_location, status = PickupLocation.objects.get_or_create(user = request.user, zip_code = rp['origin_zipcode'], telephone =rp['phone'],address1=rp['address1'], address2=rp['address2'], city = rp['city'],state= rp['state'],country=rp['country'] )
							#if request.user.is_authenticated():
								dropoffpostoffice, status = DropOffPostOffice.objects.get_or_create(user = user, zip_code = rp['po_zipcode'], telephone =rp['po_phone'],address_line1=rp['po_address1'], address_line2=rp['po_address2'], city = rp['po_city'],state= rp['po_state'],country=rp['po_country'])

								# if status == False and dropoffpostoffice.user != request.user: # checks if another user has same address
								#     dropoffpostoffice = DropOffPostOffice.objects.get_or_create(user = request.user, zip_code = rp['po_zipcode'], telephone =rp['po_phone'],address_line1=rp['po_address1'], address_line2=rp['po_address2'], city = rp['po_city'],state= rp['po_state'],country=rp['po_country'])
								# else:
								#     dropoffpostoffice.user = request.user
								#     dropoffpostoffice.save()
						#   else:
						#       dropoffpostoffice, status = DropOffPostOffice.objects.get_or_create(user = None, zip_code = rp['po_zipcode'], telephone =rp['po_phone'],address_line1=rp['po_address1'], address_line2=rp['po_address2'], city = rp['po_city'],state= rp['po_state'],country=rp['po_country'])

								request.session['drop-at-postoffice'] = dropoffpostoffice.pk
								return redirect(reverse('shipping:add_item_page'))

						elif handling_option == "pick-up-package":  #change option name to "I have the package with me"
							# print "current user ...", request.user
							# pickup_location, status = PickupLocation.objects.get_or_create(user = request.user, zip_code = rp['origin_zipcode'], telephone =rp['phone'],address1=rp['address1'], address2=rp['address2'], city = rp['city'],state= rp['state'],country=rp['country'] )
						#   user = None
						#   if request.user.is_authenticated():
						#       user = request.user
								pickup_location, status = PickupLocation.objects.get_or_create(user = user, zip_code = rp['pk_zipcode'], telephone =rp['pk_phone'],address_line1=rp['pk_address1'], address_line2=rp['pk_address2'], city = rp['pk_city'],state= rp['pk_state'],country=rp['pk_country'])

								# if status == False and pickup_location.user != request.user: # checks if another user has same address
								#   pickup_location = PickupLocation.objects.create(user = request.user, zip_code = rp['pk_zipcode'], telephone =rp['pk_phone'],address_line1=rp['pk_address1'], address_line2=rp['pk_address2'], city = rp['pk_city'],state= rp['pk_state'],country=rp['pk_country'])
								# else:
								#   pickup_location.user = request.user
								#   pickup_location.save()
						#   else:
						#     pickup_location, status = PickupLocation.objects.get_or_create(user = None, zip_code = rp['pk_zipcode'], telephone =rp['pk_phone'],address_line1=rp['pk_address1'], address_line2=rp['pk_address2'], city = rp['pk_city'],state= rp['pk_state'],country=rp['pk_country'])
								#pickup_location.user = None
								#pickup_location.save()

								request.session['pickup_location_key'] = pickup_location.pk
								return redirect(reverse('shipping:add_item_page'))

						elif handling_option == "drop-at-location":
							request.session['dropoff_location_id'] = rp.get('dropoff_location')
							return redirect(reverse('shipping:add_item_page'))

						elif handling_option == "send-from-shop": #default import option
							return redirect(reverse('shipping:add_item_page'))

		 return redirect('/')



@login_required
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None )
def package_information(request):

		 handling_option = None
		 template_name = 'shipping/review_cart.html'
		 try:
				pickup_location  = PickupLocation.objects.filter(pk = request.session.get('pickup_location_key',""))
		 except:
				pickup_location  = None
		 handling_option = request.session.get('handling_option',"")
		 request.session['pickup-location']  =  pickup_location
		 request.session['shipment_placed'] = False
		 if 'quantity' in request.session:
					request.session['quantity'] = ''
		 if 'error_alert' in request.session:
					request.session['error_alert'] = ''
		 if request.session.get('shipment_placed', False):
				 return redirect ("/shipping/")
		 return render(request, template_name, {'handling_option':handling_option})



def get_package_warehouses(request, origin, destination):
	mm = marketing_member(request)
	try:
		return mm.get_shipping_chain_route_warehouses(origin, destination)
	except Exception as e:
		print 'get_package_warehouses e: ',e
		return None





def save_uploaded_invoice(request, package):
		# print "trying to save uploaded invoices for ....", package
		if request.FILES:
			for invoice in request.FILES.getlist("pic"):
				ShippingPackageInvoice.objects.create(user=request.user, invoice=invoice, package = package)



def get_dropoff_location(request,marketing_member,country,state):
	''' if marketing member has multiple drop off location per state, get
	a list of all locations, checks nearest and return'''
	return marketing_member.destination_warehouse.drop_off_location.all().filter(country = country, state = state)
	# pass



@login_required
@csrf_exempt
def select_warehouse(request):
		 template_name = "shipping/select_warehouse_location.html"
		 items_count = get_cart_items(request).count()#  ShippingItem.objects.filter(user = request.user, shipment = None).count()
		 if items_count < 1:
					messages.info(request, "Empty cart! You should have at least one item in your cart before you proceed")
					return redirect (reverse("shipping:add_item_page"))
		 country = request.COOKIES.get('country', 'us')
		 if country == "":
					return redirect("/")
		 warehouses = WarehouseMember.objects.filter(active = True, country = country)
		 if request.method == "POST":
					if 'warehouse_id' in request.POST:
							 request.session["warehouse_id"] = request.POST["warehouse_id"]
							 response_data = {"result": "Warehouse location successfully selected. You can now proceed to the next page."}
							 return HttpResponse(json.dumps(response_data), content_type='application/json')
					return redirect(reverse("shipping:select_package"))
		 else:
					return render(request, template_name, {"warehouses": warehouses})




@login_required
def select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination):
		 template_name = "shipping/select_box_and_freight.html"
		 request.session['do_not_delete_all'] = False
		 country = request.COOKIES.get('country', 'us')
		 filtered_packages = get_packages(request)#[:1]
		 #boxes = PreDefinedBoxes.objects.all()
		 suggestedWeight_K          = round(suggestedWeight * lb_kg_factor, 2)
		 added_suggested_box        = request.session.get('suggested_box', False)
		 costcalc                   = marketingmember_costcalc(request,lb_country)
		 shippingWeight             = shipping_Weight(request)
		 shippingWeight_kg          = shippingWeight * lb_kg_factor
		 shipping_origin        = request.session.get('shipping_origin',"None")
		 shipping_destination   = request.session.get('shipping_destination',"None")

		 if shipping_origin == 'United States':
				 lb_country = shipping_destination
		 else:
				 lb_country = shipping_origin


		 localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
		 costPerLbAir, costPerLbSea, costPerLbExpress, exchange_rate, expressFreight, expressFreight_N = PackageCostCalc(request, shippingWeight, shippingWeight_kg, shipping_origin, shipping_destination, None, lb_country)


		 airFreight_val = airFreight_val_N = seaFreight_val = seaFreight_val_N = expressFreight_val = expressFreight_val_N = 0
		 for pkg in filtered_packages:
				 localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
				 cPerLbAir, cPerLbSea, cPerLbExpress, exchange_rate, expressFreight, expressFreight_N = PackageCostCalc(request, pkg.box_weight_higher(), pkg.box_weight_higher_K(), shipping_origin, shipping_destination, None, lb_country)

				 pkg.intl_freight_D = airFreight
				 pkg.intl_freight_N = airFreight_N
				 pkg.save()

				 airFreight_val     += airFreight
				 airFreight_val_N   += airFreight_N
				 seaFreight_val     += seaFreight
				 seaFreight_val_N   += seaFreight_N
				 expressFreight_val += expressFreight
				 expressFreight_val_N += expressFreight_N


		 response_dict.update({
														'airFreight': airFreight_val, 'airFreight_N': airFreight_val_N, 'seaFreight': seaFreight_val, 'seaFreight_N': seaFreight_val_N, 
														'expressFreight':expressFreight_val, 'expressFreight_N':expressFreight_val_N,
														'shippingWeight': shippingWeight, 'shippingWeight_kg': shippingWeight_kg, 
														#'totalUserShipmentWeight': totalUserShipmentWeight, 'totalUserShipmentWeight_kg': totalUserShipmentWeight_kg,
														'costPerLbAir': costPerLbAir, 'costPerLbSea': costPerLbSea, 'costPerLbExpress':costPerLbExpress,
														'suggestedWeight': suggestedWeight, 'suggestedWeight_K': suggestedWeight_K,
														'country': country, #'boxes': boxes,
														'lb_country':lb_country,
														'maxShippingWeight': shippingWeight, 'maxShippingWeight_kg': shippingWeight_kg,
														'officePickupInLag': 0, 'officePickupInLag_N': 0,
														'packages': filtered_packages, #'predefined_boxes': boxes,
														'filtered_packages': filtered_packages,
														'added_suggested_box': added_suggested_box, "is_promo_on": is_promo_on})
		 return render(request, template_name, response_dict)


def get_unordered_items(request):
	item_list = get_cart_items(request)
	return item_list



def get_local_freight_cost(request):
		shipping_origin = request.session.get('shipping_origin',"None")
		shipping_destination = request.session.get('shipping_destination',"None")

		if shipping_origin == 'United States':
				lb_country = shipping_destination
		else:
				lb_country = shipping_origin

		location_id    = request.GET.get('location_id')
		request.session['location_id'] = location_id
		shippingWeight = shipping_Weight(request)
		weight_kg = shippingWeight * 0.453592 #lb_kg_factor
		print 'get_local_freight_cost | weight_kg'
		location = LocalDistributorLocation.objects.get(pk = location_id)
		if location == None:
					return 0
		else:
					region = location.region
					local_freight_cost_D,  local_freight_cost_N = region_local_freight_costs(request, region, weight_kg,lb_country)
					return JsonResponse({'local_freight_cost_D': format_num(local_freight_cost_D), 'local_freight_cost_N': format_num(local_freight_cost_N)})


@login_required
@csrf_exempt
def select_package_size(request):
		 mm = marketing_member(request)

		 shipping_origin = request.session.get('shipping_origin',"None")
		 shipping_destination = request.session.get('shipping_destination',"None")

		 if shipping_origin == 'United States':
				 lb_country = shipping_destination
		 else:
				 lb_country = shipping_origin

		 print "ship origin - ship destination:", shipping_origin, shipping_destination

		 costcalc =  marketingmember_costcalc(request,lb_country)
		 exchange_rate = costcalc.dollar_exchange_rate

		 packages_created = False

		 try:
				 active_shipping_chain = marketing_member(request).get_shipping_chain_route(shipping_origin, shipping_destination)
		 except:
				 messages.warning(request, 'Please contact Customer Care for shipping from {} to {}'.format(shipping_origin, shipping_destination))
				 return redirect (reverse('shipping:add_item_page'))
		 #  get package warehouse
		 #package_warehouse = get_package_warehouses(request, shipping_origin, shipping_destination)
		 origin_warehouse, destination_warehouse = get_package_warehouses(request, shipping_origin, shipping_destination)


		 if origin_warehouse == None:
					msg = "No Warehouse found for %s in %s. Please contact Customer Care." %(mm.storefront_name.title(), shipping_origin.title())
					messages.warning(request, msg)
					return redirect (reverse('shipping:add_item_page'))
		 else:
				 #print 'origin_warehouse.zip_code: ',origin_warehouse.zip_code
				 request.session['package_warehouse'] = origin_warehouse

		 custom_package_created = False
		 unordered_user_item_list = get_unordered_items(request)
		 filtered_packages = get_packages(request)  #ShippingPackage.objects.filter(user = request.user, deleted = False)
		 form2 = AddCustomPackageForm()

		 #costcalc = costcalc_settings() # add request
		 # costcalc = marketer_costcalc_settings(request.marketing_member, request.session['shipping_origin']) # KEEP THIS FOR REFERENCE
		 lb_kg_factor                  = costcalc.lb_kg_factor
		 weightFactor                  = costcalc.dim_weight_factor
		 costcalc_is_promo_on          = costcalc.is_promo_on

		 is_promo_on = False
		 country = request.COOKIES.get('country', 'us')

		 if request.user.is_authenticated():
					items = get_cart_items(request) #ShippingItem.objects.filter(user = request.user, shipment = None, country = country)

					marketingmember = marketing_member(request)
					suggestedWeight, matchingKeywords_info = suggestedWeightAndInfo(items, costcalc, marketingmember, shipping_origin, shipping_destination)
					suggestedWeight_K = round(suggestedWeight * lb_kg_factor, 2)
		 else:
					#for anonymous users
					suggestedWeight, suggestedWeight_K, matchingKeywords_info = 0, 0 , ''

		 alert1 = 'You have already chosen Bill Me Later! To Select a Box or Enter Dimension, please clear your cart or refresh this page!'
		 additional_msg = 'Please select your delivery option and click proceed.'
		 form3 = BillMeLaterForm()
		 form4 = DeliveryMethodForm()
		 response_dict = {'costcalc':costcalc, 'active_service_chain':active_shipping_chain,'item_list':unordered_user_item_list, 'form2': form2, 'form3': form3, 'form4': form4,
												 "matchingKeywords_info": matchingKeywords_info,
												}
		 #office_pickup_locations = get_office_pickup_locations(request, shipping_origin, shipping_destination, shipping_destination)
		 office_pickup_locations = get_office_pickup_locations(request, shipping_origin, shipping_destination, 'destination')
		 print 'office_pickup_locations: ',office_pickup_locations

		 if office_pickup_locations == None:
			messages.error(request, "No office pick up location found for this member")
			#return redirect (reverse('shipping:select_package'))
		 else:
			response_dict.update({'office_pickup_locations':office_pickup_locations})

		 handling_option = request.session.get('handling_option',"send-from-shop")
		 response_dict.update({'handling_option':handling_option})
			#request.session['office_pickup_locations'] = office_pickup_locations
		 if request.method =="POST":
					if handling_option == "pick-up-package":
							pickup_location_id      =    request.session.get('pickup_location_key')
							pickup_location         =    get_object_or_404(PickupLocation, pk = pickup_location_id)
							pickup_location.user    =    request.user
							pickup_location.save()
							print 'pickup_location: ',pickup_location

					if handling_option == "drop-at-postoffice":
							drop_at_postoffice_id     = request.session.get('drop-at-postoffice')
							drop_at_postoffice        = get_object_or_404(DropOffPostOffice, pk = drop_at_postoffice_id)
							drop_at_postoffice.user   = request.user
							drop_at_postoffice.save()
							print 'drop_at_postoffice: ',drop_at_postoffice

					if handling_option == 'drop-at-location':
							drop_off_location = LocalDistributorLocation.objects.get(pk = request.session.get('dropoff_location_id'))

					print 'handling_option: ',handling_option
					if request.POST.has_key("suggestedbox") and request.POST["suggestedbox"] != "":
								if request.session.get("billmelater", False):
										request.session['quantity'] = ''
										messages.success(request, alert1)
										if request.user.is_authenticated():
												 return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, country, is_promo_on, shipping_origin, shipping_destination)
										return redirect ("/quick-estimate/select-package-size/")
								else:
										suggestboxWeight = float(request.POST["suggestedbox"])
										quantity = 1
										suggestedBox = ShippingPackage.objects.create(box_quantity = quantity, user = request.user,
																		box_length = 2, box_width = 2, box_height = 2,
																		box_weight_Actual = suggestboxWeight, box_weight_Actual_K = suggestboxWeight * float(lb_kg_factor),
																	 )
										#suggestedBox.number = get_packages(request).count() + 1 #ShippingPackage.objects.filter(user = request.user).count() + 1
										suggestedBox.origin_warehouse       = origin_warehouse
										suggestedBox.destination_warehouse  = destination_warehouse

										if handling_option == "pick-up-package":
												suggestedBox.pickup_location     = pickup_location

										if handling_option == "drop-at-postoffice":
												suggestedBox.dropoff_postoffice  = drop_at_postoffice

										if handling_option == 'drop-at-location':
												suggestedBox.drop_off_location = drop_off_location

										print 'handling_option: ',handling_option

										if handling_option in ['drop-at-postoffice', 'drop-at-location', 'pick-up-package']:
												pick_up_charge_D, pick_up_charge_N = calculate_pickup_charge(request, handling_option, suggestedBox, origin_warehouse)
												print 'pick_up_charge_D, pick_up_charge_N: ',pick_up_charge_D, pick_up_charge_N

												suggestedBox.pick_up_charge_D = pick_up_charge_D
												suggestedBox.pick_up_charge_N = pick_up_charge_N

										suggestedBox.save()

										# save uploaded invoice
										save_uploaded_invoice(request, suggestedBox)

										# assign import items to package
										item_shipping_chain = mm.get_shipping_chain_route(shipping_origin,shipping_destination)
										print "the chain: ",item_shipping_chain
										ShippingItem.objects.filter(pk__in = [item.pk for item in unordered_user_item_list]).update(package = suggestedBox,shipping_chain=item_shipping_chain, ordered=True)
										update_pkg_total_value(ShippingPackage, suggestedBox)

										# print 'handling_option: ',handling_option
										#
										# if handling_option in ['drop-at-postoffice', 'drop-at-location', 'pick-up-package']:
										#     pick_up_charge_D, pick_up_charge_N = calculate_pickup_charge(request, handling_option, suggestedBox, origin_warehouse)
										#     print 'pick_up_charge_D, pick_up_charge_N: ',pick_up_charge_D, pick_up_charge_N
										#
										#     suggestedBox.pick_up_charge_D = pick_up_charge_D
										#     suggestedBox.pick_up_charge_N = pick_up_charge_N


										#suggestedBox.save()

										# if handling_option == "pick-up-package" or handling_option == "export-import":
										#   suggestedBox.pickup_location = pickup_location
										#   suggestedBox.save()
										#   try:
										#     pick_up_charge_D = get_pickup_charge(request, suggestedBox, "usps")
										#     pick_up_charge_N = float(pick_up_charge_D) * float(exchange_rate)
										#     suggestedBox.pick_up_charge_D = pick_up_charge_D
										#     suggestedBox.pick_up_charge_N = pick_up_charge_N
										#     suggestedBox.save()
										#   except:
										#     pass

										request.session['boxadded'] = True
										request.session['billmelater'] = False
										request.session['suggested_box'] = True
										alert = 'Suggested weight added successfully. %s' %additional_msg
										messages.info(request, alert)
										return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)

				#   if request.POST.has_key("selectabox") and request.POST["selectabox"] != "":
				#        if request.session.get("billmelater", False):
				#             alert = 'You have already chosen Bill Me Later! To Select a Box or Enter Dimension, please clear your cart!'
				#             request.session['quantity'] = ''
				#             messages.error(request, alert)
				#             return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, country, is_promo_on, shipping_origin, shipping_destination)
				#        else:
				#             # box = PreDefinedBoxes.objects.get(pk = request.POST['selectabox'])
				#             # box.usage_count += 1
				#             # box.save()
				#             added_box = ShippingPackage()
				#             try:
				#                  box_quantity = int(request.POST.get('box_quantity', 1))
				#             except:
				#                  box_quantity = 1
				#             added_box.box_quantity = box_quantity
				#             quantity = float(box_quantity)
				#             if request.user.is_authenticated():
				#                  added_box.user           = request.user
				#             added_box.box_name       = box.box_name
				#             added_box.box_length     = box.box_length
				#             added_box.box_width      = box.box_width
				#             added_box.box_height     = box.box_height
				#             added_box.box_weight_Actual     = float(box.box_weight) * quantity
				#             added_box.box_weight_Actual_K   = float(box.box_weight) * quantity * lb_kg_factor
				#             #added_box.number         =  get_packages(request).count() + 1 #ShippingPackage.objects.filter().count() + 1
				#             added_box.origin_warehouse       =   origin_warehouse
				#             added_box.destination_warehouse  = destination_warehouse
					#
				#             if handling_option == "pick-up-package":
				#                 added_box.pickup_location     = pickup_location
					#
				#             if handling_option == "drop-at-postoffice":
				#                 added_box.dropoff_postoffice  = dropoff_postoffice
					#
				#             if handling_option == 'drop-at-location':
				#                 added_box.drop_off_location = drop_off_location
					#
				#             added_box.save()
				#             # assign import items to package
				#             ShippingItem.objects.filter(pk__in = [item.pk for item in unordered_user_item_list]).update(package = added_box)
				#             update_pkg_total_value(ShippingPackage, added_box)
				#             save_uploaded_invoice(request, added_box)
					#
				#             if handling_option ==   "pick-up-package" or handling_option == "drop-at-postoffice":
				#             #   added_box.pickup_location  =   pickup_location
				#             #   added_box.save()
					#
				#               pick_up_charge_D = get_pickup_charge(request, added_box, "usps")
				#               pick_up_charge_N = float(pick_up_charge_D) * float(exchange_rate)
				#               added_box.pick_up_charge_D = pick_up_charge_D
				#               added_box.pick_up_charge_N = pick_up_charge_N
				#               added_box.save()
					#
				#             request.session['boxadded'] = True
				#             request.session['billmelater'] = False
				#             request.session['quantity'] = quantity
					#
				#             alert = '%s box added successfully. Please select your delivery option and click proceed.' %box_quantity
				#             messages.info(request, alert)
				#             return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, country, is_promo_on, shipping_origin, shipping_destination)

					if "enterdimension" in request.POST:
							 if request.session.get("billmelater", False):
										alert = 'You have already chosen Bill Me Later! To Select a Box or Enter Dimension, please clear your cart!'
										messages.info(request, alert)
										request.session['quantity'] = ''
										return redirect (request.META.get("HTTP_REFERER", "/"))
							 else:
										selected_items = request.POST.getlist('selected_item')
										print "selected_items: ", selected_items
										form2 = AddCustomPackageForm
										form2 = AddCustomPackageForm(request.POST)
										if form2.is_valid():
												 added_box = form2.save(commit=False)
												 if request.user.is_authenticated():
															added_box.user      = request.user
												 quantity = 1
												 dim_weight = quantity * (float(form2.cleaned_data['box_length']) * float(form2.cleaned_data['box_width']) * float(form2.cleaned_data['box_height'])/ weightFactor)
												 entered_weight  = float(form2.cleaned_data['box_weight_Actual'])
												 weight_unit = request.POST["weight_unit"]
												 added_box.box_weight_Dim = dim_weight #* quantity
												 added_box.box_weight_Dim_K = dim_weight * lb_kg_factor #* quantity

												 if weight_unit == "lbs":
															added_box.box_weight_Actual = entered_weight * quantity # multiply weight in lb by quantity
															added_box.box_weight_Actual_K = entered_weight * lb_kg_factor * quantity
												 else:
															added_box.box_weight_Actual = entered_weight * 2.20462 * quantity # convert weight from kg to lb
															added_box.box_weight_Actual_K = entered_weight * quantity

												 added_box.origin_warehouse       = origin_warehouse
												 added_box.destination_warehouse  = destination_warehouse

												 if handling_option == "pick-up-package":
														 added_box.pickup_location     = pickup_location

												 if handling_option == "drop-at-postoffice":
														 added_box.dropoff_postoffice  = drop_at_postoffice

												 if handling_option == 'drop-at-location':
														 added_box.drop_off_location = drop_off_location

												 if handling_option in ['drop-at-postoffice', 'drop-at-location', 'pick-up-package']:
														 pick_up_charge_D, pick_up_charge_N = calculate_pickup_charge(request, handling_option, added_box, origin_warehouse)
														 print 'pick_up_charge_D, pick_up_charge_N: ',pick_up_charge_D, pick_up_charge_N

														 added_box.pick_up_charge_D = pick_up_charge_D
														 added_box.pick_up_charge_N = pick_up_charge_N

												 added_box.save()

												 # add items to package
												 item_shipping_chain = mm.get_shipping_chain_route(shipping_origin,shipping_destination)
												 ShippingItem.objects.filter(pk__in = selected_items).update(package = added_box, shipping_chain=item_shipping_chain, ordered=True)
												 update_pkg_total_value(ShippingPackage, added_box)

												#  if handling_option in ['drop-at-postoffice', 'drop-at-location', 'pick-up-package']:
												#      pick_up_charge_D, pick_up_charge_N = calculate_pickup_charge(request, handling_option, added_box, origin_warehouse)
												#      print 'pick_up_charge_D, pick_up_charge_N: ',pick_up_charge_D, pick_up_charge_N
												 #
												#      added_box.pick_up_charge_D = pick_up_charge_D
												#      added_box.pick_up_charge_N = pick_up_charge_N



												 # added_box.pickup_location   = pickup_location
												 #added_box.save()

													# create package nvoice
												 save_uploaded_invoice(request, added_box)
												 response_dict.update({'custom_box_created': True})
												 # custom_package_created = True
												 print "length: ",len(unordered_user_item_list)
												 if len(unordered_user_item_list) > 0:
													messages.error(request, "You still have " +  str(len(unordered_user_item_list)) +  " item(s) yet to be added to a box.Use the 'Create Custom Box' tab to create one or more boxes for these items.")
												 else:
													messages.success(request, "You have successfully created boxes for all your items. Select delivery method below")
													response_dict.update({'all_packages_created':True})
												#   if handling_option          ==  "pick-up-package" or handling_option == "export-import":
												#     for pkg in get_packages(request):
												#       pkg.pickup_location  = pickup_location # save pick up location
												#       # pkg.save()
												#       try:
												#         pick_up_charge_D = get_pickup_charge(request, pkg, "usps")
													#
												#         pick_up_charge_N = float(pick_up_charge_D) * float(exchange_rate)
												#         pkg.pick_up_charge_D =  pick_up_charge_D
												#         pkg.pick_up_charge_N =  pick_up_charge_N
												#         pkg.save()
												#       except:
												#         msg = "Could not fetch pick up charge at the moment, please go back to the previous page and try again"
												#         messages.error(request,msg)
												 request.session['boxadded'] = True
												 request.session['billmelater'] = False
												 request.session['quantity'] = int(quantity)
												 return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)
										else:
												 if request.session.has_key('quantity'):
															del request.session['quantity']
												 if request.session.has_key('error_alert'):
															del request.session['error_alert']

												 form_errors_dict = form_errors(form2.errors())
												 for k,v in form_errors_dict.iteritems():
														##print k, v
														messages.error(request, "%s - %s" %(k, v))
												 response_dict.update({'form2': form2})
												 return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)

					if "accept_do_later" in request.POST:
							 if request.session.get('boxadded', False):
										messages.error(request, 'You have already added 1 or more boxes! To use let us do it for you later, please clear all your packages or refresh this page!')
										request.session['quantity'] = ''
										return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)
							 else:
										# accepted bill me later, set all values to 0.0
										added_box = ShippingPackage()
										added_box.box_quantity = 1
										if request.user.is_authenticated():
												added_box.user           = request.user
												# added_box.cart_id        = _cart_id(request)
												added_box.box_name       = "do it later"
												added_box.box_length     = 0.0
												added_box.box_width      = 0.0
												added_box.box_height     = 0.0
												added_box.box_weight_Actual     = 0.0
												added_box.box_weight_Actual_K   = 0.0
												#added_box.number         =  get_packages(request).count() + 1 #ShippingPackage.objects.filter().count() + 1

												added_box.origin_warehouse       = origin_warehouse
												added_box.destination_warehouse  = destination_warehouse

												if handling_option == "pick-up-package":
														added_box.pickup_location     = pickup_location

												if handling_option == "drop-at-postoffice":
														added_box.dropoff_postoffice  = drop_at_postoffice

												if handling_option == 'drop-at-location':
														added_box.drop_off_location = drop_off_location

												added_box.save()
												# assign import items to package

												item_shipping_chain = mm.get_shipping_chain_route(shipping_origin,shipping_destination)
												ShippingItem.objects.filter(pk__in = [item.pk for item in unordered_user_item_list]).update(package = added_box, shipping_chain=item_shipping_chain, ordered=True)
												update_pkg_total_value(ShippingPackage, added_box)
												save_uploaded_invoice(request, added_box)

												# if handling_option       ==   "pick-up-package" or handling_option == "export-import":
												#   added_box.pickup_location  =   pickup_location
												#   added_box.save()
												#   added_box.pick_up_charge_D = 0.0
												#   added_box.pick_up_charge_N = 0.0
												#   added_box.save()

										request.session['let_us_do_it_for_you_later'] = True
										request.session['billmelater']     = True
										request.session['boxadded']        = False
										request.session['quantity'] = ''
										messages.info(request, 'You have successfully chosen let us do it for you later. Please select your delivery option and click proceed.')
										response_dict.update({"accept_do_later": True})
										return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)

					if request.user.is_authenticated():
							 if "proceed" in request.POST:
										if (not request.session.get('boxadded', False) and not request.session.get('billmelater', False)) and filtered_packages.count() < 1:
												 request.session['error_alert'] = 'Please add one or more boxes or choose Let Us Do It For You Later before you proceed!'
												 request.session['quantity'] = ''
												 return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)
										if request.method == 'POST':
												 packages = get_packages(request)
												 form = DeliveryMethodForm()
												 form = DeliveryMethodForm(request.POST)
												 if form.is_valid():
															dvm = form.cleaned_data["delivery_method"]
															request.session['dvm'] = dvm
															if dvm not in ['AF - HD', 'SF - HD', 'EX - HD']: # if office pickup is selected
																	 print 'dvm: ',dvm
																	 selected_pickup_location = LocalDistributorLocation.objects.get(pk = request.POST['location_id'])
																	 #pickup_state = selected_pickup_location.state
																	 packages = get_packages(request)
																	 packages.update(local_pickup_address = selected_pickup_location, handling_option = request.session.get('handling_option',""), delivery_method = "Office pickup", shipping_method = dvm)
																#    delivery_intl_freight_D, delivery_local_freight_D, delivery_total_freight_D  = get_freight_costs(request, pkg, origin, destination)
																#    delivery_zone = request.POST.get("delivery_zone")
																#    delivery_city = request.POST.get("delivery_city")
																	 request.session['selected_delivery_method'] = dvm
																	 request.session['delivery_method'] = 'chosen'
																	 request.session['dm'] = True
																	 request.session['selected_pickup_location'] = selected_pickup_location
																	 request.session['package_destination']      = True
																	 return redirect (reverse('shipping:shipping_payment'))
															else:
																	 return redirect(reverse("shipping:shipping_address"))
												 else:
															request.session['error_alert'] = 'Please select one of the delivery options before you proceed.'#'Please add 1 or more boxes or choose Let Us Do It For You Later before you proceed.'
															request.session['quantity'] = ''
															return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)

		 if request.session.get('do_not_delete_all', False):
					return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)
		 else:
					keys_to_del = ['quantity', 'error_alert', 'boxadded', 'suggested_box', 'billmelater']
					for key in keys_to_del:
							if request.session.has_key(key):
									del request.session[key]
					ShippingItem.objects.filter(Q(user = request.user), ~Q(package = None), Q(ordered = False), Q(item_type="Regular")).update(package = None)
					packages = ShippingPackage.objects.filter(Q(user = request.user), Q(ordered = False))#.delete()
					for pkg in packages:
						ShippingPackageInvoice.objects.filter(package = pkg).delete()
						pkg.delete()
					#DeliveryAddress.objects.filter(user = request.user, shippingpackage = None).delete()
					return select_box_response(request, response_dict, suggestedWeight, lb_kg_factor, lb_country, is_promo_on, shipping_origin, shipping_destination)



@login_required
#@user_passes_test(staff_check_for_booking, login_url=None, redirect_field_name='/admin/my-account/')
#@user_passes_test(address_activated, login_url=None, redirect_field_name='/shipping/')
#@user_passes_test(flagged_check, login_url='/bank-deposit-verification/', redirect_field_name = None)
def select_shipping_address(request):
		shipping_origin         = request.session.get('shipping_origin', '')
		shipping_destination    = request.session.get('shipping_destination', '')

		if shipping_origin == 'United States':
				lb_country = shipping_destination
		else:
				lb_country = shipping_origin

		#regions = world_geo_data.Region.objects.filter(country__name = shipping_destination).values_list('name', 'name')
		#print 'regions: ',regions
		regions = fetch_country_regions(shipping_destination)

		packages = get_packages(request)
		 #template_name = "client/send-to.html"
		template_name = "shipping/select_shipping_address.html"

		country_list_choice = ((shipping_destination, shipping_destination),)
		form = AddressBookForm(country = country_list_choice, states = regions)

		if request.method == "POST":
				if "add_address" in request.POST.values():
						##print request.POST
						#form = AddressBookForm()
						action = request.POST['action']
						if action == 'add_address':
								form = AddressBookForm(request.POST, country = country_list_choice, states = regions)
						else:
								address_id = action.split('|')[1]
								address = AddressBook.objects.get(pk = address_id)
								form = AddressBookForm(request.POST, instance=address, country = country_list_choice, states = regions)

						if form.is_valid():
								#form.save()
								address = form.save(commit=False)
								address.user      = request.user
								#address.first_name = request.POST["full_name"].split(" ")[0]
								#address.last_name = request.POST["full_name"].split(" ")[1]
								address.save()
								return JsonResponse({'result': 'Ok'})
						print form.errors
						return JsonResponse({'result': 'fail'})


		if "edit_address" in request.GET:
				address_id = request.GET['id']
				address = AddressBook.objects.get(pk = address_id)
				#form = EditAddressBookForm()
				# form = EditAddressBookForm(request.POST, instance=address)
				# if form.is_valid():
				#      #form.save()
				#      address = form.save(commit=False)
				#      address.save()
				#      messages.info(request, "Address successfully edited")
				#      return HttpResponseRedirect("/shipping/shipping-address/send-to/")
				form = AddressBookForm(instance=address, country = country_list_choice, states = regions)
				return render(request, "shipping_snippet/add_address.html", {"form": form, 'action': 'edit_address|%s' %address_id})

		if "delete_address" in request.GET:
				address_id = request.GET['id']
				address = get_object_or_404(AddressBook, pk = address_id)
				address.delete()
				return JsonResponse({'result': 'Ok'})

		if 'select_address' in request.GET:
				address_id = request.GET['address_id']
				request.session['selected_home_address'] = address_id

				address = AddressBook.objects.get(pk = address_id)
				# print "address:",address
				delivery_address = DeliveryAddress()

				#country = request.COOKIES.get('country', 'us')
				shippingWeight = shipping_Weight(request)
				#pickup_state = address.state
				#weight_kg = shippingWeight * 0.453592 #lb_kg_factor

				costcalc =  marketingmember_costcalc(request,lb_country)

				''' update deliveryAddress '''
				for field in address._meta.fields:
					setattr(delivery_address, field.name, getattr(address, field.name))
					delivery_address.id = None
					delivery_address.save()
					packages.update(delivery_address = delivery_address, handling_option = request.session.get('handling_option',""), delivery_method = "Home delivery")


				return JsonResponse({'result': 'Shipping Destination successfully selected. Please proceed to the next page.'})
				# costcalc                  = marketingmember_costcalc(request)
				#
				# packages = get_packages(request)
				# delivery_intl_freight_D, delivery_local_freight_D, delivery_total_freight_D  = get_freight_costs(request, packages, shipping_origin, shipping_destination, costcalc)
				#
				# total_freight_D = delivery_total_freight_D
				#
				# return JsonResponse({'result': 'Shipping Cost to your destination is $%s. You can now proceed to the next page.' %format_num(total_freight_D)})

		addresses = get_customer_addresses(request, shipping_destination)
		return render(request, template_name, {"form": form,"addresses": addresses})








def print_usps_label(request, packages, pick_up_address, action):
	print "connecting to label printing API . . ."
	counter = 0
	for pkg in packages:
		counter += 1
		if request.session.get('handling_option', "")  == "pick-up-package" or  request.session.get('handling_option',"") == "drop-at-postoffice" or action == "requery":
			try:
				print "print_usps_label | generating label: ", counter
				label   =   print_label(request, pkg, packages.count(), pick_up_address, counter)
				label_obj = CourierLabel.objects.create(package = pkg, tracking_id = pkg.tracking_number, label = label)

				# pkg.usps_label = label_obj
				# pkg.save()
			except Exception as e:
				msg =  "Can't print label at this time, please try again because: " + str(e)
				messages.error(request, msg)
				print "Error" , e
			





@login_required
@csrf_exempt
def payment_page(request):

		 template_name = 'shipping/package_review.html'
		 #country = request.COOKIES.get('country', 'us')
		 shipping_origin = request.session.get('shipping_origin',"None")
		 shipping_destination = request.session.get('shipping_destination',"None")

		 if shipping_origin == 'United States':
				lb_country = shipping_destination
		 elif request.POST.has_key('select_currency'):
				 print "no"
				 lb_country = shipping_destination
		 else:
				 lb_country = shipping_origin

		 request.session['lb_country'] = lb_country

		 marketingmember                = marketing_member(request)
		 cost_calc                      = marketingmember_costcalc(request,lb_country)
		 #  shipping_origin                = request.session.get('shipping_origin',"None")
		 #  shipping_destination           = request.session.get('shipping_destination',"None")
		 weightFactor                   = cost_calc.dim_weight_factor
		 lb_kg_factor                   = cost_calc.lb_kg_factor
		 pick_up_charge_D               = 0.0
		 pick_up_charge_N               = 0.0
		 exchange_rate                  = 1
		 jejepay_credit_N, jejepay_credit_D = account_standing(request, request.user)

		 pkg_count                = get_packages(request).aggregate(quantity_count=Sum(F('box_quantity')))['quantity_count']
		 item_count               = get_cart_items(request).count()
		 shippingWeight           = shipping_Weight(request)
		 cart_value               = cartWorth(request)
		 total_freight_D          = request.session.get('delivery_total_freight_D', 0.0)
		 intl_freight_D           = request.session.get('delivery_intl_freight_D', 0.0)
		 local_freight_D          = request.session.get('delivery_local_freight_D',0.0)

		 packages                 = get_packages(request)
		 #store package IDs in session
		 package_ids  = [pkg.pk for pkg in packages]
		 request.session['package_ids'] = package_ids


		 #if not request.session.has_key('import_packages'):
		#      request.session['import_packages'] = packages


		 #shipping_origin        = request.session.get('shipping_origin',"None")
		 #shipping_destination   = request.session.get('shipping_destination',"None")
		 handling_option        = request.session.get('handling_option')
		 #print 'handling_option: ',handling_option

		 freight_VAT_SC_D = PSDG_D = VAT_D = coverage_amount_D = 0

		 for pkg in packages:

				 localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
				 costPerLbAir, costPerLbSea, costPerLbExpress, exchange_rate, expressFreight, expressFreight_N  = PackageCostCalc(request, pkg.box_weight_higher(), pkg.box_weight_higher_K(), shipping_origin, shipping_destination, None,lb_country)
 

				 if pkg.local_pickup_address:
						 print 'pkg.local_pickup_address: ',pkg.local_pickup_address
						 local_freight_cost_D, local_freight_cost_N = get_local_freight_from_state(request, pkg.box_weight_higher(), pkg.local_pickup_address.id)
						 pkg.local_freight_D = local_freight_cost_D
						 pkg.local_freight_N = local_freight_cost_N

						 total_freight_D                    = local_freight_cost_D + airFreight
						 items_total_value_D                = pkg.shippingitem_set.all().aggregate(value = Sum('total_value'))['value']


				 dvm = request.session['dvm']
				 pkg_shipping_method = dvm

				 pkg.shipping_chain = marketingmember.get_shipping_chain_route(shipping_origin,shipping_destination)

				 if 'AF' in pkg_shipping_method:
						pkg.shipping_method = "Air Freight"
						pkg.intl_freight_D = airFreight
						pkg.intl_freight_N = airFreight_N
				 elif 'SF' in pkg_shipping_method:
						pkg.shipping_method = "Sea Freight"
						pkg.intl_freight_D = seaFreight
						pkg.intl_freight_N = seaFreight_N
				 else:
						pkg.shipping_method = "Express"
						pkg.intl_freight_D = expressFreight
						pkg.intl_freight_N = expressFreight_N
				 #print 'dvm: ',dvm
				 if 'HD' in dvm:

				 		if pkg.shipping_chain.origin_distributor == None:
				 		 	local_freight_D = local_freight_N = 0.0

				 		else:
							 #pick_up_charge_D, pick_up_charge_N = calculate_pickup_charge(request, handling_option, pkg, pkg.warehouse)
							 #print 'pick_up_charge_D, pick_up_charge_N: ',pick_up_charge_D, pick_up_charge_N
							 local_freight_D, local_freight_N = calculate_last_mile_charges(request, pkg, shipping_origin, shipping_destination, 'destination')
							 print 'local_freight_D, local_freight_N: ', local_freight_D, local_freight_N
							 pkg.local_freight_D = float(local_freight_D)
							 pkg.local_freight_N = float(local_freight_N)


				 pkg_count                = pkg.box_quantity
				 #item_count               = get_cart_items(request).count()
				 linked_items             = pkg.shippingitem_set.all()
				 print "items", linked_items
				 item_count               = linked_items.count()
				 #shippingWeight           = shipping_Weight(request)
				 shippingweight           = pkg.box_weight_higher()
				 #cart_value               = cartWorth(request)
				 cart_value               = linked_items.aggregate(value = Sum('total_value'))['value']
				 print "cart_value: ",cart_value
				 # print "shippingweight: ", shippingweight
				 #intl_freight_D           = pkg.intl_freight_D
				 #local_freight_D          = pkg.local_freight_D

				 total_freight_D          = pkg.intl_freight_D + pkg.local_freight_D

				 #shipment_info = {}
				 pkg_info = {'pkg_count': pkg_count, 'item_count': item_count,
									 'shippingWeight': shippingweight, 'cart_value': cart_value, 'total_freight_D': total_freight_D}
												#'intl_freight_D': intl_freight_D, 'local_freight_D': local_freight_D})
				 #print "TV", pkg_info['cart_value']

				 total_freight_D_val, VAT_D_val, totalServiceCharge_D_val, \
				 CON_D_val, PSDG_D_val, SMP_D_val, freight_VAT_SC_D_val, coverage_amount_D_val, exchange_rate = CreateShipmentCostCalc(request, pkg_info, lb_country)

				 freight_VAT_SC_D   += freight_VAT_SC_D_val
				 PSDG_D             += PSDG_D_val
				 VAT_D              += VAT_D_val
				 coverage_amount_D  += coverage_amount_D_val

				 pkg.insurance_fee_D = PSDG_D_val
				 pkg.insurance_fee_N = PSDG_D_val * exchange_rate

				 pkg.VAT_charge_D = VAT_D_val
				 pkg.VAT_charge_N = VAT_D_val * exchange_rate

				 pkg.service_charge_D = totalServiceCharge_D_val
				 pkg.service_charge_N = totalServiceCharge_D_val * exchange_rate

				 total_payable_val_D = freight_VAT_SC_D_val + pkg.pick_up_charge_D
				 pkg.admin_total_payable_D = pkg.user_total_payable_D = total_payable_val_D
				 pkg.admin_total_payable_N = pkg.user_total_payable_N = total_payable_val_D * exchange_rate
				 if handling_option == "send-from-shop":
					origin_address = WarehouseLocation.objects.get(id = request.session.get('WHaddress'))
					pkg.default_origin_address = origin_address.full_address()
				 pkg.save()


		 # print 'freight_VAT_SC_D total: ',freight_VAT_SC_D
		 dollar_exchange_rate = cost_calc.dollar_exchange_rate

		 freight_VAT_SC_N  = freight_VAT_SC_D * dollar_exchange_rate
		 PSDG_N            = PSDG_D * dollar_exchange_rate
		 VAT_N             = VAT_D * dollar_exchange_rate
		 coverage_amount_N = coverage_amount_D * dollar_exchange_rate

		 if request.session['handling_option'] in["pick-up-package" or "drop-at-postoffice"]: # get usps pick up charge using origin and destination zip code
				 pick_up_charge_D =  packages.aggregate(Sum('pick_up_charge_D'))['pick_up_charge_D__sum']  #get_pickup_charge(request, get_packages(request), "usps")
				# pick_up_charge_D =  request.session['pick_up_charge_D']  #get_pickup_charge(request, get_packages(request), "usps")
				 if pick_up_charge_D == None:
						pick_up_charge_D = 0.0
						pick_up_charge_N = 0.0
				 else:
						pick_up_charge_N = pick_up_charge_D * dollar_exchange_rate
		 else:
				 pick_up_charge_D = 0.0
				 pick_up_charge_N = 0.0

		 #print 'pick_up_charge_D: ',pick_up_charge_D
		#  except Exception as e:
		#     print e
		#     pass


		 if request.method == "POST" or (request.GET.has_key("tx") and request.GET.has_key("st")) or (request.GET.has_key('status') and request.GET.has_key('ref_no')) or request.GET.has_key('trxref') or request.GET.get('resp'):

					'''check if POST is not coming from Flutterwave or PayPal'''
					if not request.GET.has_key('trxref') and not request.GET.has_key('resp') and not request.GET.has_key("st"):

							 #keep user selected options in memory
							 '''keeping request.POST for subsequent actions'''
							 request.session['requestPOST'] = request.POST
							 print 'request.POST 1: ',request.POST

					requestPOST = request.session['requestPOST']
					print 'request.POST 2: ',requestPOST

					form = paymentTypeForm(requestPOST)

					if form.is_valid():
							 print 'form is valid'
							 if request.session.has_key('requestPOST'):
										if request.session.has_key("selected_home_address"):
												chosen_address   = AddressBook.objects.get(pk = request.session['selected_home_address'])
												delivery_address = DeliveryAddress()
												for field in chosen_address._meta.fields:
													setattr(delivery_address, field.name, getattr(chosen_address, field.name))
												delivery_address.id = None
												delivery_address.save()
												get_packages(request).update(destination_address = delivery_address, handling_option = request.session.get('handling_option',"send-from-shop"),delivery_method = "home_delivery")
										elif request.session.has_key("selected_pickup_location"):
												get_packages(request).update(handling_option = request.session.get('handling_option',"send-from-shop"),delivery_method = "office_pickup",local_pickup_address = request.session['selected_pickup_location'])

						#    if request.session['handling_option'] == ("pick-up-package" or "drop-at-postoffice"):
						#         pickup_location = get_object_or_404(PickupLocation, pk = request.session['pickup_location_key'])
						#         packages.update(pickup_location = pickup_location)

							 user_total_payable_D = freight_VAT_SC_D + PSDG_D
							 user_total_payable_N = user_total_payable_D * exchange_rate

							 payment_type = requestPOST['payment_type']
							 print "payment_type: ",payment_type

							 #if request.session['handling_option'] == "pick-up-package" or request.session['handling_option'] == "export-import":
							 if pick_up_charge_D > 0:
								 user_total_payable_D += pick_up_charge_D
								 user_total_payable_N = user_total_payable_D * exchange_rate

								 if request.session['handling_option'] == "pick-up-package":
										pickup_location = get_object_or_404(PickupLocation, pk = request.session['pickup_location_key'])
										packages.update(pickup_location = pickup_location)

								 if request.session['handling_option'] == "drop-at-postoffice":
										dropoff_postoffice = get_object_or_404(DropOffPostOffice, pk = request.session['drop-at-postoffice'])
										packages.update(dropoff_postoffice = dropoff_postoffice)

							 insure = False
							 if requestPOST.has_key('insure'):
										insure = True
							 else:
										# user_total_payable_D -= PSDG_D
										# user_total_payable_N = user_total_payable_D * exchange_rate
										# user_total_payable_D += PSDG_D
										# user_total_payable_N = user_total_payable_D * exchange_rate
										user_total_payable_D -= PSDG_D
										user_total_payable_N = user_total_payable_D * exchange_rate
							 '''Pay with Flutterwave'''
							 if payment_type == 'Card Payment' and not request.GET.has_key('resp'):
							 			 print "this is where i started"
										 dest_namespace_1 = 'shipping:shipping_payment'
										 kwargs_dict      = {'actual_amount_D': user_total_payable_D, 'dest_namespace_1': dest_namespace_1, 'lb_country':lb_country,
																				'dest_namespace_2': None, 'txn_desc': 'Payment Confirmation',
																				'Flutterwave':'Flutterwave'}
										 try:
												 response_dict = card_payment(request, **kwargs_dict)
												 print 'card_payment|response_dict: ',response_dict
												 try:
														 pay_response = ast.literal_eval(response_dict.content)
														 print "pay respone obj: ", pay_response
														 if pay_response.has_key('pkg_placement'):
																 pay_response_msg = pay_response['response_msg']
																 jejepay_ref = pay_response['jejepay_ref']
														 else:
																return response_dict
												 except Exception as e:
														 print 'card_payment inner|e: ',e
														 return response_dict
										 except Exception as e:
												 print 'card_payment|e: ',e
												 pass


							 #send customer to go and pay at Paypal only if user is not coming from Paypal
							 if payment_type == 'PP' and not request.GET.has_key("tx"):
										# site_redirect_url = "http://jsa-test.elasticbeanstalk.com/client/payment_page"
										# site_redirect_url = "http://127.0.0.1:8000/confirm_ebiz_payment/"
										# order_number = get_transc_no()
										# receiver_mail = 'info@sokohali.com'
										# #final_total_cost_of_order = final_cost_of_order
										# command = "sale"
										# final_total = str(round(user_total_payable_D * (102.9/100), 2)) #amount + 2.9% charge
										# # print 'final_total: ',final_total
										# seed = get_transc_no()
										# invoice = get_transc_no()
										# # print 'invoice: ',invoice
										# source_key = "_W6qzSmCe4EoD468RI3wmrC6mw9nvLB2"					
										# pin = "sG8CIz"
										# # print 'seed: ',seed
										# hashedData = command + ":" + pin + ":" + final_total + ":" + invoice + ":" + seed				
										# # hashedValue = hashlib.md5(hashedData).hexdigest()
										# ebizhashedValue = "s/%s/%s/y" %(seed, hashlib.sha1(hashedData).hexdigest())					
										# # ebizhashedValue = "m" + "/" + seed + "/" + hashedValue +  "/"
										# # print "ebiz hash value", ebizhashedValue
										# kwargs = {"ebizHash": ebizhashedValue, "site_redirect_url":site_redirect_url,
										# "receiver_mail":receiver_mail,"ebiz":'ebizCharge',"final_total":final_total,
										# "order_id":order_number, 'invoice': invoice}				
										# return payment_option_api(request,**kwargs)
										# print 'i got here'

										request.session['pay_for_booking'] = 'pay_for_booking'
										request.session.modified = True
										return_url     = PAYPAL_RETURN_URL
										receiver_mail  = PAYPAL_RECEIVER_EMAIL
										markedup_amount = round(user_total_payable_D * (102.9/100), 2) #amount + 2.9% charge
										kwargs = {'actual_amount': user_total_payable_D, 'markedup_amount': markedup_amount, 'site_redirect_url': return_url, 'receiver_mail': receiver_mail, 'PayPal':'PayPal','Shipping':'Shipping'}
										return initialize_paypal_payment(request, **kwargs)

							 '''For intl cards'''
							 if request.GET.has_key('resp'):
										print "I got back from flutterwave"
										#pay_response =  ast.literal_eval(request.GET.get('resp'))
										#data = request.GET.get('resp')
										pay_response = str(request.GET.get('resp'))
										jejepay_ref = request.GET.get('jejepay_ref')
										#jejepay_ref = pay_response['merchtransactionreference']
										#pay_response_msg = pay_response['responsemessage']
										pay_response_msg = pay_response
										print pay_response_msg
										print type(pay_response_msg)
										#if pay_response_msg != "Approved" or pay_response_msg != "Successful":
										if pay_response_msg != "success":							
												#messages.error(request, pay_response_msg)
											print "Am going home"
											#tranx_id = pay_response['merchtransactionreference']
											tranx_id = jejepay_ref
											for pkg in packages:
												print "PKG:",pkg.tracking_number
												payment = MarketerPayment.objects.create(user=request.user.useraccount,payment_channel='Card Payment',created_at=timezone.now(),ref_no=jejepay_ref,
													amount=pkg.user_total_payable_D,package=pkg,marketer=marketingmember,status=pay_response_msg,payment_gateway_tranx_id =tranx_id)
												payment.save()
											messages.error(request, "The payment" + pay_response_msg)
											return redirect (reverse('shipping:shipping_payment'))

							 ''' Pay with shipping credit '''
							 if payment_type == "Shipping Credit":
										if jejepay_credit_D < user_total_payable_D: #import_shipment.admin_total_payable_N:
												 messages.error(request, "Insufficient Soko-Pay balance! Your Soko-Pay Balance of %s Dollar is less than the current total payable for this shipment." %format_num(jejepay_credit_D))
												 messages.error(request, "Please fund your Soko-Pay Wallet or use a different payment option.")
												 return redirect (request.META.get("HTTP_REFERER", reverse('shipping:shipping_payment')))


							 if request.session.has_key('requestPOST'):
										for pkg in packages:
												 if insure == True:
													pkg.insure = True
												 else:
													pkg.insurance_fee_D = 0
													pkg.insurance_fee_N = 0
												 #costcalc_obj = create_obj_costcalc(pkg)
												 costcalc_obj = create_obj_costcalc(request,lb_country)

												 # def __init__(self, marketing_member, origin, destination, prefix, char_length):
												 update_pkg_values(marketingmember,shipping_origin,shipping_destination, pkg, costcalc_obj, 'IM', ShippingPackage, insure, payment_type)

							 if payment_type == "Shipping Credit":
										for pkg in packages:
												 apply_shipping_credit(request, pkg)

							 counter = 0
							 label_ids = []
							 for pkg in packages:
									 '''Create ActionHistory record'''
									 print "user",request.user
									 pkg_status_list(pkg.pk, "ShippingPackage", request.user, "New")
									 print 'creating action history record'

									 counter += 1
									 if request.session['handling_option'] in ["pick-up-package", "drop-at-postoffice"]:
											 if request.session['handling_option'] == "pick-up-package":
													 pickup_add = get_object_or_404(PickupLocation, pk = request.session.get('pickup_location_key'))
													 #pickup_add = PickupLocation.objects.get(pk = request.session.get('pickup_location_key', ""))

											 if request.session['handling_option'] == "drop-at-postoffice":
													pickup_add = get_object_or_404(DropOffPostOffice, pk = request.session.get('drop-at-postoffice'))

											 try:

													 distributor, origin_has_api = origin_distributor_access(request, pkg)
														#print "generating label: ", counter
													 if origin_has_api:
																print 'printing label.......'
																label   =   print_label(request, pkg, packages.count(), pickup_add, counter)
																label_obj = CourierLabel.objects.create(package = pkg, tracking_id = pkg.tracking_number, label = label)
																# pkg.usps_label = label_obj
																# pkg.save()
																label_ids.append(pkg.tracking_number)
											 except Exception as e:
													 msg = "System couldn't generate label at this time. %s" %e
													 messages.error(request, msg)
													 #return redirect(request.META.get('HTTP_REFERER'))
												#print "error: ", e

							 request.session['label_ids'] = label_ids

							 print 'label_ids: ',label_ids

							 generate_package_barcode(pkg, pkg.id, "import-barcodes")

							 '''Verify Flutterwave payment status and apply'''
							 if payment_type == 'Card Payment' and ('success' in pay_response_msg or 'Approved' in pay_response_msg):
								request.session['status'] = pay_response_msg
								#jejepay_ref = pay_response['jejepay_ref']
								print "flutter"
								update_payment_record_for_packages(request, packages, jejepay_ref)

							 elif payment_type == 'PP' and (request.GET.get('st') == "Completed"):

							 	update_paypal_payment_record_for_packages(request, packages)
							 	

							 packages.update(ordered = True, delivery_speed = request.session.get('dvm', ''))
							 get_cart_items(request).update(ordered = True)


							 # packages.update(ordered = True, delivery_speed = request.session.get('dvm', ''))
							 # get_cart_items(request).update(ordered = True)


							 #send confirmation mail to customer

							 try:
								send_confirmation_mail(shipment.user, shipment)
							 except:
								pass

							 request.session['shipment_placed'] = True

							 if payment_type == 'Card Payment' and ('Successful' in pay_response_msg or 'Approved' in pay_response_msg):
								print "welcome home"
								return redirect (reverse('shipping:confirmation_page'))
								#return JsonResponse({'redirect_url': request.build_absolute_uri(reverse('shipping:confirmation_page'))})
							 else:
								return redirect (reverse('shipping:confirmation_page'))

					try:
						messages.error(request, "Please select a payment method and accept %s's Terms and Conditions before you proceed." % request.marketing_member.storefront_name )
					except:
						pass
		 # pick_up_add = request.session.get('pickup-location', "none")
		 # counter = 0
		 # for pkg in packages:
		 #  counter += 1
		 #  if request.session['handling_option']  == "pick-up-package" or  request.session['handling_option'] == "export-import":
		 #    try:
		 #      label, file_path   =   print_label(request, pkg, packages.count(), pick_up_add, counter)
		 #      label_obj = UspsLabel.objects.create(tracking_id = pkg.tracking_number, label = file_path)
		 #      pkg.usps_label = label_obj
		 #      pkg.save()
		 #    except Exception as e:
		 #      print'e: ',e
					print form.errors
		# print "freight_VAT_SC_D + PSDG_D + pick_up_charge_D: ",freight_VAT_SC_D, PSDG_D, pick_up_charge_D
		 total_payable_D = freight_VAT_SC_D + PSDG_D + pick_up_charge_D
		 total_payable_N = freight_VAT_SC_N + PSDG_N +pick_up_charge_N
		 return render(request, template_name, {'handling_option':request.session.get('handling_option',""), 'packages': packages,
																					 'total_payable_D': total_payable_D, 'total_payable_N': total_payable_N,
																					 'shipping_cost_D': freight_VAT_SC_D, 'shipping_cost_N': freight_VAT_SC_N,
																					 'shipping_origin': shipping_origin, 'shipping_destination': shipping_destination,
																					 'coverage_D': coverage_amount_D, 'coverage_N': coverage_amount_N,
																					 'insurance_rate_D': PSDG_D, 'insurance_rate_N': PSDG_N, 'pick_up_charge_D':pick_up_charge_D,
																					 'pick_up_charge_N':pick_up_charge_N,'lb_country':lb_country,
																					 'months_list': flutterwave_helpers.months_list(), 'years_list': flutterwave_helpers.years_list()})





@login_required
def confirmation_page(request):
		context = {}
		active_session_list = ['pick_up_zipcode', 'dm','handling_option','shipment_placed','quantity','do_not_delete_all','suggested_box',
		'delivery_method','boxadded','delivery_local_freight_D','delivery_intl_freight_N',
		'billmelater','selected_delivery_method','package_destination','selected_pickup_location','package_warehouse',
		'delivery_total_freight_D', 'fedExLocs', 'selected_home_address','pickup-location',
		'requestPOST','shipping_origin','shipping_destination','dvm','pick_up_charge_D','addresses','delivery_intl_freight_D']

		handling_option = request.session.get('handling_option', "")


		pkg_list = request.session.get('package_ids', "")

		if len(pkg_list) > 0:
				packages = ShippingPackage.objects.filter(pk__in = pkg_list)
				context = get_context_dicts(request, packages)
				context.update({'handling_option':handling_option})

				for pkg in packages:

				#   pkg_model = "ShippingPackage"
					#
				#   status = "New"
					#
				#   pkg_status_list(pkg.pk,pkg_model,request.user,status)

					try:
						subject = "%s Package-%s Invoice" %(request.storefront_name.title(), pkg.tracking_number)
						#title = "[" + str(request.storefront_name.title()) + "] " + str(pkg.tracking_number) + " Package Invoice"
						sokohali_sendmail(request, request.user, subject, "email/package_invoice_email_template.html", pkg)
					except Exception as e:
						print "email not sent because:  %s" %(e)
						pass

				# delete cart session variables
				for key in request.session.keys():
					if key in active_session_list:
						del request.session[key]
				# print "cnt: ", context
				return render(request, 'shipping/confirmation.html', context)

		else:
				return redirect('/')




def package_invoice_page(request, tracking_id):
	template = "email/package_invoice_email_template.html"
	context = {}
	# print "here"
	# if shipment_type.lower() == "import":
	#   pkg = get_object_or_404(ShippingPackage, pk=pkg_id)
	# else:
	#   pkg = get_object_or_404(ExportPackage, pk=pkg_id)
	pkg = get_object_or_404(ShippingPackage, tracking_number=tracking_id)
	lb_country = pkg.costcalc_instance.country
	# if pkg.shipping_chain.origin == "United States":
	#     lb_country = pkg.shipping_chain.destination
	# else:
	#     lb_country = pkg.shipping_chain.origin

	context.update({'total_intl_freight_D': pkg.total_intl_freight_D(),
										'total_intl_freight_N': pkg.total_intl_freight_N(),'lb_country':lb_country})
	#print "pkg details: ",model_to_dict(pkg)
	context.update({'pkg':pkg})
	return render(request, template, context)



@login_required
def payment_option_api(request,**kwargs):
	 
	current_date = datetime.datetime.now()
	hashedValue = ""
	
	if request.method == "POST":
		
		customer_id = request.user.id			
		customer_name = request.user.get_full_name()		
					
		if kwargs.has_key("paypal"):			
			print "got to paypal"
			pay_type 			 = "Paypal"
			ref_no               = kwargs['order_id']
			bank                 = "Paypal"
			template_name_1      = "general_client/paypal_data.html"
			purchase_type_1      = "PayPal"
			receiver_mail        = kwargs['receiver_mail']
			amount 				 = kwargs['final_total']
			site_redirect_url 	 = kwargs['site_redirect_url']
			hashedValue 		 = hashedValue
			

		elif kwargs.has_key("ebiz"):
			print "got to ebiz"
			pay_type 			= "ebizCharge"
			ref_no   			= kwargs['order_id']
			bank 				="ebizCharge"
			template_name_1     ="general_client/ebiz.html"
			purchase_type_1     ="ebizCharge"
			receiver_mail       = kwargs["receiver_mail"]
			amount              = kwargs["final_total"]
			site_redirect_url   = kwargs["site_redirect_url"]
			hashedValue         = kwargs['ebizHash']
			invoice				= kwargs['invoice']

			# print 'hashedValue 1: ',hashedValue
			# print 'invoice 1: ',invoice
					
		return render_to_response(template_name_1,{'amount': amount,'txn_ref': ref_no,'customer_id': customer_id,
				"ebizHash": hashedValue, 'site_redirect_url': site_redirect_url,'receiver_mail':receiver_mail,
				'customer_name': customer_name, 'pay_type': pay_type, 'invoice': invoice}
				,context_instance=RequestContext(request))
		
				
	else:		
		return HttpResponse("Kindly enter the amount in number without the Dollar symbol and any comma.")



#@csrf_exempt
def fetchPackageLabel(request, tracking_id):
	template = "shipping_snippet/package-label.html"
	context = {}
	labels = []
	#context['single']  =  False
	if tracking_id == "all":
		context['labels'] = CourierLabel.objects.filter(tracking_id__in = request.session['label_ids'])
	else:
		label_obj = CourierLabel.objects.filter(tracking_id = tracking_id)
		if label_obj.exists():
			print 'label_obj: ',label_obj
			context['labels'] = label_obj#[0]
		else:
			#Reconnect to usps with package details and attempt label creation
			#package_obj = ShippingPackage.objects.filter(tracking_number = tracking_id)
			#pickup_location = package_obj[0].get_pickup_location()
			package_obj = ShippingPackage.objects.filter(tracking_number = tracking_id)
			pickup_location = package_obj[0].get_pickup_location()
			print_usps_label(request, package_obj, pickup_location, "requery")
			context['labels'] = CourierLabel.objects.filter(tracking_id = tracking_id)
			#context['labels'] = CourierLabel.objects.filter(tracking_id = tracking_id)

		#context['single']  =  True

	#print 'context: ',context
	return render(request, template, context)


@login_required
@csrf_exempt
def user_del_item(request):
		ShippingItem.objects.get(pk=request.POST.get('item_id')).delete()
		return JsonResponse({"ok":"ok"})



@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def dockreceipts(request):
	context = {}
	first_name =request.user.first_name
	# print "first_name :",first_name
	last_name =request.user.last_name
	# print "last_name :",last_name
	created_by = first_name +" "+ last_name
	# print "created_by :",created_by
	if request.POST:
		dock_form = DockReceiptForm(request.POST or None)
		shipping_package = ShippingPackageForm(request.POST or None)
		if dock_form.is_valid():
			dock = dock_form.save(commit=False)
			dock.created_by = created_by
			dock.tracking_number = str(request.POST.get('tracking_number'))
			print"Tracking Number :",dock.tracking_number
			dock.arrival_date = str(request.POST.get('arrival_date'))
			print"Arrived Date :",dock.arrival_date
			dock.arrived_time = request.POST['arrived_time']
			dock.unloaded_date = request.POST['unloaded_date']
			dock.unloaded_time = request.POST['unloaded_time']
			dock.date_from_receiving_clerk = request.POST['date_from_receiving_clerk']
			dock.shipping_package = ShippingPackage.objects.get(tracking_number =dock.tracking_number)
			dock.save()

			# status = "New dock Receipt"
			# action = "Dock Receipt wast created."
			# pkg_model = "DockReceipt"
			# post = DockReceipt.objects.get(tracking_number=tracking_number)
			# #pkg_status_list(post.pk,pkg_model,request.user,status)
			# shipment_history(request.user,post.pk,pkg_model,status,action)

			return redirect(request.META['HTTP_REFERER'])
			# render(request, 'sokohaliAdmin/shipments.html', {'dock_form':dock_form})
		else:
			print dock_form.errors
	else:
		return HttpResponseRedirect(reverse('shipping:shipment-manager'))

	return render(request, 'sokohaliAdmin/shipments.html', {'dock_form':dock_form})


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def dock_form_edit(request):
	if request.method =="POST":

		context = {}
		# print "I am here"
		tracking_number = request.POST.get('tracking_number')

		dock_form = get_object_or_404(DockReceipt, tracking_number=tracking_number)
		print"dock_form is : ", dock_form
		# return JsonResponse({'each_awb':each_awb})
	else:
		dock_form = DockReceiptForm

	# return render(request, "sokohaliadmin_snippet/editdock.html", {'dock_form':dock_form})
	return render(request, 'sokohaliAdmin/shipments.html', {'dock_form':dock_form})


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def dock_edit(request): 
	ItemToEdit =""
	rp = request.POST
	# print "rp", rp
	context ={}
	if request.method == "POST":
		tracking_number = rp.get('tracking_number')
		print"Track Number : ", tracking_number
		# containerized = rp.get('containerized')
		# print "Containerized : ",containerized

		itemToEdit = get_object_or_404(DockReceipt, tracking_number=tracking_number)

		itemToEdit.exporter_name_and_address = rp.get('exporter_name_and_address')
		# print"exporter_name_and_address: ", exporter_name_and_address
		itemToEdit.zip_code = rp.get('zip_code')
		itemToEdit.consigned_to = rp.get('consigned_to')
		itemToEdit.notify_party_name_and_address = rp.get('notify_party_name_and_address')
		itemToEdit.document_number = rp.get('document_number')
		itemToEdit.bl_or_awb_number = rp.get('bl_or_awb_number')
		itemToEdit.export_references = rp.get('export_references')
		itemToEdit.forwarding_agent_fmc_no = rp.get('forwarding_agent_fmc_no')
		itemToEdit.state_and_country_of_origin_or_ftz_number = rp.get('state_and_country_of_origin_or_ftz_number')
		itemToEdit.domestic_routing =rp.get('domestic_routing')
		itemToEdit.loading_pier = rp.get('loading_pier')
		itemToEdit.type_of_move = rp.get('type_of_move')
		itemToEdit.containerized = rp.get('containerized')
		print "Containerized :", itemToEdit.containerized
		itemToEdit.precarriage_by = rp.get('precarriage_by')
		itemToEdit.place_of_receipt_by_precarrier = rp.get('place_of_receipt_by_precarrier')
		itemToEdit.exporting_carrier = rp.get('exporting_carrier')
		itemToEdit.port_of_loading =rp.get('port_of_loading')
		itemToEdit.foreign_port_of_unloading = rp.get('foreign_port_of_unloading')
		itemToEdit.place_of_delivery_by_oncarrier = rp.get('place_of_delivery_by_oncarrier')
		itemToEdit.mks_nos = rp.get('mks_nos')
		itemToEdit.no_of_pkgs = rp.get('no_of_pkgs')
		itemToEdit.description_of_package_and_goods = rp.get('description_of_package_and_goods')
		itemToEdit.gross_weight = rp.get('gross_weight')
		itemToEdit.measurement = rp.get('measurement')
		itemToEdit.lighter_truck =rp.get('lighter_truck')
		itemToEdit.arrived_date = rp.get('arrived_date')
		itemToEdit.arrived_time =rp.get('arrived_time')
		itemToEdit.unloaded_date = rp.get('unloaded_date')
		itemToEdit.unloaded_time =rp.get('unloaded_time')
		itemToEdit.checked_by = rp.get('checked_by')
		itemToEdit.placed_location = rp.get('placed_location')
		itemToEdit.receiving_clerk_name = rp.get('receiving_clerk_name')
		itemToEdit.date_from_receiving_clerk = rp.get('date_from_receiving_clerk')

		itemToEdit.save()

		# status = "Edited dock Receipt"
		# action = "Dock Receipt was Edited."
		# pkg_model = "DockReceipt"
		# post = DockReceipt.objects.get(tracking_number=tracking_number)
		# print "POST :",post.tracking_number
		# #pkg_status_list(post.pk,pkg_model,request.user,status)
		# shipment_history(request.user,post.pk,pkg_model,status,action)
	# return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))
	return redirect(request.META['HTTP_REFERER'])


@login_required
def dock_template(request, tracking_number):
	context = {}
	bill_detail = get_object_or_404(DockReceipt, tracking_number=tracking_number)
	# print "Bill Detail : ", bill_detail
	# print "Shippers Name and Address : ", bill_detail.shippers_name_and_address
	return render(request, 'sokohaliAdmin/ocean-doc.html', {'bill_detail':bill_detail})




def get_local_distributor_locations(request):
    state = request.GET.get('state')
    country = request.GET.get('country')
    identifier = request.GET.get("identifier")
    local_locations = LocalDistributorLocation.objects.filter(country=country,state=state)
    #print local_locations, state, country
    return render(request, 'shipping_snippet/local_locations.html', {'locations':local_locations, "identifier":identifier})


def get_local_distributor_prices(request):
    origin_state = request.GET.get('origin_state')
    dest_state = request.GET.get('dest_state')
    origin_address = request.GET.get('origin_address')
    dest_address = request.GET.get('dest_address')
    weight = request.GET.get('weight')
    country = request.GET.get('country')
    from_option = request.GET.get('from_option')
    to_option = request.GET.get('to_option')
    if from_option == "drop-off":
	origin_city = LocalDistributorLocation.objects.get(id=origin_address).city
    if to_option == "pick-up":
	dest_city = LocalDistributorLocation.objects.get(id=dest_address).city
    region = TariffZone.objects.filter(from_city=origin_city, to_city=dest_city, country=country)
    print region
    price_list = []
    for x in region:
	price = LocalDistributorPrice.objects.get(region=x.region, weight=weight, weight_unit="kg")
	price_list.append(price)
    print price_list
    return render(request, 'shipping_snippet/local_rate.html', {'price_list':price_list})

def generate_local_tracking_no(request):
    mm = marketing_member(request)
    datetime = str(time.strftime("%y%m%d"))
    random_code = User.objects.make_random_password(length = 4, allowed_chars='0123456789')
    tracking_no = str(datetime) + str(random_code) + str(mm.random_code)
    while DomesticPackage.objects.filter(tracking_number=tracking_no):
	tracking_no = str(datetime) + str(random_code) + str(mm.random_code)
    print tracking_no
    return tracking_no
    



@login_required
def domestic_package(request):
    mm = marketing_member(request)
    if request.method == "POST":
	print request.POST
	origin_state 	= request.POST.get('state')
	dest_state 	= request.POST.get('state2')
	#origin_address 	= request.POST.get('origin_address')
	#dest_address 	= request.POST.get('dest_address')
	weight 		= request.POST.get('weight')
	country 		= request.POST.get('country')
	from_option 	= request.POST.get('from')
	to_option 	= request.POST.get('to')
	description 	= request.POST.get('description')
	price_id		= request.POST.get('amount')
	if from_option == "drop-off":
	    origin_address 	= request.POST.get('dropoff_address')
	    dropoff_center = LocalDistributorLocation.objects.get(id=origin_address)
	    pickup_address = None
	else:
	    address_line1 = request.POST.get('address1')
	    address_line2 = request.POST.get('address2')
	    city = request.POST.get('city')
	    zipcode = request.POST.get('zipcode')
	    telephone = request.POST.get('phone')
	    origin_address = DeliveryAddress.objects.create(user=request.user,address_line1=address_line1,address_line2=address_line2,city=city,state=origin_state, country=country,telephone=telephone,
						      zip_code=zipcode)
	    origin_address.save()
	    dropoff_center = None
	    pickup_address = origin_address
	    
	if to_option =="pick-up":
	    dest_address = request.POST.get('pickup_address')
	    pickup_center = LocalDistributorLocation.objects.get(id=dest_address)
	    dropoff_address = None
	else:
	    address_line1 = request.POST.get('to_address1')
	    address_line2 = request.POST.get('to_address2')
	    city = request.POST.get('to_city')
	    zipcode = request.POST.get('to_zipcode')
	    telephone = request.POST.get('to_phone')
	    dest_address = DeliveryAddress.objects.create(user=request.user,address_line1=address_line1,address_line2=address_line2,city=city,state=origin_state, country=country,telephone=telephone,
						      zip_code=zipcode)
	    dest_address.save()
	    pickup_center = None
	    dropoff_address = dest_address
	tracking_no = generate_local_tracking_no(request)
	ld_price = LocalDistributorPrice.objects.get(id=price_id)
	todaysdate  = datetime.datetime.now()
	weight_lb = float(weight) * 2.2
	local_pkg = DomesticPackage.objects.create(user=request.user, marketer=mm,tracking_number=tracking_no,weight_kg = weight, weight_lb = weight_lb,created_on=todaysdate,
					       amount=ld_price.price, shipper=ld_price.region.courier, description=description,dropoff_center=dropoff_center,pickup_center=pickup_center,dropoff_address=dropoff_address,pickup_address=pickup_address)
	local_pkg.save()
	request.session['local_pkg'] = local_pkg
	payment = select_payment_option(request)
	#print payment
	return payment
	
	
	    
	    
    
    
	
