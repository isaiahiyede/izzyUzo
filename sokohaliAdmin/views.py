from general.models import *
from shipping.models import *
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponse , HttpResponseRedirect, JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import user_passes_test, login_required
from general.staff_access import *
from cities_light.models import *
from django.core.files.base import ContentFile
from base64 import b64decode
from sokopay.templatetags.account_standing import account_standing
from django.contrib.auth import authenticate, login,logout
from general.payment_helpers import creditpurchase_ref
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from itertools import chain
from operator import attrgetter
from django.core import serializers, mail
from django.db.models import Q, Count, Sum
from django.utils.text import Truncator
from django.contrib import messages
from django.template.context import RequestContext

from django import template

from shipping.views import get_package_warehouses
from general.barcode_generator import generate_package_barcode
from general.views import get_route_chains, get_dest_warehouse_add
from shipping.pkg_charges import calculate_pickup_charge, calculate_last_mile_charges

import re
import hashlib
import datetime
import urllib
import time
import json, random, math

from sokopay.models import SokoPay, MarketerPayment
from django.core.urlresolvers import reverse

from django.template.loader import get_template, render_to_string
from django.template import Context
from django.utils import timezone
from sokohaliAdmin.models import *
from sokohaliAdmin.forms import *
from general.custom_functions import *
from general.forms import UserAccountForm
from sokohaliAdmin.forms import BatchForm, TruckingForm, BatchEditHistoryForm, AwbForm, SpecialRateForm, notifyUserForm, ShippingPackageForm, LocalDistributionMemberForm, LocalDistributorLocationForm
from sokohaliv2.settings import MEDIA_ROOT
from django.core.serializers.json import DjangoJSONEncoder
from shipping.forms import *
from django.core.mail import send_mail, EmailMessage,  get_connection, EmailMultiAlternatives
from service_provider.models import *
from service_provider.views import subscriber_marketer, request_subscriber
from shipping.views import get_office_pickup_locations, package_invoice_page

from shipping.CreateShipmentCostCalculator import *
from shipping.PackageCostCalculator import *
from general.custom_passes_test import request_passes_test

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from general.encryption import value_encryption, value_decryption


# Create your views here.

# Create your views here.


def get_pkg_rank(status):
	ranks = {"Processing for delivery":1,"Ready for collection":2,"Enroute to delivery":3,"Delivered":4}
	pkg_rank = []
	for rank in ranks:
		if rank == status:
			pkg_rank.append(ranks[rank])
		else:
			continue
	return pkg_rank


def get_batch_rank(status):
	ranks = {"New":1,"Processing":2,"Delivered to carrier":3,"Departed":4,
		"Clearing customs":5,"Processing for delivery":6,"Archive":7,"Cancel":8}
	batch_rank = []
	for rank in ranks:
		if rank == status:
			batch_rank.append(ranks[rank])
		else:
			continue
	return batch_rank


def get_counntry_from_short_code(value):
	try:
		code = []
		value = value.split('-')
		# print "the value: ",value
		for i in value:
			val = i.strip()
			get_country_name = Country.objects.get(code3=val)
			code.append(str(get_country_name))
	except:
		get_country_name = Country.objects.get(code3=value)
		code = get_country_name.name
	return code

#customized for batch number generation only
def get_short_code_from_country_name(value):
	value = value.split('-')
	code = []
	for i in value:
		val = i.strip()
		get_code = Country.objects.get(name=val)
		code.append(str(get_code.code3))
	return code


def getBatchNumber(value):
	old_time = re.sub('[:,-.'']',',',str(datetime.now())).replace(" ",",").split(',')
	del old_time[3:6]
	current_time = "".join(old_time)
	suffix = get_short_code_from_country_name(value)
	print "value: ",value
	# if value == "import":
	# 	return "IMP" + current_time
	# else:
	# 	return "EXP" + current_time
	return current_time + suffix[0] + "-" + suffix[1]


def add_space(word):
	the_new_word = list(word)
	new_word = []
	for i in the_new_word:
		if i.isupper():
			i = " " + i
			new_word.append(i)
		print "new word: ",new_word
	return "".join(new_word)


def save_file(file, path=''):
	filename = file._get_name()
	fd = open('%s/%s' % (MEDIA_ROOT, str(path) + str(filename)), 'wb')
	for chunk in file.chunks():
		fd.write(chunk)
	fd.close()


def all_same(items):
	return all(x == items[0] for x in items)


def truncateCharacters(word):
    if len(word) > 20:
        return word[0:20] + "..."
    else:
        return word


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def dashboardView(request):
	user = request.user
	# useraccount =
	print "USer ;",user
	return render(request, 'sokohaliAdmin/admin-dashboard.html', {})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def Shopping_orders(request):
	return render(request, 'sokohaliAdmin/orders.html', {})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None )
def shipments(request):

	try:
		populate_dockreceipt = DockReceipt.objects.latest('tracking_number')
		context['populate_dockreceipt'] = populate_dockreceipt

		dock_forms = DockReceiptForm(instance=populate_dockreceipt)
		# print "22222222222222"
	except:
		dock_forms = DockReceiptForm()
		# print "1111111111111"

	dock_form = dock_forms

	dockreceipt = DockReceipt.objects.values_list('tracking_number', flat=True)
	# print "DockReceipt :",dockreceipt
	# dockreceipt = dockreceipt

	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		mm_chains = subscriber.get_all_shipping_chains()
		imprt = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
	except:
		subscriber = request_subscriber(request)
		#Sub_WHM = subscriber.get_warehouses()
		imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
		mm_chains = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))

	# print "origin_ware_house:",subscriber.warehousemember
	# print "packages:",imprt
	client = checkSubscriber(request)
	if client != "Ordinary marketer":
		client = subscriber
	# if Sub_WHM:
	# 	imprt  = ShippingPackage.objects.filter((Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
	# else:
	# 	imprt = ShippingPackage.objects.filter(Q(shipping_chain__subscriber=subscriber), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))

	#export = ExportPackage.objects.filter(Q(user__useraccount__marketer = mm), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
	#imprt  = ShippingPackage.objects.filter((Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
	#imprt = ShippingPackage.objects.filter(Q(shipping_chain__subscriber=subscriber), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
	#shipment = paginate_list(request, list(reversed(sorted(chain(export, imprt), key=attrgetter('created_on')))),10)
	shipment = paginate_list(request, imprt, 10)

	# mm_chains = subscriber.get_all_shipping_chains()
	# print"mm_chains : ",mm_chains

	return render(request, 'sokohaliAdmin/shipments.html', {'shipment': shipment, 'mm_chains': mm_chains, 'subscriber':subscriber, 'dock_form': dock_form, 'dockreceipt':dockreceipt})


@login_required
def view_invoice(request, tracking_number):
	pkg_no = str(tracking_number)
	# if tracking_number[0] == "E":
	#     package = get_object_or_404(ExportPackage, tracking_number=pkg_no)
	# else:
	#     package = get_object_or_404(ShippingPackage, tracking_number=pkg_no)
	package = get_object_or_404(ShippingPackage, tracking_number=pkg_no)
	#address = package.destination_warehouse.warehouselocation.complete_address()
	#print "address;",address
	return render(request, 'sokohaliAdmin/invoice.html', {'package': package})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def process_package(request, tracking_number):

		print "rP: ",request.POST
		if request.POST.has_key('edit'):
			print "i wanna edit"
		else:
			print "i wanna process"

		tracking_number = str(tracking_number)
		quantity = 1
		selected_items_in_package = str(request.POST.get('put_selected_items')).split(",")
		marketer = marketing_member(request)

		post = get_object_or_404(ShippingPackage, tracking_number=tracking_number)

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

		weight_unit = str(request.POST.get("pkg_unit"))

		post_values = model_to_dict(post)

		new_tracking_number = post.tracking_number[15:].split('-')

		ship_origin = new_tracking_number[0]
		ship_destination = new_tracking_number[1]

		shipping_origin = country = get_counntry_from_short_code(ship_origin)
		# print 'shipping_origin:',shipping_origin
		shipping_destination = get_counntry_from_short_code(ship_destination)
		# print "shipping_destination:",shipping_destination
		if request.POST.has_key('edit'):
			check_exp_sea_or_air_freight = str(request.POST.get('pkg_ship_method'))
			check_home_or_ofice = post.delivery_method
			# print "Exp_Air_Sea",check_exp_sea_or_air_freight, check_home_or_ofice
		else:
			check_exp_sea_or_air_freight = str(post.shipping_method)
			check_home_or_ofice = str(post.delivery_method)
			#print "Exp_Air_Sea - Home_Office: ",check_exp_sea_or_air_freight,check_home_or_ofice

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

				form = ShippingPackageForm(request.POST, request.FILES, instance = post)

				if form.is_valid():
						post = form.save(commit=False)
						post.box_length = float(str(request.POST.get('box_length')))
						post.box_width  = float(str(request.POST.get('box_width')))
						post.box_height = float(str(request.POST.get('box_height')))
						post.box_weight = float(str(request.POST.get('box_weight')))
						# post.pkg_image  =  truncateCharacters(str(request.POST.get('contact_image_1')))
						imageURL  = request.POST.get('contact_image_1', '')
						x= imageURL[23:]
						image_data = b64decode(x)
						photo_code = ''
						characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
						photo_code_length = 20
						for x in range(photo_code_length):
							 photo_code += characters[random.randint(0, len(characters)-1)]
						photo_name = photo_code + '.jpeg'
						photo = ContentFile(image_data, photo_name)
						post.pkg_image = photo
						# print "photo", photo
						if request.POST.has_key('edit'):
							if weight_unit == "lb":
								post.box_weight_Dim = quantity * (post.box_length * post.box_width * post.box_height) / weightFactor
								post.box_weight_Dim_K = post.box_weight_Dim * lb_kg_factor
								print "wgt_d - wgt_k: ",post.box_weight_Dim,post.box_weight_Dim_K
								post.box_weight_K = post.box_weight * lb_kg_factor
								post.box_weight_Actual = post.box_weight * quantity
								post.box_weight_Actual_K = post.box_weight * lb_kg_factor * quantity
								post.shipping_method = check_exp_sea_or_air_freight
							else:
								post.box_weight_Dim = quantity * (post.box_length * post.box_width * post.box_height) / weightFactor
								post.box_weight_Dim_K = post.box_weight_Dim * lb_kg_factor
								print "wgt_d - wgt_k: ",post.box_weight_Dim,post.box_weight_Dim_K
								post.box_weight_K = post.box_weight * lb_kg_factor
								post.box_weight_Actual = post.box_weight * 2.20462 * quantity
								post.box_weight_Actual_K = post.box_weight * lb_kg_factor * quantity
						else:
							post.box_weight_Dim = quantity * (post.box_length * post.box_width * post.box_height) / weightFactor
							post.box_weight_Dim_K = post.box_weight_Dim * lb_kg_factor
							print "wgt_d - wgt_k: ",post.box_weight_Dim,post.box_weight_Dim_K
							post.box_weight_K = post.box_weight * lb_kg_factor
							post.box_weight_Actual = post.box_weight * quantity
							post.box_weight_Actual_K = post.box_weight * lb_kg_factor * quantity
						post.updated_by =  request.user.username
						post.updated_on =  timezone.now()
						# post.delivery_method = request.POST.get('pkg_delivery_method')
						post.approved = True

						if not request.POST.has_key('edit'):
							post.prepared_for_shipping = True
							post.status = "Prepared for shipping"

						if not request.POST.has_key('edit'):
							linked_items = ShippingItem.objects.filter(pk__in=selected_items_in_package)
							cart_value   = linked_items.aggregate(value = Sum('total_value'))['value']
							item_count   = linked_items.count()

						if request.POST.has_key('edit'):
							linked_items = post.item_packages()
							# print "LIIP:",linked_items
							cart_value = linked_items.aggregate(value = Sum('total_value'))['value']
							item_count = linked_items.count()
							# print "LI - CV - IC:",linked_items,cart_value,item_count

						# if request.POST.has_key('edit'):
						# 	location = LocalDistributorLocation.objects.get(id=request.POST.get('source'))
						# else:
						# 	location = LocalDistributorLocation.objects.filter(state=pickup_state)[0]

						# pkg_location_id = location.pk
						# request.session['pkg_location_id'] = pkg_location_id

						new_post = []
						new_post.append(post)

						shipping_weight = post.box_weight_higher()

						# region = location.region

						# local_freight_cost_D, local_freight_cost_N = region_local_freight_costs(request,region, shipping_weight)

						local_freight_cost_D = post.local_freight_D

						print "local_freight_cost_N , local_freight_cost_D:",local_freight_cost_D

						delivery_intl_freight_D, delivery_local_freight_D, delivery_total_freight_D  = get_freight_costs(request, new_post, shipping_origin[0], shipping_destination[0], costcalc)

						total_freight_D  = delivery_intl_freight_D + local_freight_cost_D

						print "total_freight_D = delivery_intl_freight_D + local_freight_cost_D :",delivery_intl_freight_D + local_freight_cost_D
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

						if request.POST.has_key('edit'):
							if request.POST.has_key('pkg_handling_option'):
								if post.discount_percentage:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val) * exchange_rate
									post.discount_D = (post.discount_percentage * post.admin_total_payable_D) / 100
									post.discount_N = (post.discount_percentage * post.admin_total_payable_N) / 100
									post.insure = True
								else:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val) * exchange_rate
									post.insure = True
							else:
								if post.discount_percentage:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val) * exchange_rate
									post.discount_D = (post.discount_percentage * post.admin_total_payable_D) / 100
									post.discount_N = (post.discount_percentage * post.admin_total_payable_N) / 100
									post.insure = False
								else:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val) * exchange_rate
									post.insure = False

						else:
							if post.insure:
								if post.discount_percentage:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val) * exchange_rate
									post.discount_D = (post.discount_percentage * post.admin_total_payable_D) / 100
									post.discount_N = (post.discount_percentage * post.admin_total_payable_N) / 100
								else:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val + PSDG_D_val) * exchange_rate
							else:
								if post.discount_percentage:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val) * exchange_rate
									post.discount_D = (post.discount_percentage * post.admin_total_payable_D) / 100
									post.discount_N = (post.discount_percentage * post.admin_total_payable_N) / 100
								else:
									post.admin_total_payable_D = post.user_total_payable_D = local_freight_cost_D + freight_VAT_SC_D_val
									post.admin_total_payable_N = post.user_total_payable_N = (local_freight_cost_D + freight_VAT_SC_D_val) * exchange_rate

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

							if user_country == "USA" or user_country == "United States":
								amount = post.balance_paid_D - post.admin_total_payable_D
							else:
								amount = post.balance_paid_N - post.admin_total_payable_N
							#print "amount", amount
							post.balance_paid_D = post.admin_total_payable_D
							post.balance_paid_N = post.admin_total_payable_N
							post.balance_D = post.balance_N = 0.00

							jejepay_obj = SokoPay.objects.create(user=post.user,purchase_type_1="Refund", purchase_type_2="Add", status = "Approved", ref_no = creditpurchase_ref(request),
							amount=amount,bank="Admin", message="Excess amount added to customer vei wallet")

							# print "jeje", jejepay_obj
							# post.balance_D = 0.00
							# post.balance_N = 0.00

						post.intl_freight_D = delivery_intl_freight_D
						post.intl_freight_N = delivery_intl_freight_D * exchange_rate

						post.local_freight_D = local_freight_cost_D
						post.local_freight_N = local_freight_cost_D * exchange_rate

						# print "freight_VAT_SC_D + PSDG_D + pick_up_charge_D: ",freight_VAT_SC_D, PSDG_D, pick_up_charge_D
						if not request.POST.has_key('edit'):
							ShippingItem.objects.filter(pk__in=selected_items_in_package).update(package=post)
						post.save()

						for item in linked_items:
							item.status = "Received"
							item.save()

						edit = {"height":post.box_height, "length":post.box_length, "width":post.box_width, "weight":post.box_weight, "weight_k":post.box_weight_K, "insurance":post.insure, "Shipping-method":post.shipping_method}
						pkg_model = "ShippingPackage"
						# print "edit:", edit
						if request.POST.has_key('edit'):
							fields_changed = {}
							status = "EDIT PACKAGE"
							diffkeys = [k for k in previous if previous[k] != edit[k]]
							for k in diffkeys:
								fields_changed.update({k: '%s to %s' %(previous[k], edit[k])})
							action = "The following fields were edited :" + str(fields_changed)
						else:
							status = post.status
							action = "This package was prepared for shipping"
							#pkg_status_list(post.pk,pkg_model,request.user,status)
						shipment_history(request.user,post.pk,pkg_model,status,action)
						# del request.session['pkg_location_id']

						try:
							del request.session['dvm']
						except:
							pass
						# to create bank record for all packages
						if request.user.useraccount.marketer.storefront_name == "volkmannexpress":

							user_client = UserAccount.objects.get(user = post.user)
							payment_channel = 'Bank Deposit'
							message = 'Being Payment for package balance'
							amount = post.admin_total_payable_D
					        ref_no = generate_creditpurchase_ref()
					        bank = None
					        teller_no = None
					        local_package = None

					        # payment = MarketerPayment.objects.create(user=user_client,
					        # 										 payment_channel=payment_channel,
					        # 										 created_at=datetime.now(),
					        # 										 message=message,
					        #                                          amount=amount,
					        #                                          package=post,
					        #                                          ref_no=ref_no,
					        #                                          marketer=marketer,
					        #                                          bank=bank,
					        #                                          teller_no=teller_no,
					        #                                          local_package=local_package)
					        # payment.save()

						del request.session['handling_option']
						del request.session['package']

						try:
							#user = User.objects.get(email=post.user.email)
							user = get_marketing_member_user(request, post.user.username)
							pkg = post
							subject = "%s Package-%s Invoice" %(request.storefront_name.title(), pkg.tracking_number)
							sokohali_sendmail(request, user, subject, "email/package_invoice_email_template.html", pkg)
							print 'email was sent to',user
						except Exception as e:
							print "email not sent because:  %s" %(str(e))
							pass

						if not request.POST.has_key('edit'):
							messages.success(request, "This package has been sucessfully Prepared for Shipping.")
						else:
							messages.success(request, "This package has been sucessfully edited.")
						return redirect(request.META['HTTP_REFERER'])
				else:
					print form.errors
					return redirect(reverse('sokohaliAdmin:shipment_manager'))
		else:
			return redirect(reverse('sokohaliAdmin:shipment_manager'))
		return redirect(reverse('sokohaliAdmin:shipment_manager'))


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def edit_package(request):
	rG = request.GET
	context = {}
	tracking_number = str(rG['pkg_id'])
	# client = checkSubscriber(request)
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
	except:
		subscriber = request_subscriber(request)
		#Sub_WHM = subscriber.get_warehouses()

	new_tracking_number = tracking_number[15:].split('-')

	shipping_origin = get_counntry_from_short_code(new_tracking_number[0])

	shipping_destination = get_counntry_from_short_code(new_tracking_number[1])

	regions = world_geo_data.Region.objects.filter(country__name = shipping_destination[0]).values_list('id','name')

	country_list_choice = ((shipping_destination[0], shipping_destination[0]),)

	form = AddressBookForm(country = country_list_choice, states = regions)

	if request.method == "GET":

		package = ShippingPackage.objects.get(tracking_number=rG['pkg_id'])

		marketer = marketing_member(request)

		office_pickup_locations = get_office_pickup_locations(request, shipping_origin, shipping_destination, 'destination')

		context = {'package':package,'office_pickup_locations':office_pickup_locations,'form':form, 'subscriber':subscriber}

		return render(request, 'admin-snippet/editpackage.html',context)
	else:
		return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def pkg_shipping_label(request, tracking_number):
	pkg = get_pkg_by_tracking_no_prefix(tracking_number)
	# print model_to_dict(pkg)
	if pkg.barcode_src == None:
		print 'generaing pkg barcode...'
		location = 'import'
		if tracking_number[0] == "E":
			location = 'export'
		generate_package_barcode(pkg, pkg.id, "%s-barcodes" %location)

	return render(request, 'sokohaliAdmin/shipping-label.html', {'pkg': pkg})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def item_details(request):
		package = None
		if request.method == "GET":
			input_detail = str(request.GET.get('trackg_no')).strip()
			# print input_detail
			# if input_detail[0] == "E":
			# 	package = ExportPackage.objects.get(tracking_number=input_detail)
			# else:
			package = ShippingPackage.objects.get(tracking_number=input_detail)
			return render(request, 'admin-snippet/process_package_modal.html', {'package':package})
		else:
			return render(request, 'sokohaliAdmin/item_details.html', {})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def assign_batch(request):
		'''who can assign to batch will be taken care of in the template'''
		batch = None
		if request.method == "GET":
			tracking_number = str(request.GET.get('tracking_number')).strip()
			direction = get_counntry_from_short_code(tracking_number[15:])
			new_direction = direction[0] + ' ' + '-' + ' ' + direction[1]
			pkg = ShippingPackage.objects.get(tracking_number=tracking_number)
			shipper = pkg.shipping_chain.shipper
			print "the shipper:", shipper
			print 'direction',new_direction
			subscriber = Subscriber.objects.get(shippingmember=shipper)

			print "the subscriber: ",subscriber
			# if tracking_number[0] == "E":
			# 	batches = Batch.objects.filter(batch_type="export", status="new")
			# else:
			# 	batches = Batch.objects.filter(batch_type="import", status ="new")
			pkg_shp_method = str(pkg.shipping_method).replace(' ','-')
			print pkg_shp_method
			batches = Batch.objects.filter(status="new",batch_type=new_direction,subscriber=subscriber, freight_type=pkg_shp_method)
			print "the bATCHES",batches
			return render(request, 'admin-snippet/assign_to_pkg_modal.html', {'batches':batches, 'tracking_number':tracking_number})
		else:
			print 'here'
			pkg_no = str(request.POST.get('trackg_no'))
			batch_no = str(request.POST.get('batchName'))
			package = ShippingPackage.objects.get(tracking_number=pkg_no)
			batch = Batch.objects.get(batch_number=batch_no)
			package.batch_assigned = batch
			package.status = "Assigned to batch"
			package.assigned_to_batch = True
			package.save()
			pkg_model = "ShippingPackage"
			action = "This package was assigned to batch" + " " + batch.batch_number
			status = package.status
			shipment_history(request.user,package.id,pkg_model,status,action)

			try:
				user = get_marketing_member_user(request, package.user.username)
				pkg = package
				subject = "%s Package-%s Invoice" %(request.storefront_name.title(), pkg.tracking_number)
				sokohali_sendmail(request, user, subject, "email/package_invoice_email_template.html", pkg)
				print 'email was sent to',user
			except Exception as e:
				print "email not sent because:  %s" %(str(e))
				pass

			messages.success(request, 'This package has been Assigned to a Batch')
			return redirect(reverse('sokohaliAdmin:shipment_manager'))


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def undo_batchassigned(request, tracking_number):
		pkg_no = tracking_number
		# if pkg_no[0] == "E":
		# 	package = ExportPackage.objects.get(tracking_number=pkg_no)
		# 	btch_num = package.batch_assigned.batch_number
		# else:
		package = ShippingPackage.objects.get(tracking_number=pkg_no)
		btch_num = package.batch_assigned.batch_number

		package.batch_assigned = None
		package.assigned_to_batch = False
		package.status = "Prepared for shipping"
		package.save()
		# if package.tracking_number[0] == 'E':
		# 	pkg_model = "ExportPackage"
		# else:
		pkg_model = "ShippingPackage"

		status = package.status
		action = "This package was removed from batch" + " " + btch_num
		#pkg_status_list(package.pk,pkg_model,request.user,status)
		shipment_history(request.user,package.id,pkg_model,"Removed from batch",action)
		btch_obj = Batch.objects.get(batch_number = btch_num)
		# print "btch_values: ",model_to_dict(btch_obj)
		# if pkg_no[0] == 'E':
		# 	if btch_obj.exportpackage_set.all().count() == 0:
		# 		btch_obj.status = "New"
		# 		btch_obj.save()
		# 	else:
		# 		pass
		# else:
		if btch_obj.shippingpackage_set.all().count() == 0:
			btch_obj.status = "New"
			btch_obj.save()
		else:
			pass
		messages.success(request, 'The package has been removed from the batch')
		return redirect(reverse('sokohaliAdmin:shipment_manager'))


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None )
def Batch_manager(request):
	context = {}
	form = BatchForm()
	try:
		populate_awb = AirwayBill.objects.latest('id')
		context['populate_awb'] = populate_awb
		# print "POPUL : ",popul
		awb_form = AwbForm(instance=populate_awb)
		# print "AWB :",awb_form
	except:
		awb_form = AwbForm()

	context['awb_form'] = awb_form
	# print "AWB FORM ?:", awb_form

	try:
		populate_dockreceipt = DockReceipt.objects.latest('id')
		context['populate_dockreceipt'] = populate_dockreceipt

		dock_form = DockReceiptForm(instance=populate_dockreceipt)
	except:
		dock_form = DockReceiptForm()

	context['dock_form'] = dock_form

	try:
		marketer = marketing_member(request)
		subscriber = marketer.subscriber
		routes = subscriber.get_all_shipping_chains()
	except:
		subscriber = request_subscriber(request)
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))

	# print "the subscriber: ",subscriber
	# print "marketer: ",marketer
	all_batches = new_batches = paginate_list(request,Batch.objects.filter(deleted=False,subscriber=subscriber),10)
	context['batches'] = all_batches
	context['new_batches'] = new_batches
	context['form'] = form
	awb = AirwayBill.objects.values_list('batch', flat=True)
	# print 'AWB : ', awb
	context['awb'] = awb
	dockreceipt = DockReceipt.objects.values_list('batch', flat=True)
	context['dockreceipt'] = dockreceipt
	context['subscriber'] = subscriber

	context['routes'] = routes

	return render(request, 'sokohaliAdmin/batches.html', context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
@user_passes_test(address_activated, login_url='/redirect_to_address_activation/', redirect_field_name=None )
def user_manager(request):
	mm = marketing_member(request)
	form = AdminCreateuserForm()
	form2 = SpecialRateForm()
	try:
		subscriber = mm.subscriber
	except:
		subscriber = request_subscriber(request)
	#useraccount = UserAccount.objects.all()
	origin, destination = get_route_chains(request)
	useraccount = UserAccount.objects.filter(marketer = mm, sokohali_admin=False)
	return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form': form, 'origin_countries':origin, 'destination_countries':destination, 'form2':form2, 'subscriber':subscriber})


def apply_specialRate(request):
	form2 = SpecialRateForm()
	origin, destination = get_route_chains(request)
	if request.method == "POST":
		user_pk  = request.POST.get('user')
		user = User.objects.get(id = user_pk)
		origin = request.POST.get('origin')
		destination = request.POST.get('destination')
		freight_type = request.POST.get('freight_type')
		rate = request.POST.get('rate_per_lb_D')
		create_specialRate = UserSpecialRate.objects.get_or_create(user=user, origin=origin,destination=destination,
																   freight_type=freight_type,rate_per_lb_D = rate,created_by=request.user,created_on=timezone.now())
		user_manager_history(request.user,user_pk,"UserAccount","Specialrate","Special rate was applied to this useraccount")
		return redirect(reverse('sokohaliAdmin:user-manager'))
	else:
		user_id = request.GET.get('user_id')
		user = User.objects.get(id = user_id)
		user_routes = UserSpecialRate.objects.filter(user=user)
		return render (request, 'admin-snippet/special_rate_modal.html', {'user_routes':user_routes, 'form2':form2, 'origin_countries':origin, 'destination_countries':destination})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def payments_log(request, payment_type, status):
	mm = marketing_member(request)
	try:
		subscriber = mm.subscriber
	except:
		subscriber = request_subscriber(request)
	if payment_type == 'card':
		if status == "successful":
			payments_log = MarketerPayment.objects.mm_successful_card_payments(mm)
			print "payments_log :", payments_log
		else:
			payments_log = MarketerPayment.objects.mm_unsuccessful_card_payments(mm)
			print "payments_log :", payments_log
	elif payment_type == 'veiwallet':
		if status == "successful":
			payments_log = MarketerPayment.objects.filter((Q(purchase_type_2="Add") | Q(purchase_type_2="Remove")), status="Approved", purchase_type_3="veiwallet")
			print "payments_log :", payments_log
		else:
			payments_log= MarketerPayment.objects.filter(purchase_type_2="Add",status="Unsuccessful", purchase_type_3="veiwallet")
			print "payments_log :", payments_log
	elif payment_type == 'bank-deposit':
		if status == "approved":
			payments_log = MarketerPayment.objects.mm_successful_bank_payments(mm)
			print "payments_log :", payments_log
		elif status == "pending":
			payments_log = MarketerPayment.objects.mm_pending_bank_payments(mm)
			print "payments_log :", payments_log
		else:
			payments_log= MarketerPayment.objects.mm_declined_bank_payments(mm)
			print "payments_log :", payments_log
	else:
		payments_log = MarketerPayment.objects.mm_paypal_payments(mm)
		print "payments_log :", payments_log

	return render(request, 'sokohaliAdmin/payments_log.html', {'payments_log': payments_log,
							'payment_type': payment_type, 'status': status, 'subscriber':subscriber})

@csrf_exempt
def approve_bankpayment(request):
	if request.method == "POST":
		print "rp",request.POST
		status = request.POST.get('decision')
		print 'A',status
		obj_id = request.POST.get('obj_id')
		print 'B',obj_id

		# obj_pw = request.POST.get('obj_pw')
		# print 'C',obj_pw

		# secret_ans = SecurityQuestion.objects.get(user=request.user.useraccount).answer
		# print "Secret Ans :", secret_ans

		payment = MarketerPayment.objects.get(id=obj_id)
		useraccount = payment.user
		pkg = ShippingPackage.objects.get(tracking_number=payment.package.tracking_number)
		dollar_exchange_rate = pkg.costcalc_instance.dollar_exchange_rate

		if pkg.admin_total_payable_D <= payment.amount:
			pkg.user_total_payable_D=pkg.admin_total_payable_D=pkg.balance_D = 0
			pkg.user_total_payable_N=pkg.admin_total_payable_N=pkg.balance_N = 0
			pkg.balance_paid_D = payment.amount
			pkg.balance_paid_N = payment.amount*dollar_exchange_rate
			pkg.save()

		#pkg.balance_paid_D = payment.amount
		#payment_helpers.apply_shipping_credit(request, pkg, pkg.user, payment.amount)
			# if secret_ans:
			# 	if status == "yes":
			# 		payment.status = "Approved"
			# 		payment.message = request.user.username
			# 		payment.save()
			# 		messages.success(request, "This payment has been sucessfully approved")
			# 		action = "This payment has been sucessfully approved"
			# 		# print payment.ref_no
			# 	else:
			# 		payment.status = "Declined"
			# 		payment.message = request.user.username
			# 		payment.save()
			# 		messages.warning(request, "This Payment has been Declined")
			# 		action = "This Payment has been Declined"
			# 	#user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
			# 	sokopayment_history(request.user, payment.ref_no,"MarketerPayment",payment.status,action)
			# else:
			# 	print "Wrong secret answer"

			if status == "yes":
				payment.status = "Approved"
				payment.message = request.user.username
				payment.save()
				messages.success(request, "This payment has been sucessfully approved")
				action = "This payment has been sucessfully approved"
				# print payment.ref_no
			else:
				payment.status = "Declined"
				payment.message = request.user.username
				payment.save()
				messages.warning(request, "This Payment has been Declined")
				action = "This Payment has been Declined"
			#user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
			sokopayment_history(request.user, payment.ref_no,"MarketerPayment",payment.status,action)

	return redirect(request.META['HTTP_REFERER'])

@csrf_exempt
def approve_veipayment(request):
	mm = marketing_member(request)
	if request.method == "POST":
		print request.POST
		status = request.POST.get('decision')
		print status
		obj_id = request.POST.get('obj_id')
		print obj_id
		payment = MarketerPayment.objects.get(id=obj_id)
		user = payment.user.user
		useraccount = UserAccount.objects.get(user=user)
		if not status == "yes":
			payment.status = "Declined"
			payment.message = "This payment has been declined"
			payment.approved_by = request.user.username
			payment.save()
			messages.warning(request, "This Payment has been Declined")
			action = "This Payment has been Declined"
		else:
			payment.status = "Approved"
			payment.message = "This payment has been sucessfully approved"
			payment.approved_by = request.user.username
			payment.save()
			messages.success(request, "This payment has been sucessfully approved")
			action = "This payment has been sucessfully approved"
			# print payment.ref_no
			all_cost = CostCalcSettings.objects.get(marketer=mm,country=useraccount.country)
			if not useraccount.country == "United States" or "USA":
			    dollarNairaRate = all_cost.dollar_exchange_rate
			    useraccount.credit_amount_D += payment.amount
			    useraccount.credit_amount_N += float(dollarNairaRate) * float(useraccount.credit_amount_D)
			    useraccount.save()
			else:
			    useraccount.credit_amount_D += payment.amount
			    useraccount.save()
			
        sokopayment_history(request.user, payment.ref_no,"MarketerPayment",payment.status,action)
        return redirect(request.META['HTTP_REFERER'])


def approve_sokopayment(request):
	if request.method == "POST":
		status = request.POST.get('decision')
		print status
		obj_id = request.POST.get('obj_id')
		print obj_id
		payment = SokoPay.objects.get(id=obj_id)
		user = payment.user
		useraccount = UserAccount.objects.get(user=user)
		if status == "yes":
			payment.status = "Approved"
			payment.message = request.user.username
			payment.save()
			messages.success(request, "This payment has been sucessfully approved")
			action = "This payment has been sucessfully approved"
			# print payment.ref_no
		else:
			payment.status = "Declined"
			payment.message = request.user.username
			payment.save()
			messages.warning(request, "This Payment has been Declined")
			action = "This Payment has been Declined"
		user_credit_amount_N, user_credit_amount_D = account_standing(request, user)
		sokopayment_history(request.user, payment.ref_no,"Sokopay",payment.status,action)
		return redirect(request.META['HTTP_REFERER'])


@login_required
def paySearch(request):
	if request.method == 'GET':
		mm = marketing_member(request)
		# print "MM ",mm
		try:
			subscriber = mm.subscriber
		except:
			subscriber = request_subscriber(request)

		input_value = request.GET.get('input_value')
		# print "input Value : ", input_value

		date_from = request.GET.get('from')
		# print "Date from :", date_from
		date_to = request.GET.get('to')
		# print "Date to : ", date_to

		if input_value != '' and date_from != '' and date_to != '':
			payments_log = SokoPay.objects.filter(Q(ref_no=input_value) | Q(user__first_name=input_value) |Q(user__last_name=input_value) | Q(teller_no=input_value),
			Q(created_at__range=[date_from, date_to]), user__useraccount__marketer = mm)
			# print "payments_log ", payments_log
			return render(request, 'sokohaliAdmin/payments_log.html', {'payments_log':payments_log, 'input_value':input_value, 'date_from':date_from, 'date_to':date_to})

		if date_from != '' and date_to != '':
			payments_log = SokoPay.objects.filter(Q(created_at__range=[date_from, date_to]), user__useraccount__marketer = mm)
			# print "payments_log ", payments_log
			return render(request, 'sokohaliAdmin/payments_log.html', {'payments_log':payments_log, 'date_from':date_from, 'date_to':date_to})

		if input_value != '':
			payments_log = SokoPay.objects.filter(Q(ref_no=input_value) | Q(user__first_name=input_value) |Q(user__last_name=input_value) | Q(teller_no=input_value),
			user__useraccount__marketer = mm)
			# print "payments_log ", payments_log
			return render(request, 'sokohaliAdmin/payments_log.html', {'payments_log':payments_log})

	return render(request, 'sokohaliAdmin/payments_log.html', {'payments_log':payments_log, 'input_value':input_value, 'date_from':date_from, 'date_to':date_to,'subscriber':subscriber})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def adminCreateuser(request):
	print 'the method',request.method
	mm = marketing_member(request)
	#print "i reach here"
	username = str(request.GET.get('username')).strip()
	email  = str(request.GET.get('email')).strip()
	#firstname = str(request.GET.get('firstname')).strip()
	#lastname = str(request.GET.get('lastname')).strip()
	if request.method == "GET":
		# print username, email
		user_email = UserAccount.objects.filter(user__email=email, marketer = mm, sokohali_admin=False)
		user = UserAccount.objects.filter(user__username=username, marketer = mm, sokohali_admin=False)
		if user_email.exists() and not user.exists():
			return JsonResponse({'result':'email'})
		elif user.exists() and not user_email.exists():
			return JsonResponse({'result':'user'})
		elif user_email.exists() and user.exists():
			return JsonResponse({'result': 'both'})
		else:
			return JsonResponse({'result':'Ok'})

	if request.method == "POST":
		form = AdminCreateuserForm(request.POST)
		username = str(request.POST.get('username')).strip()
		email  = str(request.POST.get('email')).strip()
		firstname = str(request.POST.get('first_name')).strip()
		lastname = str(request.POST.get('last_name')).strip()
		# print firstname, lastname
		if form.is_valid():
			password = email
			user = User.objects.create_user(username = username, email=email, first_name=firstname, last_name=lastname, password=password)
			# print user.username
			createduser = form.save(commit=False)
			createduser.suite_no = generate_suite_no()
			createduser.user = user
			createduser.registration_time = timezone.now()
			try:
				createduser.marketer = mm
			except:
				pass
			createduser.save()
			text = 'email/admin_welcome_email.txt'
			user = createduser.user
			try:
				sokohali_sendmail(request, user,"Welcome Aboard", text, None)
			except:
				pass
			user_manager_history(request.user, user.id,"UserAccount","AdminCreateUser","This useraccount was created on this day")
		return redirect(reverse('sokohaliAdmin:user-manager'))
	else:
		form = AdminCreateuserForm()
	return render(request, 'admin-snippet/create_user_modal.html', {'form': form})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def searchbar(request):
	#mm = marketing_member(request)
	#mm_chains = mm.get_shipping_chains()
	form = AdminCreateuserForm()
	form2 = SpecialRateForm()
	if request.method == "GET":
		page = request.GET.get('page')
		if page == "userpage":
			mm = marketing_member(request)

			input_value = str(request.GET.get('input_value')).strip()
			start_date = request.GET.get("from")
			to_date = request.GET.get("to")

			if input_value != "":
				if start_date == "" and to_date == "":
					useraccount = UserAccount.objects.filter(Q(user__username=input_value) |Q(user__useraccount__suite_no=input_value) |Q(first_name=input_value) |Q(last_name=input_value) |Q(user__email__iexact=input_value), marketer = mm,  sokohali_admin=False)
					return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2})
				else:
					end_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days = 1)# this is to convert the to_date which is in unicode to a datetime object.
					useraccount = UserAccount.objects.filter(Q(user__username=input_value) |Q(user__useraccount__suite_no=input_value) |Q(first_name=input_value) |Q(last_name=input_value) |Q(user__email__iexact=input_value) |Q(registration_time__range=[start_date, end_date]), marketer = mm,  sokohali_admin=False)
					return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2})
			elif input_value == "":
				if start_date != "" and to_date != "":
					end_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days = 1)# this is to convert the to_date which is in unicode to a datetime object.
					useraccount = UserAccount.objects.filter(registration_time__range=[start_date, end_date], marketer = mm,  sokohali_admin=False)
					return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2})
				else:
					messages.error(request,"Please Enter a search parameter")
			else:
				return redirect(request.META['HTTP_REFERER'])

		elif page == "shipmentpage":
			input_value = str(request.GET.get('input_value')).strip()
			month 	=	request.GET.get('month')
			print input_value,month
			#Sub_WHM = subscriber.get_warehouses()

			if input_value == "" and month == 'hide':
				messages.error(request,"Please Enter a search parameter")
				return redirect(request.META['HTTP_REFERER'])

			elif input_value != "" and month == 'hide':
				#export = ExportPackage.objects.filter((Q(user__useraccount__marketer = mm) |Q(user__email__iexact=input_value) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)),deleted=False)
				try:
					mm = marketing_member(request)
					subscriber = mm.subscriber
					mm_chains = mm.get_shipping_chains()
					imprt =  ShippingPackage.objects.filter((Q(user__email__iexact=input_value) |Q(user__useraccount__suite_no=input_value) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)),deleted=False, is_estimate=False, ordered = True, shipping_chain__subscriber=subscriber)
					print"Imprt : ",imprt
				except:
					subscriber = request_subscriber(request)
					mm_chains = None
					imprt =  ShippingPackage.objects.filter((Q(user__email__iexact=input_value) |Q(user__useraccount__suite_no=input_value) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), deleted=False, is_estimate=False, ordered = True )
					#imprt =  ShippingPackage.objects.filter((Q(user__email__iexact=input_value) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)),deleted=False, is_estimate=False, ordered = True, shipping_chain__subscriber=subscriber)
				#print "import - export: ",imprt, export
				client = checkSubscriber(request)
				if client != "Ordinary marketer":
					client = subscriber
				shipment = paginate_list(request, imprt, 10)
				print shipment
				return render(request, 'sokohaliAdmin/shipments.html', {'shipment': shipment,'mm_chains':mm_chains, 'subscriber':subscriber})

			elif input_value != "" and month != 'hide':
				#export = ExportPackage.objects.filter((Q(user__email__iexact=input_value) |Q(created_on__month=month) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)), user__useraccount__marketer = mm, deleted=False)
				try:
					mm = marketing_member(request)
					subscriber = mm.subscriber
					mm_chains = mm.get_shipping_chains()
					imprt = ShippingPackage.objects.filter((Q(user__email__iexact=input_value) |Q(user__useraccount__suite_no=input_value) |Q(created_on__month=month) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), deleted=False, is_estimate=False, ordered = True, shipping_chain__subscriber=subscriber)
					print"Imprt : ",imprt
					#imprt = ShippingPackage.objects.filter((Q(user__email__iexact=input_value) |Q(created_on__month=month) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), deleted=False, is_estimate=False, ordered = True)
				except:
					subscriber = request_subscriber(request)
					mm_chains = None
					imprt = ShippingPackage.objects.filter((Q(user__email__iexact=input_value) |Q(user__useraccount__suite_no=input_value) |Q(created_on__month=month) |Q(tracking_number__iexact=input_value) |Q(user__first_name=input_value) |Q(user__last_name=input_value)), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), deleted=False, is_estimate=False, ordered = True)
				#shipment = paginate_list(request, list(reversed(sorted(chain(export, imprt), key=attrgetter('created_on')))),10)
				client = checkSubscriber(request)
				if client != "Ordinary marketer":
					client = subscriber
				shipment = paginate_list(request, imprt, 10)
				return render(request, 'sokohaliAdmin/shipments.html', {'shipment': shipment,'mm_chains':mm_chains, 'subscriber':subscriber})

			elif input_value == "" and month != 'hide':
				try:
					mm = marketing_member(request)
					subscriber = mm.subscriber
					mm_chains = mm.get_shipping_chains()
				#export = ExportPackage.objects.filter(Q(created_on__month=month), user__useraccount__marketer = mm, deleted=False)
					imprt = ShippingPackage.objects.filter(Q(created_on__month=month), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), shipping_chain__subscriber=subscriber, deleted=False, is_estimate=False, ordered = True)
					print"Imprt : ",imprt
				except:
					subscriber = request_subscriber(request)
					imprt = ShippingPackage.objects.filter(Q(created_on__month=month), (Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), deleted=False, is_estimate=False, ordered = True)
				#shipment = paginate_list(request, list(reversed(sorted(chain(export, imprt), key=attrgetter('created_on')))),10)
				client = checkSubscriber(request)
				if client != "Ordinary marketer":
					client = subscriber
				shipment = paginate_list(request, imprt, 10)
				return render(request, 'sokohaliAdmin/shipments.html', {'shipment': shipment,'mm_chains':mm_chains, 'subscriber':subscriber})

		else:
			return redirect(request.META['HTTP_REFERER'])
	else:
		return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def package_filter(request, route_id):
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		mm_chains = subscriber.get_all_shipping_chains()
	except:
		subscriber = request_subscriber(request)
		mm_chains = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber)
												 |Q(destination_warehouse__offered_by = subscriber))
	print"mm_chains : ",mm_chains
	pkgs = ShippingChain.objects.get(id = route_id)
	print pkgs
	shipment=pkgs.get_pkgs_in_chain().filter(deleted=False)
	# route_value = str(request.POST.get('route_value'))
	#print"Sent Value : ", route_value
	return render(request, 'sokohaliAdmin/shipments.html', {'shipment': shipment, 'mm_chains':mm_chains,'subscriber':subscriber})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def sidebar(request, action):
	form = AdminCreateuserForm()
	form2 = SpecialRateForm()
	status = action

	try:
		mm = marketing_member(request)
	except:
		pass
	try:
		subscriber = mm.subscriber
	except:
		subscriber = request_subscriber(request)


	if action == "new":
		time_24_hours_ago = datetime.now() - timedelta(days=1)
		useraccount = UserAccount.objects.filter(registration_time__gte=time_24_hours_ago, marketer = mm)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})

	elif action == "address_activation":
		useraccount = UserAccount.objects.filter(address_activation = True, marketer = mm, sokohali_admin=False)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})

	elif action == "Admin":
		useraccount = UserAccount.objects.filter(user__is_staff = True, marketer = mm, sokohali_admin=False)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})

	elif action == "Deactivated":
		useraccount = UserAccount.objects.filter(deactivated = True, marketer = mm, sokohali_admin=False)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})

	elif action == "Flagged":
		useraccount = UserAccount.objects.filter(flagged = True, marketer = mm, sokohali_admin=False)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})

	elif action == "unverified":
		useraccount = UserAccount.objects.filter(address_activation = False, address_activation_completed = True, marketer = mm,  sokohali_admin=False)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})

	elif action == "staff_access":
		useraccount = UserAccount.objects.filter(user__is_staff = True, marketer = mm, sokohali_admin=False)
		return render(request, 'sokohaliAdmin/staff_access.html', {'useraccount': useraccount, 'form':form, 'form2':form2,'subscriber':subscriber})


	elif action == status:
		if not status == "revoked":
			try:
				mm = marketing_member(request)
				subscriber = mm.subscriber
				#mm_chains = subscriber.get_all_shipping_chains()
				imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False), Q(status=action))
				mm_chains = mm.get_shipping_chains()
			except:
				subscriber = request_subscriber(request)
				#Sub_WHM = subscriber.get_warehouses()
				imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False), Q(status=action))
				mm_chains = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
		else:
			try:
				mm = marketing_member(request)
				subscriber = mm.subscriber
				#mm_chains = subscriber.get_all_shipping_chains()
				imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=True))
				mm_chains = mm.get_shipping_chains()
			except:
				subscriber = request_subscriber(request)
				#Sub_WHM = subscriber.get_warehouses()
				imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=True))
				mm_chains = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))


		client = checkSubscriber(request)
		print "client:", client
		if client != "Ordinary marketer":
			client = subscriber
		# try:
		# 	mm = marketing_member(request)
		# 	subscriber = mm.subscriber
		# except:
		# 	subscriber = request_subscriber(request)

		# Sub_WHM = subscriber.get_warehouses()
		# if Sub_WHM:
		# 	imprt  = ShippingPackage.objects.filter((Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(status=status), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
		# else:
		# 	imprt = ShippingPackage.objects.filter(Q(shipping_chain__subscriber=subscriber), Q(ordered = True), Q(status=status), Q(is_estimate=False), Q(deleted=False))
		#export = ExportPackage.objects.filter(Q(user__useraccount__marketer = mm), Q(ordered = True), Q(is_estimate=False), Q(status=status), Q(deleted=False))
		#shipment = paginate_list(request, list(reversed(sorted(chain(export, imprt), key=attrgetter('created_on')))),10)
		shipment = paginate_list(request, imprt, 10)
		return render(request, 'sokohaliAdmin/shipments.html', {'shipment': shipment,'mm_chains':mm_chains, 'subscriber':subscriber})

	else:
		useraccount = UserAccount.objects.filter(marketer = mm)
		return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount,'subscriber':subscriber})


@login_required
def user_history(request, user_id):
	history = ActionHistory.objects.filter(obj_id=user_id)
	return render (request, 'sokohaliAdmin/userhistory.html', {'history': history})


@login_required
def payment_history(request):
	history = ActionHistory.objects.filter(obj_model_name="Sokopay")
	return render (request, 'sokohaliAdmin/userhistory.html', {'history': history})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def usertype(request, user_id, action):
	mm = marketing_member(request)
	user_model = "UserAccount"
	useraccount = UserAccount.objects.filter(marketer = mm, sokohali_admin=False)
	if action == "make_admin":
		print user_id
		user = User.objects.filter(pk = user_id)#.update(is_staff = True)
		useraccount = UserAccount.objects.get(user=user)
		if not useraccount.address_activation:
			messages.warning(request, "This User status cannot be changed until address activation is verified.")
			status = "This account couldn't be made an admin due to incomplete verification"
			user_manager_history(request.user,user_id,user_model,action,status)
			return redirect(reverse('sokohaliAdmin:user-manager'))
		else:
			user = User.objects.filter(pk = user_id).update(is_staff = True)
			messages.success(request, "This User status has been sucessfully updated")
			status = "This User was made an Admin"
			user = User.objects.get(pk = user_id)
			title = "Account Update"
			text = 'email/admin.txt'
	elif action == "undo_admin":
		user = User.objects.filter(pk = user_id).update(is_staff = False)
		messages.success(request, "This User status has been sucessfully updated")
		status = "This User's Admin status was undone"
		user = User.objects.get(pk = user_id)
		title = "Account Update"
		text = 'email/undo-admin.txt'
	elif action == "flag":
		user_status = UserAccount.objects.filter(pk = user_id).update(flagged = True)
		flag_packages(request, user_id, 'flag')
		user = UserAccount.objects.get(pk=user_id)
		user = user.user
		user_id = user.id
		messages.success(request, "This User Account has been sucessfully Flagged")
		status = "This User was Flagged"
		title = "Account Update"
		text = 'email/flagged.txt'
	elif action == "verify":
		user_status = UserAccount.objects.filter(pk = user_id).update(flagged = False)
		flag_packages(request, user_id, 'verify')
		user = UserAccount.objects.get(pk=user_id)
		user = user.user
		user_id = user.id
		messages.success(request, "This User Account has been sucessfully Verified")
		status = "This User has been verified"
		title = "Account Update"
		text = 'email/verified.txt'
	elif action == "deactivate":
		user_status = UserAccount.objects.filter(pk = user_id).update(deactivated = True)
		user = UserAccount.objects.get(pk=user_id)
		user = user.user
		user_id = user.id
		messages.success(request, "This User status has been sucessfully updated")
		status = "This User's account was deactivated"
		title = "Account Deactivation"
		text = 'email/deactivated.txt'
	elif action == "reactivate":
		user_status = UserAccount.objects.filter(pk = user_id).update(deactivated = False)
		user = UserAccount.objects.get(pk=user_id)
		user = user.user
		user_id = user.id
		messages.success(request, "This User status has been sucessfully updated")
		status = "This User's account was reactivated"
		title = "Account Re-activation"
		text = 'email/reactivation.txt'
	elif action == "reverify":
		user = UserAccount.objects.get(pk=user_id)
		user.address_activation = False
		user.address_activation_completed = False
		user.save()
		user = user.user
		user_id = user.id
		messages.success(request, "This User status has been sucessfully updated")
		status = "This User was asked to reverify his account"
		title = "Account Update"
		text = 'email/reverify.txt'
	elif action == "activate_address":
		useraccount = UserAccount.objects.get(pk = user_id)
		useraccount.address_activation = True
		useraccount.save()
		messages.success(request, "This User status has been sucessfully updated")
		user = useraccount.user
		user_id = user.id
		status = "This User's address was activated"
		text = 'email/address_activation.txt'
		title = "Address Activation"
	try:
		sokohali_sendmail(request, user, title, text, None)
	except Exception as e:
		print e
	user_manager_history(request.user,user_id,user_model,action,status)
	return redirect(reverse('sokohaliAdmin:user-manager'))
	#return render(request, 'sokohaliAdmin/users.html', {'useraccount': useraccount})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def find_user(request):
	#print "i got here"
	''' revisit this function '''
	query = request.GET.get('query')
	print "query:",query
	if request.GET.has_key('identifier'):
		template_name = 'admin-snippet/matchingusers.html'
		identifier = str(request.GET.get('identifier')).strip()
	else:
		template_name = 'admin-snippet/received_users.html'
		identifier = 'identifier'
	print "identifier:", identifier
	find_user = get_marketing_member_users(request).filter(address_activation = True, user__is_staff=False, flagged = False).filter(
			Q(suite_no = query)|
			Q(first_name__icontains = query)|
			Q(last_name__icontains = query)|
			Q(user__email__iexact = query))

	print "users:",find_user
	return render(request, template_name,  {'users': find_user, 'identifier': identifier})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def notify_user(request):
	user_id = str(request.GET.get('user_id'))
	description = str(request.GET.get('description'))
	user = User.objects.get(useraccount__pk = user_id)
	print user.username, description
	title = "Package Creation Notification"
	text = 'email/notify_user.html'
	try:
		sokohali_sendmail(request, user, title, text, description)
	except Exception as e:
		print "message was not sent because of ", e
	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def show_admin_added_items(request):
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		marketer_routes = subscriber.get_all_shipping_chains()
	except:
		subscriber = request_subscriber(request)
		marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))

    #print 'see me na.... coding things on point'
	template_name = 'admin-snippet/cb_item_list.html'
	user_id = str(request.GET.get('user_id'))
	user_obj = UserAccount.objects.get(id=user_id)
	user = User.objects.get(useraccount=user_obj)
	items_type = str(request.GET.get('items_type'))
	print "items_type: ",items_type

	if not items_type == "FixedWeight":
	    items = ShippingItem.objects.filter(user=user,created_by_admin=True, ordered=False, item_type="Regular")
	    if items:
	        alert = "You have added Regular items for this customer"
	    else:
	        alert = "You have not added any Regular items for this customer"
	else:
	    items = ShippingItem.objects.filter(user=user,created_by_admin=True, ordered=False, item_type="fixed_weight")
	    if items:
	        alert = "You have added fixed weight items for this customer"
	    else:
	        alert = "You have not added any fixed weight items for this customer"
	return render(request, template_name, {'items': items,'alert':alert,'marketer_routes':marketer_routes,'subscriber':subscriber})

	try:
	    query = request.GET.get('query')
	    identifier = request.GET.get('identifier')
	except:
	    return {'result': 'fail'}
	    if query:
	        find_user = User.objects.filter(Q(useraccount__suite_no = query) | Q(first_name__icontains = query) | Q(last_name__icontains = query) | Q(email__icontains = query))
	        if len(find_user) > 0:
	            return render(request, template_name, {'users': find_user, 'identifier': identifier})
	        else:
	            return render(request, 'admin-snippet/matchingusers.html', {'alert': 'No matching result'})
	        return HttpResponse(response, content_type = 'application/javascript; charset=utf-8')
	    else:
	        return render(request, 'admin-snippet/matchingusers.html', {'alert': 'Please enter Suite #, First Name , Last Name or E-mail !!!','subscriber':subscriber})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def cb_user_info(request):
	#print "i got here"
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		routes = subscriber.get_all_shipping_chains()
	except:
		subscriber = request_subscriber(request)
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))

	template_name = 'admin-snippet/cb_add_item.html'
	# exp_category = ExportCategory.objects.all()
	rG = request.GET
	#print "rG:",rG
	if 'user_id' in request.GET:
		user_id = request.GET.get('user_id')
		print "id:",user_id
		user = UserAccount.objects.get(pk = user_id)
		print "user:",user
		# return render(request, template_name, {'user': user, 'exp_category':exp_category})
		return render(request, template_name, {'user': user,'marketer_routes':routes,'subscriber':subscriber})
	else:
		return render(request,  template_name, {'alert': 'Please check a box before you click the Next button','mm_routes':marketer_routes,'subscriber':subscriber})



@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def subCategory(request):
	category = request.GET.get('category')
	cat = ExportCategory.objects.get(name=category)
	sub_category = cat.exportsubcategory_set.all().values('id', 'content', 'name')
	return JsonResponse({'response': json.dumps(list(sub_category), cls=DjangoJSONEncoder)})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def fixed_weight_info(request):
	fixed_wgt_cat_id = request.GET.get('cat_id')
	print "This is the id: ",fixed_wgt_cat_id
	fixed_wgt_rate = FixedShipment.objects.get(id=fixed_wgt_cat_id)
	return JsonResponse({'fixed_wgt_rate': fixed_wgt_rate.unit_price_D, 'fxd_item_desc':fixed_wgt_rate.description})


def get_warehouse_addresses(request):
	context = {}
	direction = request.GET.get('direction')
	selected_items = request.GET.getlist('searchIDs[]')
	print "SIT: ", selected_items
	print 'rG:',request.GET
	if request.GET.has_key('fxd_wgt_val'):
		template_name = 'admin-snippet/whadresses2.html'
	else:
		template_name = 'admin-snippet/whaddresses.html'
	print "dir", direction
	sh_chain = ShippingChain.objects.get(id = direction)
	print "sc: ", sh_chain
	origin_whm = sh_chain.origin_warehouse.get_all_warehouses().filter(country = sh_chain.origin)
	print origin_whm
	dest_whm = sh_chain.destination_warehouse.get_all_warehouses().filter(country=sh_chain.destination)
	print dest_whm
	routes = []
	for selected_item in selected_items:
		route = ShippingItem.objects.get(id=selected_item).shipping_chain
		routes.append(route)
	print "routes: ",routes

	if all_same(routes):
		pass
	else:
		print "was here not ok"
		result = 'fail'
		return JsonResponse({'result':result})
	for route in routes:
		if sh_chain != route:
			print "was here not ok"
			result = 'fail again'
			return JsonResponse({'result':result})
		else:
			pass
	return render(request, template_name, {'origin_whm':origin_whm, 'dest_whm':dest_whm})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def cb_add_item(request):
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
	except:
		subscriber = request_subscriber(request)
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	if request.method=="POST":
	    rp = request.POST
	    print "rP:",rp
	    user_account = UserAccount.objects.get(pk = str(rp.get('user_id')))
	    user = User.objects.get(useraccount=user_account)
	    # shipping_chain_obj = ShippingChain.objects.get(id=rp.get('sh_chain'))
	    pkg_type = str(rp.get('cb_pkg_type'))
	    # print "type: ",pkg_type
	    # print user
	    # naira_value = float(rp.get('cb_total_value')) * dollarNairaRate
	    if not rp.get('extra_charges') == "extra_charges":
	    	extra_charge = float(rp.get('extra_charges'))
	    	fixed_value = float(rp.get('cb_total_value'))
	    	total_value = extra_charge + fixed_value
	    	print "total value:", total_value
	    else:
	    	total_value = str(rp.get('cb_total_value')).replace(",","")

	    # print "naira_value", naira_value
	    if total_value == 0.0:
	    	return render(request, 'admin-snippet/cb_item_list.html', {'fail': 'fail', 'items': items,'marketer_routes':routes,'subscriber':subscriber})

	    else:
		    try:
				if not pkg_type == "FixedWeight":
				    item = ShippingItem.objects.create(
				        user = user,
				        quantity = str(rp.get('cb_quantity')),
				        total_value = total_value,
				        # shipping_chain = shipping_chain_obj,
				        # total_value_N = naira_value,
				        courier_tracking_number = rp['uniquetrait1'],
				        description= rp['uniquetrait2'], created_by_admin=True,
				    	status = "Received")
				    items = ShippingItem.objects.filter(user = user,created_by_admin=True, ordered=False, item_type="Regular")
				else:
					shipping_chain_obj = ShippingChain.objects.get(id=rp.get('sh_chain'))
					desc = str(rp.get("uniquetrait2")) + "," + str(rp.get("fxd_wgt_desc"))
					cat_id = str(rp.get("fxd_id"))
					print "desc: ",desc
					print "cat_id",cat_id
					item = ShippingItem.objects.create(
				        user = user,
				        quantity = str(rp.get('cb_quantity')),
				        total_value = total_value,
				        shipping_chain = shipping_chain_obj,
				        courier_tracking_number = rp['uniquetrait1'],
				        description= desc,
				        created_by_admin=True,
				        item_type="fixed_weight",
				        status="Received",
				        cat_num=cat_id)
					items = ShippingItem.objects.filter(user = user,created_by_admin=True,ordered=False,item_type="fixed_weight")
				return render(request, 'admin-snippet/cb_item_list.html', {'items': items,'marketer_routes':routes,'subscriber':subscriber})
		    except Exception as e:
		    	# print "error because of " + str(e)
		    	items = ShippingItem.objects.filter(user = user, package = None)
		    	return render(request, 'admin-snippet/cb_item_list.html', {'alert': 'Please complete all form fields correctly', 'items': items,'marketer_routes':routes,'subscriber':subscriber})


	else:
		return render(request, 'admin-snippet/cb_item_list.html', {'alert': 'Please complete all form fields correctly', 'items': items,'marketer_routes':routes,'subscriber':subscriber})


@login_required
def admin_create_package(request):
    current_time = datetime.today()

    if request.method == "POST":

		rp = request.POST
		print 'rP: ',request.POST

		freight_VAT_SC_D = PSDG_D = VAT_D = coverage_amount_D = 0

		if not rp.get('shipment_type') == "FixedWeight":
			length = float(str(rp.get('id_length')))
			width  = float(str(rp.get('id_width')))
			height = float(str(rp.get('id_height')))
			weight = float(str(rp.get('id_weight')))
		else:
			length = 0.0
			width  = 0.0
			height = 0.0
			weight = 0.0

		if rp.get('shipment_type') == "FixedWeight":
			print "yes1"
			direction = str(rp.get('shipping_direction2')).split('-')
			print direction
		else:
			print "yes2"
			direction = str(rp.get('shipping_direction')).split('-')
		print "direction: ",direction

		selected_items = str(rp.get('user_items_selected')).split(",")
		print selected_items

		# if rp.get('shipment_type') == "FixedWeight":
		# 	origin = rp.get('WHaddress3')
		# 	destination = rp.get('WHaddress4')
		# 	print "origin-destination", origin, destination
		# else:
		# 	origin = rp.get('WHaddress')
		# 	destination = rp.get('WHaddress2')

		if rp.get('shipment_type') == "FixedWeight":
			try:
				direction = str(rp.get('shipping_direction2')).split('-')
				origin = str(direction[0]).strip()
				destination = str(direction[1]).strip()
			except:
				origin = rp.get('WHaddress3')
				destination = rp.get('WHaddress4')
			print "origin-destination", origin, destination

		else:
			origin = rp.get('WHaddress')
			destination = rp.get('WHaddress2')

		print "selected_items:",selected_items

		# if rp.get('shipment_type') == "FixedWeight":
		# 	total_value = 0
		# 	items_selected = ShippingItem.objects.filter(pk__in=selected_items)
		# 	for item in items_selected:
		# 		total_value += item.total_value
		# 	print "total_value: ",total_value
		# 	print "items-selected",items_selected
		# else:
		# 	pass

		try:
			if rp.has_key('user_obj'):
				user_client = UserAccount.objects.get(user__username = rp.get('user_obj'))
				print "user_client:",user_client
				user_marketer = user_client.marketer
				print "user_client:",user_marketer
				client = User.objects.get(useraccount=user_client)
				print "client: ",client
				admin = request.user
			else:
				user_client = UserAccount.objects.get(user = rp.get('user_package_created'))
				print "user_clientB:",user_client
				user_marketer = user_client.marketer
				print "user_clientB:",user_marketer
				client_obj = UserAccount.objects.get(pk=rp.get('user_package_created'))
				client = User.objects.get(useraccount=client_obj)
				admin = request.user

		except:
			user_client = UserAccount.objects.get(user=request.user)
			print "user_clientC:",user_client
			user_marketer = user_client.marketer
			print "user_clientC:",user_marketer
			client = User.objects.get(useraccount=user_client)
			print "clientC: ",client
			admin = None

		quantity = 1

		marketer = marketing_member(request)

		request.session['handling_option'] = "send-from-shop"

		# print "the chain: ", marketer_chain

		if rp.get('shipment_type') == "FixedWeight":
			shipping_origin = country = str(direction[0]).strip()
			shipping_destination = str(direction[1]).strip()
			print "shipping origin:", shipping_origin
			print "shipping destination:", shipping_destination
		else:
			shipping_origin = country = direction[0].strip()
			shipping_destination = direction[1].strip()
			print "shipping origin:", shipping_origin
			print "shipping_destination:", shipping_destination

		# warehouse_destination = marketer.get_shipping_chain_route_warehouse_destination(shipping_origin, shipping_destination)
		# warehouse_origin = marketer.get_shipping_chain_route_warehouse_origin(shipping_origin, shipping_destination)

		try:
			warehouse_destination = WarehouseLocation.objects.get(id = destination)
			warehouse_origin = WarehouseLocation.objects.get(id = origin)
		except:
			warehouse_destination = WarehouseLocation.objects.get(id = rp.get('WHaddress4'))
			warehouse_origin = WarehouseLocation.objects.get(id = rp.get('WHaddress3'))

		request.session['WHaddress'] = warehouse_destination.id

		default_address = warehouse_destination.full_address()
		# print "default_address: ",default_address

		if shipping_origin == 'United States':
			lb_country = shipping_destination
		else:
			lb_country = shipping_origin

		costcalc  =  create_obj_costcalc(request,lb_country)
		print "cost settingS: ", costcalc

		weightFactor   = costcalc.dim_weight_factor
		lb_kg_factor   = costcalc.lb_kg_factor
		kg_lb_factor   = costcalc.kg_lb_factor
		exchange_rate  = costcalc.dollar_exchange_rate

		dim_weight = quantity * (length * width * height) / weightFactor #in lbs
		entered_weight = weight
		weight_unit = str(rp.get("unit"))

		box_weight_Dim = dim_weight #* in lbs
		box_weight_Dim_K = dim_weight * lb_kg_factor
		box_weight_K = weight * lb_kg_factor

		shippingWght = 0.0

		if weight_unit == "lb":
			box_weight_Actual = entered_weight * quantity
			box_weight_Actual_K = entered_weight * lb_kg_factor * quantity

			if box_weight_Actual_K > box_weight_Dim_K:
				shippingWght = box_weight_Actual_K
			else:
				shippingWght = box_weight_Dim_K

		elif rp.has_key('mail_bag_package'):
			box_weight_Actual_K = 0
			box_weight = box_weight_K = box_weight_Dim = box_weight_Dim_K = box_weight_Actual = 0
			box_length = box_width = box_height = 0
			items_selected_total_weight = ShippingItem.objects.filter(pk__in=selected_items).aggregate(Sum('weight'))['weight__sum']
			print "items_total_weight",items_selected_total_weight
			shippingWght = float(items_selected_total_weight) * quantity
			box_weight_Actual_K = shippingWght
			box_weight_Actual = box_weight_Actual_K
			print "weight:",shippingWght

		else:
			box_weight_Actual = entered_weight * 2.20462 * quantity
			box_weight_Actual_K = entered_weight * quantity

			if box_weight_Actual_K > box_weight_Dim_K:
				shippingWght = box_weight_Actual_K
			else:
				shippingWght = box_weight_Dim_K


		create_package = ShippingPackage.objects.create(user=client,box_weight_Actual=box_weight_Actual,
					box_weight_Actual_K=box_weight_Actual_K,box_weight_Dim=box_weight_Dim,box_weight_Dim_K=box_weight_Dim_K,
					box_length=length,box_width=width,box_weight=weight,box_height=height,box_weight_K=box_weight_K)

		create_package.destination_warehouse = warehouse_destination.owned_by
		create_package.origin_warehouse = warehouse_origin.owned_by

		create_package.default_origin_address = warehouse_origin.full_address()
		create_package.default_destination_address = warehouse_destination.full_address()

		print "whm", warehouse_origin.full_address()
		pick_up_charge_D = 0.0
		pick_up_charge_N = 0.0

		items_in_package = ShippingItem.objects.filter(pk__in=selected_items)
		item_count = items_in_package.count()

		if rp.has_key('mail_bag_package'):
			shipping_weight = shippingWght
			cart_value = str(rp.get('total'))
		else:
			shipping_weight = create_package.box_weight_higher()
			cart_value = items_in_package.aggregate(value = Sum('total_value'))['value']

		# print "cart_value: ",cart_value
		pkg_count = create_package.box_quantity

		item_shipping_chain = marketer.get_shipping_chain_route(shipping_origin,shipping_destination)

		shipping_items_to_ship = ShippingItem.objects.filter(pk__in = selected_items)

		for items in shipping_items_to_ship:
			print "shipping_items_to_ship",shipping_items_to_ship
			items.package = create_package
			items.shipping_chain = item_shipping_chain
			items.save()

		package = []

		package.append(create_package)
		print "the package:", package

		update_pkg_total_value = (ShippingPackage,package)

		state = warehouse_destination.state
		print "state: ",state

		try:
			region_obj = LocalDistributorLocation.objects.filter(state=state)[0]
			print "region: ",region_obj
			region = region_obj.region
			print "next regoin: ",region
			local_freight_cost_D, local_freight_cost_N = region_local_freight_costs(request,region, shippingWght,country)

		except:
			local_freight_D, local_freight_N = calculate_last_mile_charges(request, package[0], shipping_origin, shipping_destination, 'destination')
			local_freight_cost_D,local_freight_cost_N = float(local_freight_D),float(local_freight_N)

		print "local_freight_cost_N , local_freight_cost_D:",local_freight_cost_N, local_freight_cost_D

		if not rp.get('shipment_type') == "FixedWeight":
			delivery_intl_freight_D, delivery_local_freight_D, delivery_total_freight_D  = get_freight_costs(request, package, shipping_origin, shipping_destination, costcalc)

		elif rp.has_key('mail_bag_package'):

			localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
				costPerLbAir, costPerLbSea, costPerLbExpress, exchange_rate, expressFreight, expressFreight_N  = PackageCostCalc(request, package[0].box_weight_higher(), package[0].box_weight_higher_K(), shipping_origin, shipping_destination, None, lb_country)

			if rp.get('pkg_ship_method') == 'Sea Freight':
				delivery_intl_freight_D = seaFreight
				delivery_intl_freight_N = seaFreight_N
			else:
				delivery_intl_freight_D = airFreight
				delivery_intl_freight_N = airFreight_N

		else:
			delivery_intl_freight_D = cart_value
			print "total value", delivery_intl_freight_D

		total_freight_D  = delivery_intl_freight_D + local_freight_cost_D

		print "delivery_intl_freight_D + local_freight_cost_D:", delivery_intl_freight_D + local_freight_cost_D

		pkg_info = {'pkg_count': pkg_count, 'item_count': item_count,
						 'shippingWeight': shipping_weight, 'cart_value': cart_value, 'total_freight_D': total_freight_D}

		if country == 'United States':
			country = shipping_destination

		total_freight_D_val, VAT_D_val, totalServiceCharge_D_val, \
		  CON_D_val, PSDG_D_val, SMP_D_val, freight_VAT_SC_D_val, coverage_amount_D_val, exchange_rate = CreateShipmentCostCalc(request, pkg_info, country)

		freight_VAT_SC_D   += freight_VAT_SC_D_val
		PSDG_D             += PSDG_D_val
		VAT_D              += VAT_D_val
		coverage_amount_D  += coverage_amount_D_val

		create_package.insurance_fee_D = PSDG_D_val
		create_package.insurance_fee_N = PSDG_D_val * exchange_rate

		create_package.VAT_charge_D = VAT_D_val
		create_package.VAT_charge_N = VAT_D_val * exchange_rate
		
		create_package.service_charge_D = totalServiceCharge_D_val
		create_package.service_charge_N = totalServiceCharge_D_val * exchange_rate

		create_package.admin_total_payable_D = create_package.user_total_payable_D = freight_VAT_SC_D_val
		create_package.admin_total_payable_N = create_package.user_total_payable_N = freight_VAT_SC_D_val * exchange_rate

		create_package.coverage_amount_D = coverage_amount_D_val
		create_package.coverage_amount_N = coverage_amount_D_val * exchange_rate

		create_package.pick_up_charge_D = pick_up_charge_D
		create_package.pick_up_charge_N = pick_up_charge_N
		create_package.insure = True

		if rp.get('shipment_type') == "FixedWeight" and not rp.has_key('mail_bag_package'):
			create_package.status = "Prepared for shipping"
			create_package.prepared_for_shipping = True
			create_package.shipment_type = "fixed_weight"

		if shipping_origin == 'United States':
			lb_country = shipping_destination
		else:
			lb_country = shipping_origin

		create_package.costcalc_instance = costcalc

		create_package.intl_freight_D = delivery_intl_freight_D
		create_package.intl_freight_N = delivery_intl_freight_D * exchange_rate

		create_package.local_freight_D = local_freight_cost_D
		create_package.local_freight_N = local_freight_cost_D * exchange_rate

		create_package.total_package_value =  cart_value
		if rp.get('shipment_type') == "FixedWeight":
			create_package.shipping_method = rp.get('pkg_ship_method')
		else:
			create_package.shipping_method = "Air Freight"
		create_package.delivery_method = "Office pickup"

		try:
			create_package.shipping_chain = marketer.get_shipping_chain_route(shipping_origin,shipping_destination)
		except:
			create_package.shipping_chain = subscriber.get_subscriber_shipping_chain_route
			marketer = user_client.marketer

		marketer_state = marketer.state
		marketer_city = marketer.city
		marketer_phone_number = marketer.phone_number

		if not rp.has_key('mail_bag_package'):
			marketer_delivery_address = DeliveryAddress.objects.create(user=request.user,address_line1=marketer.address1,address_line2=marketer.address2,
				city=marketer_city,state=marketer_state,telephone=marketer_phone_number)
		elif rp.has_key('admin'):
			marketer_delivery_address = WarehouseLocation.objects.get(pk=rp.get('pick_up_add'))
		else:
			if not rp.get('pkg_ship_addresses') == "":
				marketer_delivery_address = DeliveryAddress.objects.get(pk=rp.get('pkg_ship_addresses'))
			else:
				marketer_delivery_address = DeliveryAddress.objects.create(
	            user          = request.user,
	            address_line1 = rp.get('street_number'),
	            address_line2 = rp.get('enterYourAddress'),
	            city          = rp.get('locality'),
	            state         = rp.get('route'),
	        )

		try:
			create_package.default_destination_address = marketer_delivery_address.address_line1 + ',' + marketer_delivery_address.address_line2 + ',' + marketer_delivery_address.city + ',' + marketer_delivery_address.state
		except:
			create_package.default_destination_address = marketer_delivery_address.address1 + ',' + marketer_delivery_address.address2 + ',' + marketer_delivery_address.city + ',' + marketer_delivery_address.state + ',' + marketer_delivery_address.country + ',' + marketer_delivery_address.location_prefix

		if rp.has_key('admin'):
			create_package.created_by_admin = True

		create_package.tracking_number = update_pkg_values(marketer,shipping_origin,shipping_destination, package[0], costcalc, "", ShippingPackage, create_package.insure, "Payment on hold")

		try:
			create_package.shippingitem_set.all().update(ordered=True, status="Processed")
			print "i did this"
		except:
			create_package.shippingitem_set.all().update(ordered=True)
			print "i did that"

		create_package.handling_option = "send-from-shop"

		print "got here"
		create_package.save()

		del request.session['handling_option']
		del request.session['WHaddress']

		pkg_model = "ShippingPackage"

		status = "New"

		action = status + " " + "package created"

		print "action:", action

		shipment_history(request.user,create_package.id,pkg_model,status,action)

		print "freight_VAT_SC_D + PSDG_D + pick_up_charge_D: ", freight_VAT_SC_D, PSDG_D, pick_up_charge_D

		if rp.has_key('mail_bag_package'):
			return redirect(reverse('general:my_shipments_volk'))

    return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def bmgr_actions(request,action):
	context = {}
	form = BatchForm()
	context['form'] = form
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	except:
		subscriber = request_subscriber(request)
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	template_name = "sokohaliAdmin/batches.html"
	new_batches = Batch.objects.filter(status="New",subscriber=subscriber).count()
	batches_fetched = paginate_list(request,Batch.objects.filter(status=action,subscriber=subscriber),10)
	context['batches'] = batches_fetched
	context['new_batches'] = new_batches
	context['routes'] = routes
	context['subscriber'] = subscriber
	return render(request, template_name, context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def batch_actions(request,action,batch_id):

    context = {}
    form = BatchForm()
    context['form'] = form
    referer = redirect(request.META['HTTP_REFERER'])
    # mm = marketing_member(request)
    if action == "archive":
        batch_fetched = paginate_list(request,Batch.objects.filter(id=batch_id).update(status=action),10)
        messages.success(request, "The batch status has been sucessfully updated")
        return referer
    elif action == "unarchive":
        batch_fetched = paginate_list(request,Batch.objects.filter(id=batch_id).update(status="New"),10)
        messages.success(request, "The batch status has been sucessfully updated")
        return referer
    else:
        messages.warning(request, "Oops Something went wrong and the batch status was not updated")
    return referer


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def process_batches(request):

		# marketer = MarketingMember.objects.filter(pk=1)[0]
		marketer =marketing_member(request)

		referer = redirect(request.META['HTTP_REFERER'])
		context = {}
		rp = request.POST
		update_type = str(rp.get("update_type"))
		old_status = str(rp.get("old_status")).split(",")
		# print "the status:",old_status
		# print "the Rank:", get_batch_rank(old_status[0])

		batch_ids = str(rp.get("batch_ids")).split(",")
		current_time = datetime.today()
		new_batch_rank = get_batch_rank(update_type)
		old_batch_rank = get_batch_rank(old_status[0])
		# print "old_status,new_status: ", old_status, update_type
		# print "old_batch_rank,new_batch_rank: ", old_batch_rank,new_batch_rank
		title = str(marketer.storefront_name)

		if len(old_status) > 1:
			if not all_same(old_status):
				messages.warning(request,"Cannot updates batches with different statuses")

			elif all_same(old_status):
				if old_batch_rank[0] + 1 >= new_batch_rank[0]:
					for batch_id in batch_ids:
						# Batch.objects.filter(id=batch_id,user=request.user).update(status=update_type)
						batchToEdit = Batch.objects.get(id=batch_id)
						if len(batchToEdit.get_packages_in_batch()) == 0:
							# print "pkgs in batch: ",batchToEdit.get_packages_in_batch()
							messages.warning(request,"You cannot process an empty batch")
							return referer
						else:
							batchToEdit.status = update_type
							batchedithistory = BatchEditHistory.objects.get_or_create(user=request.user,batch=batchToEdit,
													updated_on=current_time,batch_status=update_type)
							batchToEdit.save()
							pkgs = batchToEdit.get_packages_in_batch()
							print "pkgs:",pkgs
							for pkg in pkgs:
								pkg.status = update_type
								pkg.save()

								pkg_model = "ShippingPackage"

								status = pkg.status

								status = 'The status of this package was updated to ' + pkg.status

								try:
									#user = User.objects.get(email=post.user.email)
									user = get_marketing_member_user(request, pkg.user.username)
									subject = "%s - %sPackage ID" %(request.storefront_name.title(), pkg.tracking_number)
									sokohali_sendmail(request, user, subject, "email/batchupdate_email.html", pkg)
									print 'email was sent to',user
								except Exception as e:
									print "email not sent because:  %s" %(str(e))
									pass

					messages.success(request, "The Selected batch(es) status has been sucessfully updated")
				else:
					messages.warning(request, "Please update batches in the correct order")

		else:
			if old_batch_rank[0] + 1 >= new_batch_rank[0]:
						# Batch.objects.filter(id=batch_ids[0],user=request.user).update(status=update_type)
						batchToEdit = Batch.objects.get(id=batch_ids[0])
						if len(batchToEdit.get_packages_in_batch()) == 0:
							messages.warning(request,"You cannot process an empty batch")
							print "pkgs in batch: ",batchToEdit.get_packages_in_batch()
							return referer
						else:
							batchToEdit.status = update_type
							batchedithistory = BatchEditHistory.objects.get_or_create(user=request.user,batch=batchToEdit,
							updated_on=current_time,batch_status=update_type)
							batchToEdit.save()
							# if batchToEdit.batch_type == "import":
							# 	pkgs = batchToEdit.importpackage_set.all()
							# else:
							# 	pkgs = batchToEdit.exportpackage_set.all()

							pkgs = batchToEdit.shippingpackage_set.all()

							for pkg in pkgs:
								pkg.status = update_type
								pkg.save()

								pkg_model = "ShippingPackage"

								status = 'The status of this package was updated to ' + pkg.status

								pkg_status_list(pkg.pk,pkg_model,request.user,status)

								try:
									#user = User.objects.get(email=post.user.email)
									user = get_marketing_member_user(request, pkg.user.username)
									subject = "%s - %sPackage ID" %(request.storefront_name.title(), pkg.tracking_number)
									sokohali_sendmail(request, user, subject, "email/batchupdate_email.html", pkg)
									print 'email was sent to',user
								except Exception as e:
									print "email not sent because:  %s" %(str(e))
									pass

							messages.success(request, "The Selected batch(es) status has been sucessfully updated")
			else:
				messages.warning(request, "Please update batches in the correct order")

		return referer


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def search_batch(request):

	template_name = "sokohaliAdmin/batches.html"
	context = {}
	form = BatchForm()
	context['form'] = form
	rp = request.POST
	batch_no = str(rp.get("batchNo")).strip()
	batch_type = str(rp.get("batchType"))
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
	except:
		subscriber = request_subscriber(request)
	# routes = subscriber.get_all_shipping_chains()
	if batch_no:
		if batch_type != "Type":
			batches_fetched = paginate_list(request,Batch.objects.filter(batch_number=batch_no, batch_type=batch_type,subscriber=subscriber),10)
			context['batches'] = batches_fetched
			context['subscriber'] = subscriber
			return render(request, template_name, context)
		else:
			batches_fetched = paginate_list(request,Batch.objects.filter(batch_number=batch_no,subscriber=subscriber),10)
			context['batches'] = batches_fetched
			context['subscriber'] = subscriber
			return render(request, template_name, context)
	else:
		batches_fetched = paginate_list(request,Batch.objects.filter(batch_type=batch_type,subscriber=subscriber),10)
		context['batches'] = batches_fetched
		context['subscriber'] = subscriber
		return render(request, template_name, context)

	return render(request, template_name, context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def create_batch(request):
    context = {}
    try:
	    marketer = request.user.useraccount.marketer
	    subscriber = marketer.subscriber
	    routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
    except:
		subscriber = request_subscriber(request)
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
    template_name = "sokohaliAdmin/batches.html"
    all_batches = paginate_list(request,Batch.objects.filter(subscriber=subscriber),10)
    form = BatchForm()
    rp=request.POST
    # print "rp; ",rp
    context['form'] = form
    context['batches'] = all_batches
    context['routes'] = routes
    context['subscriber'] = subscriber
    batch_type = str(rp.get("shipping_direction"))
    batch_status = str(rp.get("status"))
    # print "batch_status: ",batch_status

    if batch_status != "New":
       messages.warning(request,"Batch status can only be 'New' for newly created batches")
       return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))

    else:
       if request.method == "POST":
           form = BatchForm(request.POST, request.FILES)
           if form.is_valid():
               create_batch_form = form.save(commit=False)
            #    create_batch_form.user = request.user

               # if batch_type == "export":
               # create_batch_form.batch_number = getBatchNumber(batch_type)
               # elif batch_type == "import":

               create_batch_form.batch_number = getBatchNumber(batch_type)
               create_batch_form.subscriber = subscriber
               create_batch_form.created_on = timezone.now()
               create_batch_form.status = batch_status
               create_batch_form.batch_type = batch_type
               create_batch_form.freight_type = str(rp.get('freight_type'))
               create_batch_form.save()

               return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))

           else:
               print form.errors

       return render(request,template_name,context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def getbatchitem(request):
	context = {}
	form = BatchForm(request.POST, request.FILES)
	template_name = 'sokohaliAdmin/batches.html'
	rp = request.POST
	batch_num = str(rp.get('btch_num')).lstrip()
	print "batch_number: ",batch_num
	number_batch = str(rp.get('update_batch_number')).lstrip()
	batch_fetched = Batch.objects.get(batch_number=batch_num)
	if batch_fetched:
		# if batch_fetched.batch_type == "export":
		# 	pkg_count = batch_fetched.exportpackage_set.all().count()
		# else:
		# 	pkg_count = batch_fetched.importpackage_set.all().count()
		pkg_count = batch_fetched.shippingpackage_set.all().count()
		return JsonResponse({'shipping_method':batch_fetched.shipping_method,'pkg_count':pkg_count,'awb_doc':str(batch_fetched.awb_doc),
			'carrier':batch_fetched.carrier, 'freight_type':batch_fetched.freight_type,'batch_type':batch_fetched.batch_type,'btch_number':batch_num,
			'batch_status':batch_fetched.status,'bol_doc':str(batch_fetched.bol_doc),'total_pellets':batch_fetched.total_pellets,
			'booking_ref':batch_fetched.booking_ref,'departure_date':batch_fetched.departure_date,'arrival_date':batch_fetched.arrival_date,
			'harzmat_status':batch_fetched.harzmat_status,'clearing_cost':batch_fetched.clearing_cost,'port_of_exit':batch_fetched.port_of_exit,
			'port_of_arrival':batch_fetched.port_of_arrival,'shipping_cost_D':batch_fetched.shipping_cost_D})
	else:
		return render(request,template_name,context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def update_batch(request):
    marketer = marketing_member(request)
    context = {}
    form = BatchForm()
    rp = request.POST
    referer = redirect(request.META['HTTP_REFERER'])
    number_batch = str(rp.get('update_batch_number'))
    curr_btch_st = str(rp.get('current_batch_status'))[3:].capitalize()

    freight_type = str(rp.get('freight_type'))
    carrier = str(rp.get('carrier')).lstrip()
    current_time = datetime.today()
    batchToEdit = Batch.objects.get(batch_number=number_batch)
    old_status = batchToEdit.status
    curr_btch_st_rank = get_batch_rank(curr_btch_st)
    old_batch_rank = get_batch_rank(old_status)

    try:
    	title = str(request.storefront_name)
    except:
    	title = str(marketer.storefront_name)

    # print "packages in batch: ",batchToEdit.get_packages_in_batch()
    print "old_status - curr_btch_st: ", old_status,curr_btch_st
    print "old_batch_rank - curr_btch_st_rank: ", old_batch_rank,curr_btch_st_rank

    if len(batchToEdit.get_packages_in_batch()) == 0 and not batchToEdit.status == "New":
    	messages.warning(request,"You cannot update an empty batch")
    	return referer

    elif len(batchToEdit.get_packages_in_batch()) == 0 and batchToEdit.status == "New":
    	if not curr_btch_st == "New":
    		messages.warning(request,"Updated empty batch status must be 'New' ")
    		return referer
    	else:
    		if request.method == "POST":
			print 'rP:',request.POST
			form = BatchForm(request.POST, request.FILES, instance=batchToEdit)
			if form.is_valid():
				create_batch_form = form.save(commit=False)

				create_batch_form.carrier = carrier
				create_batch_form.status = curr_btch_st
				create_batch_form.freight_type = freight_type
				create_batch_form.total_pellets = rp.get('update_total_pellets')
				create_batch_form.port_of_exit = rp.get('update_port_of_exit')
				create_batch_form.port_of_arrival = rp.get('update_port_of_arrival')
				create_batch_form.booking_ref = rp.get('update_booking_ref')
				create_batch_form.departure_date  = rp.get('update_departure_date')
				create_batch_form.arrival_date = rp.get('update_arrival_date')
				create_batch_form.clearing_cost = rp.get('update_clearing_cost')
				create_batch_form.harzmat_status = rp.get('update_harzmat_status')
				create_batch_form.notes1 = rp.get('update_notes1')
				create_batch_form.shipping_cost_D = rp.get('update_shipping_cost_D')
				create_batch_form.pkg_count = rp.get('update_pkg_count')
				create_batch_form.notes2 = rp.get('updates_notes2')
				create_batch_form.save()

				batchToEdit.batchedithistory = BatchEditHistory.objects.get_or_create(user=request.user,batch=batchToEdit,
						updated_on=current_time,batch_status=curr_btch_st)
				batchToEdit.save()

    			messages.success(request,"Successful")
    			return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))

    else:
	    if (old_batch_rank[0] + 1 == curr_btch_st_rank[0]) or (old_batch_rank[0] == curr_btch_st_rank[0]):
    		if request.method == "POST":
			print 'rP:',request.POST
			form = BatchForm(request.POST, request.FILES, instance=batchToEdit)
			if form.is_valid():
				create_batch_form = form.save(commit=False)

				create_batch_form.carrier = carrier
				create_batch_form.status = curr_btch_st
				create_batch_form.freight_type = freight_type
				create_batch_form.total_pellets = rp.get('update_total_pellets')
				create_batch_form.port_of_exit = rp.get('update_port_of_exit')
				create_batch_form.port_of_arrival = rp.get('update_port_of_arrival')
				create_batch_form.booking_ref = rp.get('update_booking_ref')
				create_batch_form.departure_date  = rp.get('update_departure_date')
				create_batch_form.arrival_date = rp.get('update_arrival_date')
				create_batch_form.clearing_cost = rp.get('update_clearing_cost')
				create_batch_form.harzmat_status = rp.get('update_harzmat_status')
				create_batch_form.notes1 = rp.get('update_notes1')
				create_batch_form.shipping_cost_D = rp.get('update_shipping_cost_D')
				create_batch_form.pkg_count = rp.get('update_pkg_count')
				create_batch_form.notes2 = rp.get('updates_notes2')
				create_batch_form.save()

				batchToEdit.batchedithistory = BatchEditHistory.objects.get_or_create(user=request.user,batch=batchToEdit,
						updated_on=current_time,batch_status=curr_btch_st)
				batchToEdit.save()

				# if batchToEdit.batch_type == "import":
				# 	pkgs = batchToEdit.importpackage_set.all()
				# else:
				# 	pkgs = batchToEdit.exportpackage_set.all()

				pkgs = batchToEdit.shippingpackage_set.all()

				for pkg in pkgs:
					if curr_btch_st == "New":
						pass
					else:
						pkg.status = curr_btch_st
					pkg.save()

					# if pkg.shipment_type == "export":
					# 	pkg_model = "ExportPackage"
					# else:
					# 	pkg_model = "ImportPackage"

					pkg_model = "ShippingPackage"

					status = 'The status of this package was updated to ' + pkg.status + " by " + request.user.username

					pkg_status_list(pkg.pk,pkg_model,request.user,status)

					try:
						#user = User.objects.get(email=post.user.email)
						user = get_marketing_member_user(request, pkg.user.username)
						subject = "%s-%sPackage ID" %(request.storefront_name.title(), pkg.tracking_number)
						sokohali_sendmail(request, user, subject, "email/batchupdate_email.html", pkg)
						print 'email was sent to',user
					except Exception as e:
						print "email not sent because:  %s" %(str(e))
						pass

				messages.success(request, "The Selected batch(es) status has been sucessfully updated")
				return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))

			else:
				print form.errors
				return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))
	    else:
	    	messages.warning(request, "Please update batches in the correct order")
	    	return referer

	    return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def print_manifest(request, pk):
	batch = get_object_or_404(Batch, pk=pk)
   	# import_packaged_items_assigned_to_batch = ShippingItem.objects.filter(package__batch_assigned = batch)
	packages_assigned_to_batch = ShippingPackage.objects.filter(batch_assigned = batch)
	return render_to_response('sokohaliAdmin/print-manifest.html',
					   {'batch': batch, #'shipments': shipments,
							'packages_assigned_to_batch':[pkg.package_info() for pkg in packages_assigned_to_batch]},
							context_instance=RequestContext(request))

	# if batch.batch_type == "import":
	#    # import_packaged_items_assigned_to_batch = ShippingItem.objects.filter(package__batch_assigned = batch)
	#    import_packages_assigned_to_batch = ShippingPackage.objects.filter(batch_assigned = batch)
	#    return render_to_response('sokohaliAdmin/print-manifest.html',
	# 						   {'batch': batch, #'shipments': shipments,
	# 							'import_packages_assigned_to_batch':[pkg.package_info() for pkg in import_packages_assigned_to_batch]},
	# 							context_instance=RequestContext(request))

	# else:
	#    # export_packaged_items_assigned_to_batch = ExportItem.objects.filter(package__batch_assigned = batch)
	#    export_packages_assigned_to_batch = ExportPackage.objects.filter(batch_assigned = batch)
	#    return render_to_response('sokohaliAdmin/print-manifest.html',
	# 						   {'batch': batch, #'shipments': shipments,
	# 						   # 'ca_packaged_items_assigned_to_batch': ca_packaged_items_assigned_to_batch},
	# 							'export_packages_assigned_to_batch':[pkg.package_info() for pkg in export_packages_assigned_to_batch]},
	# 							context_instance=RequestContext(request))


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def awb(request):
	context = {}

	if request.POST:

		awb_form = AwbForm(request.POST or None)
		if awb_form.is_valid():

			awb = awb_form.save(commit=False)
			awb.value_for_custom = request.POST['value_for_custom']
			# print "value_for_custom : ", awb.value_for_custom
			awb.batch = request.POST['batch_number']
			awb.gross_weight = request.POST['gross_weight']
			weight = awb.gross_weight
			# print"weight", weight
			awb.other_charges_due_carrier = request.POST['other_charges_due_carrier']
			charge = awb.other_charges_due_carrier
			# print"charge", charge
			awb.total_prepaid = float(awb.gross_weight) + float(awb.other_charges_due_carrier)
			awb.batch_airwaybill = Batch.objects.get(batch_number =awb.batch)
			awb.save()

			return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))
		else:
			print awb_form.errors
	else:
		return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))

	return render(request, 'sokohaliAdmin/batches.html', {'awb_form':awb_form})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
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
		if dock_form.is_valid():
			dock = dock_form.save(commit=False)
			dock.created_by = created_by
			# dock.tracking_number = request.POST['tracking_number']
			# print"Batch :",dock.tracking_number
			dock.arrival_date = str(request.POST.get('arrival_date'))
			print"Arrived Date :",dock.arrival_date
			dock.arrived_time = request.POST['arrived_time']
			dock.unloaded_date = request.POST['unloaded_date']
			dock.unloaded_time = request.POST['unloaded_time']
			dock.date_from_receiving_clerk = request.POST['date_from_receiving_clerk']
			dock.save()

			return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))
		else:
			print dock_form.errors
	else:
		return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))

	return render(request, 'sokohaliAdmin/batches.html', {'dock_form':dock_form})


@login_required
def awb_template(request, batch_number):
	context = {}
	bill_detail = get_object_or_404(AirwayBill, batch=batch_number)
	# print "Bill Detail : ", bill_detail
	# print "Shippers Name and Address : ", bill_detail.shippers_name_and_address
	return render(request, 'sokohaliAdmin/shipping-doc.html', {'bill_detail':bill_detail})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def form_edit(request):
	if request.method =="POST":

		context = {}
		# print "I am here"
		batch_number = request.POST.get('batch_number')

		each_awb = get_object_or_404(AirwayBill, batch=batch_number)
		# print"Batch Number is : ", each_awb.shippers_name_and_address
		# return JsonResponse({'each_awb':each_awb})

	return render(request, "sokohaliadmin_snippet/editbatch.html", {'each_awb':each_awb})



@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def form_update(request):
	rp = request.POST
	# print "rp", rp
	context ={}
	if request.method == "POST":
		batch_number = rp.get('batch_number')
		# print"BATCH : ", batch_number

		gross_weight = rp.get('gross_weight')
		other_charges_due_carrier = rp.get('other_charges_due_carrier')
		total_prepaid = gross_weight + other_charges_due_carrier

		itemToEdit = get_object_or_404(AirwayBill, batch=batch_number)

		itemToEdit.shippers_name_and_address = rp.get('shippers_name_and_address')
		# print"Shippers Name: ", shippers_name_and_address
		itemToEdit.shippers_number = rp.get('shippers_number')
		itemToEdit.shippers_acct_no = rp.get('shippers_acct_no')
		itemToEdit.consignees_name_and_address = rp.get('consignees_name_and_address')
		itemToEdit.consignees_number = rp.get('consignees_number')
		itemToEdit.consignees_acct_no = rp.get('consignees_acct_no')
		itemToEdit.carrier_agent_name_and_city = rp.get('carrier_agent_name_and_city')
		itemToEdit.carrier_agent_iata_code = rp.get('carrier_agent_iata_code')
		itemToEdit.agent_acct_no = rp.get('agent_acct_no')
		itemToEdit.airport_of_departure =rp.get('airport_of_departure')
		itemToEdit.origin_routing_code = rp.get('origin_routing_code')
		itemToEdit.origin_airline_carrier = rp.get('origin_airline_carrier')
		itemToEdit.destination_and_departure_routing_code1 = rp.get('destination_and_departure_routing_code1')
		itemToEdit.second_airline_carrier = rp.get('second_airline_carrier')
		itemToEdit.state_of_destination = rp.get('state_of_destination')
		itemToEdit.third_airline_carrier = rp.get('third_airline_carrier')
		itemToEdit.airport_of_destination =rp.get('airport_of_destination')
		itemToEdit.requested_flight_and_date1 = rp.get('requested_flight_and_date1')
		itemToEdit.requested_flight_and_date2 = rp.get('requested_flight_and_date2')
		itemToEdit.handling_info = rp.get('handling_info')
		itemToEdit.issued_airline_carrier_and_address = rp.get('issued_airline_carrier_and_address')
		itemToEdit.accounting_info = rp.get('accounting_info')
		itemToEdit.ref_number = rp.get('ref_number')
		itemToEdit.currency_code = rp.get('currency_code')
		itemToEdit.value_for_carriage =rp.get('value_for_carriage')
		itemToEdit.value_for_custom = rp.get('value_for_custom')
		itemToEdit.amount_of_insurance =rp.get('amount_of_insurance')
		itemToEdit.number_of_pieces_to_ship = rp.get('number_of_pieces_to_ship')
		itemToEdit.gross_weight =rp.get('gross_weight')
		itemToEdit.chargeable_rate = rp.get('chargeable_rate')
		itemToEdit.note_on_the_package = rp.get('note_on_the_package')
		itemToEdit.nature_and_quantity_of_goods = rp.get('nature_and_quantity_of_goods')
		itemToEdit.regulation_of_goods = rp.get('regulation_of_goods')
		itemToEdit.tracking_number_prefix = rp.get('tracking_number_prefix')
		itemToEdit.airline_tracking_number = rp.get('airline_tracking_number')
		itemToEdit.other_charges_due_carrier = rp.get('other_charges_due_carrier')
		itemToEdit.total_prepaid = total_prepaid
		itemToEdit.shippers_name = rp.get('shippers_name')
		itemToEdit.carrier_name = rp.get('carrier_name')
		itemToEdit.place_of_execution = rp.get('place_of_execution')

		itemToEdit.save()

	return HttpResponseRedirect(reverse('sokohaliAdmin:batch-manager'))


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def dock_form_edit(request):
	if request.method =="POST":

		context = {}
		# print "I am here"
		batch_number = request.POST.get('batch_number')

		dock_form = get_object_or_404(DockReceipt, batch=batch_number)
		# print"Batch Number is : ", each_awb.shippers_name_and_address
		# return JsonResponse({'each_awb':each_awb})
	else:
		dock_form = DockReceiptForm

	return render(request, "sokohaliadmin_snippet/editdock.html", {'dock_form':dock_form})



@login_required
@csrf_exempt
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def batch_promo(request, action, pk = None):
	context = {}
	template = 'admin-snippet/batch-promo-snippet.html'
	if action == "fetch-promos":
		existing_promos  =   BatchPromo.objects.filter(is_active = True)
		context['promos']  =  existing_promos
	elif action == "create-new":
		rp = request.POST
		new_promo = BatchPromo.objects.create(
			origin = rp['origin'],
			destination = rp['destination'],
			weight_range_at_rate = rp['weight_range_at_rate'],
			current_rate = rp['current_rate'],
			is_active = rp.get('is_active',False),
			shipment_type = rp['shipment_type'],
			estimated_departure_time = rp['estimated_departure_time'],
			available_space = rp['available_space']
			)
		if new_promo.is_active:
			BatchPromo.objects.filter(shipment_type = new_promo.shipment_type, is_active = True).exclude(pk = new_promo.pk).update(is_active = False)
		existing_promos       =   BatchPromo.objects.all()
		context['promos']     =  existing_promos
	elif action == "edit":
		pk = request.GET.get('promo_id', "")
		promo = get_object_or_404(BatchPromo, pk = pk)
		form = BatchPromoForm(initial = promo)
		context['promo_form']  = form
		#  render form to a differnt template snippet and replace existing form

	return render(request, template, context)


def staff_login_access(request):
	if check_cookie(request, 'admin_username'):
		admin_username = request.COOKIES['admin_username']
		request_by_user = get_marketing_member_user(request, admin_username)
		# print "Requested by User :", request_by_user
		if request_by_user.is_staff:
			if request.method == 'POST':
				email = request.POST['email']
				# print "Email :",email
				u = User.objects.get(email=email)
				u =u.username
				print "U :", u
				try:
					print "Got Here"
					# user = get_marketing_member_user(request, None, email)
					user = get_marketing_member_user(request, u)
					# print "User :",user
					#user.backend = 'django.contrib.auth.backends.ModelBackend'
					user.backend = 'backends.EmailAuthBackEnd'

					if user.is_staff:
						return HttpResponse("Access Denied!!! You cannot access a staff account via this channel.")
					else:
						login(request, user)
						return redirect('/')
						#request.session['admin_username'] = admin_username
						#return redirect(reverse('general:my_account'))
				except Exception as e:
					return HttpResponse('The E-mail Address you have provided does not match any record in the Database, please go back and try again. %s' %e)
			else:
				return HttpResponse('Failed')
		else:
			return redirect(reverse('access_denied'))
	else:
		return HttpResponse("ATTENTION!!! The system has failed to recognize if you are a member of staff or not. n\
						  Please login as a staff and try again")


@login_required
@csrf_exempt
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def pkg_final_updates(request):
	'''who can update a package should be taken care of in the template'''
	#print "i got here"
	try:
		mm = marketing_member(request)
		subscriber = "marketer"
	except:
		subscriber = request.user.subscriber
	referer = redirect(request.META['HTTP_REFERER'])
	context = {}
	rp = request.POST
	accepted_updates_list = ['Processing for delivery','Ready for collection','Enroute to delivery']
	update_type = str(rp.get("update_type"))
	old_status = str(rp.get("old_pkg_status")).split(",")
	marketers = str(rp.get("marketers")).split(",")

	# print "the status:",old_status
	# print "the Rank:", get_batch_rank(old_status[0])
	print "the marketers list: ",marketers

	pkg_ids = str(rp.get("pkg_ids")).split(",")
	current_time = datetime.today()
	new_pkg_rank = get_pkg_rank(update_type)
	old_pkg_rank = get_pkg_rank(old_status[0])
	print "old_status,new_status: ", old_status, update_type
	print "old_pkg_rank,new_pkg_rank: ", old_pkg_rank,new_pkg_rank

	try:
		title = str(request.storefront_name)
	except:
		title = str(mm.storefront_name)

	if len(old_status) > 1:
		if not all_same(marketers):
			messages.warning(request,"Note that you cannot carry out this action on packages whose destination warehouse is 'NOT' owned by you")
		elif not all_same(old_status):
			messages.warning(request,"Cannot updates Packages with different statuses")
		elif all_same(old_status):
			if old_status[0] not in accepted_updates_list:
				messages.warning(request,"Cannot update Packages that have not been 'Processed', 'Assigned to Batch' or in a batch that is not in 'Processing For Delivery' stage")

			elif old_pkg_rank[0] + 1 >= new_pkg_rank[0]:
				for pkg_id in pkg_ids:

					pkgToEdit = ShippingPackage.objects.get(id=pkg_id)
					pkg_model = "ShippingPackage"
					# try:
					# 	pkgToEdit = ShippingPackage.objects.get(id=pkg_id)
					# 	pkg_model = "ShippingPackage"
					# except:
					# 	pkgToEdit = ExportPackage.objects.get(id=pkg_id)
					# 	pkg_model = "ExportPackage"

					pkgToEdit.status = update_type
					pkgToEdit.save()
					pkg_status_list(pkgToEdit.pk,pkg_model,request.user,pkgToEdit.status)

					try:
						pkg = pkgToEdit
						user = get_marketing_member_user(request, pkg.user.username)
						subject = "Package Update"
						sokohali_sendmail(request, user, subject, "email/batchupdate_email.html", pkg)
				  	except Exception as e:
				  		print "email not sent because:  %s" %(e)
				  		pass

				messages.success(request, "The Selected Package(es) status has been sucessfully updated")
			else:
				messages.warning(request, "Please update Packages in the correct order")

	else:
		if marketers[0] != str(request.user.useraccount.marketer):
			messages.warning(request,"Note that you cannot carry out this action on a package whose destination warehouse is 'NOT' owned by you")

		elif not all_same(old_status):
			messages.warning(request,"Cannot updates Packages with different statuses")

		elif all_same(old_status):
			if old_status[0] not in accepted_updates_list:
				messages.warning(request,"Cannot update Packages that have not been 'Processed', 'Assigned to Batch' or in a batch that is not in 'Processing For Delivery' stage")

			elif old_pkg_rank[0] + 1 >= new_pkg_rank[0]:
				for pkg_id in pkg_ids:
					pkgToEdit = ShippingPackage.objects.get(id=pkg_id)
					pkg_model = "ShippingPackage"

					# try:
					# 	pkgToEdit = ShippingPackage.objects.get(id=pkg_id)
					# 	pkg_model = "ShippingPackage"
					# except:
					# 	pkgToEdit = ExportPackage.objects.get(id=pkg_id)
					# 	pkg_model = "ExportPackage"

					pkg_batch = pkgToEdit.batch_assigned

					pkgToEdit.status = update_type
					pkgToEdit.save()
					pkg_status_list(pkgToEdit.pk,pkg_model,request.user,pkgToEdit.status)

					try:
						pkg = pkgToEdit
						user = get_marketing_member_user(request, pkg.user.username)
						subject = "Package Update"
						sokohali_sendmail(request, user, subject, "email/batchupdate_email.html", pkg)
					except Exception as e:
						print "email not sent because:  %s" %(e)
				        pass

				messages.success(request, "The Selected Package(es) status has been sucessfully updated")
			else:
				messages.warning(request, "Please update Packages in the correct order")

	return referer


@login_required
@csrf_exempt
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def del_cncl_package(request,item_id,action):
	if action == 'delete':
		# if item_id[0] == 'E':
		# 	pkg_to_del = ExportPackage.objects.get(tracking_number=item_id)
		# else:
		# 	pkg_to_del = ShippingPackage.objects.get(tracking_number=item_id)
		pkg_to_del = ShippingPackage.objects.get(tracking_number=item_id)

		pkg_to_del.deleted = True
		pkg_to_del.save()

	elif action == 'revert':
		# if item_id[0] == 'E':
		# 	pkg_to_del = ExportPackage.objects.get(tracking_number=item_id)
		# else:
		# 	pkg_to_del = ShippingPackage.objects.get(tracking_number=item_id)
		pkg_to_del = ShippingPackage.objects.get(tracking_number=item_id)

		pkg_to_del.status = "New"
		pkg_to_del.save()

	else:
		# if item_id[0] == 'E':
		# 	pkg_to_cncl = ExportPackage.objects.get(tracking_number=item_id)
		# else:
		# 	pkg_to_cncl = ShippingPackage.objects.get(tracking_number=item_id)
		pkg_to_del = ShippingPackage.objects.get(tracking_number=item_id)

		pkg_to_cncl.status = 'cancelled'
		pkg_to_cncl.save()

	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def apply_discount(request):
	rp = request.POST
	print "rp: ",rp
	pkg_num = str(rp.get('pkg_disc_id'))
	pkg_discount = float(rp.get('pkg_disc_num'))

	pkg_obj = ShippingPackage.objects.get(tracking_number=pkg_num)
	pkg_model = "ShippingPackage"
	discount_D = (pkg_discount * pkg_obj.admin_total_payable_D) / 100
	discount_N = (pkg_discount * pkg_obj.admin_total_payable_N) / 100

	pkg_obj.discount_percentage = pkg_discount
	pkg_obj.discount_D = discount_D
	pkg_obj.discount_N = discount_N

	if pkg_obj.balance_paid_D == 0:
		pkg_obj.balance_D = pkg_obj.admin_total_payable_D - discount_D
		pkg_obj.balance_N = pkg_obj.admin_total_payable_N - discount_N
	else:
		if pkg_obj.balance_paid_D < (pkg_obj.admin_total_payable_D - pkg_obj.discount_D):
			pkg_obj.balance_D = pkg_obj.admin_total_payable_D - (pkg_obj.discount_D + pkg_obj.balance_paid_D)
			pkg_obj.balance_N = pkg_obj.admin_total_payable_N - (pkg_obj.discount_N + pkg_obj.balance_paid_N)
		else:
			pkg_obj.balance_D = 0.00
	 		pkg_obj.balance_N = 0.00
			amount = pkg_obj.balance_paid_N - (pkg_obj.admin_total_payable_N - pkg_obj.discount_N)

			jejepay_obj = SokoPay.objects.create(user=pkg_obj.user,purchase_type_1="Refund", purchase_type_2="Add", status = "Approved", ref_no = creditpurchase_ref(request),
			 		 amount=amount,bank="Admin", message="Excess amount added to customer sokopay wallet" )
			print "jeje", jejepay_obj

	pkg_obj.save()
	action = str(pkg_discount) + '%' + " " + "discount was applied to this package"
	status = "Applied Discount"
	#pkg_status_list(pkg_obj.pk,pkg_model,request.user,status)
	shipment_history(request.user, pkg_obj.pk,pkg_model, status,action)

	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
@csrf_exempt
def message_center(request):
	context = {}
	marketer = marketing_member(request)
	message_obj = paginate_list(request,MessageCenter.objects.filter(user__useraccount__marketer=marketer),10)
	rp = request.POST
	print "rp: ",rp

	try:
		subscriber = marketer.subscriber
	except:
		subscriber = request_subscriber(request)

	if rp.has_key('admin_message'):
		comment_obj = MessageCenterComment()
		comment_obj.message = rp.get('adm_comment')
		comment_obj.user = request.user
		comment_obj.message_obj = MessageCenter.objects.get(id=rp.get('bk_ref_id'))
		comment_obj.save()
		context['message_obj'] = message_obj

		message = MessageCenter.objects.get(id=rp.get('bk_ref_id'))
		message.new     = False
		message.replied = True
		message.replied_on = timezone.now() #present_time()
		message.save()
		context['subscriber'] = subscriber
		return render(request,'sokohaliAdmin/comments.html',context)

	else:
		context['message_obj'] = message_obj
		context['subscriber'] = subscriber
		return render(request,'sokohaliAdmin/message-center.html',context)

		# # return render(request,'sokohaliAdmin/messageCenter2.html',context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def message_status(request,status):
	mm = marketing_member(request)
	try:
		subscriber = marketer.subscriber
	except:
		subscriber = request_subscriber(request)
	context = {}
	context['subscriber'] = subscriber
	if status == "new":
		message_obj = paginate_list(request,MessageCenter.objects.filter(user__useraccount__marketer=mm,new=True),10)
	elif status == "replied":
		message_obj = paginate_list(request,MessageCenter.objects.filter(user__useraccount__marketer=mm,replied=True),10)
	else:
		message_obj = paginate_list(request,MessageCenter.objects.filter(user__useraccount__marketer=mm,archive=True,new=False,replied=False),10)
	context['message_obj'] = message_obj
	return render(request,'sokohaliAdmin/message-center.html',context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def msg_cntr_archv(request,item_id,status):
	context = {}
	message_obj = MessageCenter.objects.get(id=item_id)
	if status == "archive":
		message_obj.archive = True
		message_obj.replied = False
		message_obj.new = False
		message_obj.save()
		context['message_obj'] = message_obj
	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def get_cost(request):
	print 'rG',request.GET
	total_value = int(request.GET.get('qty')) * int(request.GET.get('rate'))
	print "total_value:",total_value
	return JsonResponse({'total_value':total_value})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
@csrf_exempt
def get_dimensions_of_package(request):

	rp = request.POST
	# print "rP: ",rp
	package = ShippingPackage.objects.get(id=rp.get('pkg_id'))
	request.session['pkg'] = package
	lb_country = package.costcalc_instance.country

	costcalc  =  create_obj_costcalc(request,lb_country)
	weightFactor   = costcalc.dim_weight_factor
	lb_kg_factor   = costcalc.lb_kg_factor
	kg_lb_factor   = costcalc.kg_lb_factor
	qty = 1

	length = float(str(rp.get('lgt')))
	width = float(str(rp.get('wdth')))
	height = float(str(rp.get('hgt')))
	weight = float(str(rp.get('wgt')))

	dim_weight = qty * (length * width * height) / weightFactor #in lbs
	dim_weight_K = dim_weight * lb_kg_factor

	weight_Actual = weight
	weight_Actual_K = weight * lb_kg_factor * qty
	del request.session['pkg']
	return render(request,'admin-snippet/get_dimensions.html',{'dms_weight_k':dim_weight_K,'dms_weight':dim_weight,'dms_actual_k':weight_Actual_K,'dms_actual':weight_Actual,'package':package})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
@csrf_exempt
def delete_admin_added_items(request):

	context = {}
	rp = request.POST
	print 'deleted'
	user_account = UserAccount.objects.get(id = str(rp.get('user_id')))
	user = User.objects.get(useraccount=user_account)
	mm = marketing_member(request)
	marketer_routes = mm.get_shipping_chains()
	print user
	item = ShippingItem.objects.get(id=rp.get('item_id')).delete()
	items = ShippingItem.objects.filter(user=user,created_by_admin=True,ordered=False,item_type=str(rp.get('item_type')))
	context['items'] = items
	context['marketer_routes'] = marketer_routes
	template_name = 'admin-snippet/cb_item_list.html'
	if str(rp.get('item_type')) == "Regular":
		if items:
			alert = "You have added Regular items for this customer"
			context['alert'] = alert
		else:
			alert = "You have not added any Regular items for this customer"
			context['alert'] = alert
	else:
		if items:
			alert = "You have added Fixed Weight items for this customer"
			context['alert'] = alert
		else:
			alert = "You have not added any Fixed weight item(s) for this customer"
			context['alert'] = alert
	return render(request,template_name,context)




@login_required
#@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def client_dashboard(request):
	context = {}

	user = request.user
	print "User :",user

	try:
		subscribers = Subscriber.objects.get(user=user)
		context['subscribers'] = subscribers
	except:
		mm = request.user.useraccount.marketer
		subscribers = mm.subscriber
		context['subscribers'] = subscribers

	try:
		print subscribers.get_warehouses()
	except:
		pass

	template_name = 'sokohaliAdmin/dashboard_table.html'

	return render(request,template_name,context)


@login_required
@csrf_exempt
def change_item_status(request):
	context= {}
	rP = request.POST
	# print 'rP:',rP
	try:
		subscriber = marketer.subscriber
	except:
		subscriber = request_subscriber(request)
	context['subscriber'] = subscriber
	package = ShippingPackage.objects.get(id=rP.get('get_pkg'))
	if rP.has_key('checked'):
		get_item = ShippingItem.objects.get(id=rP.get('get_id'))
		get_item.status = "Received"
		get_item.save()
	elif rP.has_key('unchecked'):
		get_item = ShippingItem.objects.get(id=rP.get('get_id'))
		get_item.status = "Not yet received"
		get_item.save()
	context['item'] = get_item
	context['package'] = package
	template_name = 'sokohaliAdmin/changeItemstatus.html'
	return render(request,template_name,context)


def check_user_access(request):
	# client = checkSubscriber(request)
	try:
		mm = marketing_member(request)
		subscriber = "marketer"
	except:
		subscriber = request.user.subscriber
	if subscriber != "marketer":
		return JsonResponse({"result":"fail"})
	else:
		if request.method == "GET":
			mkt_code = str(request.GET.get('track_num'))[11:15]
			print "number:",mkt_code
			if mm.random_code == mkt_code:
				return JsonResponse({"result":"OK"})
			else:
				return JsonResponse({"result":"fail"})
		else:
			return redirect(request.META['HTTP_REFERER'])
	return redirect(request.META['HTTP_REFERER'])

def getAllUsers(request):
	mm = marketing_member(request)
	get_all_users = UserAccount.objects.filter(user__useraccount__marketer = mm)
	get_users_list = [(x.username + "--" + str(x.suite_no)) for x in get_all_users]
	new_datalist = ",".join([str(item) for item in get_users_list])
	return new_datalist


@login_required
@csrf_exempt
def user_item_received(request):

	mm = marketing_member(request)

	get_all_notifications = NotifyUser.objects.filter(user__useraccount__marketer = mm)
	get_all_users = getAllUsers(request)

	# print "users",get_all_users
	try:
		subscriber = mm.subscriber
		marketer_routes = subscriber.get_all_shipping_chains()
	except:
		subscriber = request_subscriber(request)
		marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))


	context = {}
	context['datalist'] = get_all_users
	context['subscriber'] = subscriber
	context['all_notifications'] = get_all_notifications
	context['routes'] = marketer_routes

	shipping_item = ShippingItem.objects.filter(~Q(tag="Shopping"), user__useraccount__marketer=mm)
	context['shipping_item'] = shipping_item
	context['items_to_ship'] = paginate_list(request, shipping_item, 10)

	template_name = 'sokohaliAdmin/user_item_received_notification.html'

	if request.method == "POST":
		rp = request.POST
		print 'rp:',rp

		user_username = str(rp.get('id_name')).split('--')[0]
		try:
			get_user = UserAccount.objects.get(username=user_username)
		except:
			return redirect(request.META['HTTP_REFERER'])

		form = notifyUserForm(request.POST, request.FILES)

		if form.is_valid():
			create_notify_form = form.save(commit=False)
			create_notify_form.suite_no = get_user.suite_no
			create_notify_form.name = get_user.user.username
			create_notify_form.address = get_user.address
			create_notify_form.item_description = rp.get('id_desc')
			create_notify_form.last_four_digits = rp.get('id_last_four_digits')
			create_notify_form.created_by = request.user
			create_notify_form.user = get_user.user
			create_notify_form.weight = rp.get('id_wgt')
			try:
				create_notify_form.image_field = request.FILES['id_file']
			except:
				pass
			create_notify_form.save()

			shipping_item = ShippingItem.objects.create(
				user=get_user.user,
				weight=create_notify_form.weight,
				courier_tracking_number=create_notify_form.last_four_digits,
				description=create_notify_form.item_description,
				status="Received",
				created_by=request.user.username,
				notify=create_notify_form)

			pkg = create_notify_form
			print 'desc:', pkg.item_description
			print 'LFD:', pkg.last_four_digits
			user = get_user.user
			print user.username
			title = "Package Creation Notification"
			text = 'email/notify_user.html'
			try:
				sokohali_sendmail(request, user, title, text, pkg)
			except Exception as e:
				print "message was not sent because of ", e
			messages.success(request, "Notification sent sucessfully")
			return redirect(request.META['HTTP_REFERER'])
		else:
			print form.errors

	return render(request,template_name,context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def notification_label(request, notify_id):
	notify_user_item = NotifyUser.objects.get(id=notify_id)
	return render(request, 'sokohaliAdmin/notification_label.html', {'pkg': notify_user_item})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def get_fixed_weight_cat(request):
	''' get the weight of fixed weight items '''
	context = {}
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		marketer_routes = subscriber.get_all_shipping_chains()
	except:
		subscriber = request_subscriber(request)
		marketer_routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	if not request.GET.has_key('fixed_weight'):
		template_name = 'admin-snippet/new_fixed_weight.html'
	else:
		template_name = 'sokohaliAdmin/editFixedItems.html'
	chain_id = request.GET.get('chain_id')
	print "chain:", chain_id
	fixed_weight_category = FixedShipment.objects.filter(subscriber=subscriber,chain=chain_id)
	print 'cats:',fixed_weight_category
	context['fixed_weight_category'] = fixed_weight_category
	context['subscriber'] = subscriber
	return render(request,template_name,context)


@login_required
@csrf_exempt
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def override_payment(request):
	rp = request.POST
	print 'rP:',rp
	pkg_model = "ShippingPackage"
	pkg = ShippingPackage.objects.get(tracking_number=rp.get('tracking_number'))
	action = rp.get('action')
	status = action
	if action == "overide":
		action = 'Payment' + " " + action
		print "i want to override payment"
		pkg.override_payment = True
		pkg.save()
		shipment_history(request.user,pkg.id,pkg_model,status,action)
		messages.success(request, "You can now assign this package to a desired batch")
		return JsonResponse({'OK':'OK'})
	else:
		print "i dont want to override payment"
		pkg.override_payment = False
		pkg.save()
		shipment_history(request.user,pkg.id,pkg_model,status,action)
		messages.success(request, "Overide payment removed")
		return JsonResponse({'OK':'OK'})


@login_required
@csrf_exempt
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def edit_fxd_package(request,tracking_number):
	freight_VAT_SC_D = PSDG_D = VAT_D = 0.0
	print "special edit"
	context = {}
	rP = request.POST
	print "rP: ",rP
	post = get_object_or_404(ShippingPackage, tracking_number=tracking_number)

	# linked_items = ShippingItem.objects.filter(pk__in=selected_items_in_package)
	cart_value = post.items_total_value()
	item_count = post.items_count()
	shipping_weight = 0.0
	delivery_total_freight_D = post.intl_freight_D
	print "CV - ITC - SW - DTFD: ",cart_value, item_count, shipping_weight, delivery_total_freight_D

	new_tracking_number = post.tracking_number[15:].split('-')

	ship_origin = new_tracking_number[0]
	ship_destination = new_tracking_number[1]

	shipping_origin = country = get_counntry_from_short_code(ship_origin)

	shipping_destination = get_counntry_from_short_code(ship_destination)

	pkg_info = {'pkg_count': post.box_quantity, 'item_count': item_count,
														 'shippingWeight': shipping_weight, 'cart_value': cart_value, 'total_freight_D': delivery_total_freight_D}

	total_freight_D_val, VAT_D_val, totalServiceCharge_D_val, \
							CON_D_val, PSDG_D_val, SMP_D_val, freight_VAT_SC_D_val, coverage_amount_D_val, exchange_rate = CreateShipmentCostCalc(request, pkg_info, country, post.costcalc_instance)

	freight_VAT_SC_D   += freight_VAT_SC_D_val
	PSDG_D             += PSDG_D_val
	VAT_D              += VAT_D_val

	post.insurance_fee_D = PSDG_D_val
	post.insurance_fee_N = PSDG_D_val * exchange_rate

	post.VAT_charge_D = VAT_D_val
	post.VAT_charge_N = VAT_D_val * exchange_rate

	post.service_charge_D = totalServiceCharge_D_val
	post.service_charge_N = totalServiceCharge_D_val * exchange_rate

	print "FI - I - VAT - SC: ",post.intl_freight_D, post.insurance_fee_D , post.VAT_charge_D , post.service_charge_D

	if not rP.has_key('vat') and not rP.has_key('service_charge') and not rP.has_key('pkg_handling_option'):
		print "a"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N
		post.insure = False
		post.VAT_charge_D = post.VAT_charge_N = 0
		post.service_charge_D = post.service_charge_N = 0

	elif not rP.has_key('vat') and rP.has_key('service_charge') and rP.has_key('pkg_handling_option'):
		print "b"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.insurance_fee_D + post.service_charge_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.insurance_fee_N + post.service_charge_N
		post.VAT_charge_D = post.VAT_charge_N = 0
		post.insure = True

	elif not rP.has_key('vat') and not rP.has_key('service_charge') and rP.has_key('pkg_handling_option'):
		print "c"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.insurance_fee_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.insurance_fee_N
		post.VAT_charge_D = post.VAT_charge_N = 0
		post.service_charge_D = post.service_charge_N = 0
		post.insure = True

	elif not rP.has_key('vat') and rP.has_key('service_charge') and not rP.has_key('pkg_handling_option'):
		print "d"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.service_charge_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.service_charge_N
		post.insure = False
		post.VAT_charge_D = post.VAT_charge_N = 0

	elif rP.has_key('vat') and rP.has_key('service_charge') and rP.has_key('pkg_handling_option'):
		print "e"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.insurance_fee_D + post.service_charge_D + post.VAT_charge_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.insurance_fee_N + post.service_charge_N + post.VAT_charge_N
		post.insure = True

	elif rP.has_key('vat') and rP.has_key('service_charge') and not rP.has_key('pkg_handling_option'):
		print "f"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.service_charge_D + post.VAT_charge_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.service_charge_D + post.VAT_charge_D
		post.insure = False

	elif rP.has_key('vat') and not rP.has_key('service_charge') and rP.has_key('pkg_handling_option'):
		print "g"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.VAT_charge_D + post.insurance_fee_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.VAT_charge_N + post.insurance_fee_N
		post.service_charge_D = post.service_charge_N = 0

	elif rP.has_key('vat') and not rP.has_key('service_charge') and not rP.has_key('pkg_handling_option'):
		print "h"
		post.admin_total_payable_D = post.user_total_payable_D = post.intl_freight_D + post.VAT_charge_D
		post.admin_total_payable_N = post.user_total_payable_N = post.intl_freight_N + post.VAT_charge_N
		post.insure = False
		post.service_charge_D = post.service_charge_N = 0


	additional_charge = rP.get('late_charge')
	if additional_charge == "":
		additional_charge = post.additional_charges_D
	else:
		additional_charge = float(additional_charge)
	print "additional charge: ", additional_charge
	post.additional_charges_D = additional_charge
	post.additional_charges_N = post.additional_charges_D * exchange_rate
	post.user_total_payable_D = post.admin_total_payable_D = post.user_total_payable_D + post.additional_charges_D
	post.user_total_payable_N = post.admin_total_payable_N = post.user_total_payable_N + post.additional_charges_N
	post.balance_D = post.user_total_payable_D = post.admin_total_payable_D
	post.balance_N = post.admin_total_payable_N	= post.user_total_payable_N


	post.shipping_method = rP.get('pkg_ship_method')
	post.save()

	try:
		#user = User.objects.get(email=post.user.email)
		user = get_marketing_member_user(request, post.user.username)
		pkg = post
		subject = "%s Package-%s Invoice" %(request.storefront_name.title(), pkg.tracking_number)
		sokohali_sendmail(request, user, subject, "email/package_invoice_email_template.html", pkg)
		print 'email was sent to',user
	except Exception as e:
		print "email not sent because:  %s" %(str(e))
		pass

	return redirect(request.META['HTTP_REFERER'])



@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def admin_edit_item(request):
	context = {}
	try:
		mm = marketing_member(request)
		subscriber = "marketer"
	except:
		subscriber = request.user.subscriber
	template_name = "sokohaliAdmin/editItemForm.html"
	rG = request.GET
	# print "rG: ",rG
	item_id = rG.get('item_id')
	cat_id = rG.get('cat_id')
	try:
		item = ShippingItem.objects.get(id=item_id)
		item_chain = item.shipping_chain
		getFixedWeights = item_chain.get_fixed_weights()
		getItemChains = item.shipping_chain.subscriber.get_all_shipping_chains()
		context['marketer_routes'] = getItemChains
		context['item_chain'] = item_chain
		context['item'] = item= subscriber
		context['subscriber'] = subscriber
		context['fixed_weight_category'] = getFixedWeights
		context['cat_id'] = FixedShipment.objects.get(id=cat_id)
		rate = FixedShipment.objects.get(id=cat_id).unit_price_D
		# print "extra_charge", extra_charge
		context['rate'] = rate
	except:
		pass
		item = ShippingItem.objects.get(id=item_id)
		context['item'] = item
	return render(request,template_name,context)


@login_required
@csrf_exempt
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def editSpecial(request):
	try:
		mm = marketing_member(request)
		subscriber = mm.subscriber
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber), subscriber=subscriber)
	except:
		subscriber = request_subscriber(request)
		routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	rP = request.POST
	print 'rP: ',rP
	user = User.objects.get(email=rP.get('owner_id'))
	# print "user: ", user
	extra_charge = rP.get('extra_charge')
	if extra_charge:
		extra_charge = float(extra_charge)
	else:
		extra_charge = 0.0

	item_value = float(rP.get('item_val'))

	item_toEdit = ShippingItem.objects.get(pk=rP.get('item_id'))
	if rP.get('item_type') == "fixed_weight":
		item_toEdit.quantity = rP.get('qty')
	else:
		item_toEdit.quantity = rP.get('qty_reg')
		item_toEdit.courier_tracking_number = rP.get('item_tracking_number')
		print 'track_num: ',item_toEdit.courier_tracking_number
	item_toEdit.description = rP.get('desc')
	try:
		item_toEdit.shipping_chain = ShippingChain.objects.get(id=rP.get('chain_id'))
	except:
		pass
	item_toEdit.item_type = rP.get('item_type')
	item_toEdit.total_value = item_value + extra_charge
	item_toEdit.save()
	if rP.get('item_type') == "fixed_weight":
		items = ShippingItem.objects.filter(user = user,created_by_admin=True,ordered=False,item_type="fixed_weight")
	else:
		items = ShippingItem.objects.filter(user = user,created_by_admin=True, ordered=False, item_type="Regular")
	print "items:",items
	return render(request, 'admin-snippet/cb_item_list.html', {'items': items,'marketer_routes':routes,'subscriber':subscriber})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def superuser_dasboard(request):
	context = {}
	actual_subscribers = []
	subscribers = Subscriber.objects.all()
	for sub in subscribers:
		if sub.user.is_superuser or sub.shippingchain_set.all().count() == 0:
			pass
		else:
			actual_subscribers.append(sub)
	context['subscribers'] = actual_subscribers
	return render(request,'sokohali/sokohaliStaff.html', context)


@login_required
@csrf_exempt
def revoke_order(request):

	print "rP: ",request.POST
	pkg_model = "ShippingPackage"
	pkg_obj = ShippingPackage.objects.get(tracking_number = request.POST.get('track_num'))

	if request.POST.get('action') == "revoke":
		print "here"
		pkg_obj.deleted = True
		action = status = "Revoked"
	else:
		pkg_obj.deleted = False
		action = status = "Undo revoke"

	pkg_obj.save()

	text = 'email/revoking_notification.html'
	user = pkg_obj.user

	try:
		sokohali_sendmail(request, user, title, text, pkg_obj)
		shipment_history(request.user,pkg_obj.id,pkg_model,status,action)
		messages.success(request,'Order/booking has been succesfully revoked and a notification has been sent to customer')

	except Exception as e:
		print "Error occured as a result of ", e
		shipment_history(request.user,pkg_obj.id,pkg_model,status,action)
		messages.warning(request,'Order/booking has been succesfully revoked and a notification has been sent to customer')

	return redirect(request.META['HTTP_REFERER'])


@login_required
def get_delivery_time(request):
	mm = marketing_member(request)
	subscriber = mm.subscriber
	rp = request.GET
	origin = rp.get('origin')
	dest = rp.get('destination')
	ship_method = rp.get('ship_method')
	shipping_chain = ShippingChain.objects.get(origin=origin,destination=dest,subscriber=subscriber)
	if ship_method == "Air Freight":
		est_del_time = shipping_chain.air_delivery_time
	elif ship_method == "Sea Freight":
		est_del_time = shipping_chain.sea_delivery_time
	else:
		est_del_time = shipping_chain.express_delivery_time
	return JsonResponse({'result':est_del_time})


@login_required
@csrf_exempt
def ams_add_item(request):
	rp = request.POST
	print 'RP:',rp
	template_name = 'zaposta_snippet/added_items.html'
	item = ShippingItem.objects.create(
		user = request.user,
		quantity = rp.get('qty'),
		total_value = rp.get('value'),
		courier_tracking_number = rp.get('track_num'),
		description= rp.get('desc'),
		created_by_admin=False)
	items_list = ShippingItem.objects.filter(user = request.user,ordered=False, item_type="Regular")
	return render(request,template_name,{"items_list":items_list})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_member(request):
	context = {}
	dist_member = LocalDistributionMember.objects.all()
	# print "LocalDistributionMember :",dist_member
	avail_country = AvailableCountry.objects.all()
	mark_mem = MarketingMember.objects.all()

	loc_dist_mem = LocalDistributionMemberForm()
	if request.method=='POST':
		member_form = LocalDistributionMemberForm(request.POST or None)
		rp=request.POST
		# print "rP",rp

		if member_form.is_valid():
			member = member_form.save(commit=False)

			if LocalDistributionMember.objects.filter(courier_name = rp.get('courier_name')).exists():
				print 'courier name exists'
				messages.error(request, 'Courier name already exist.')
				return redirect(request.META['HTTP_REFERER'])

			country = request.POST['country'].partition(' ')[0]
			if country != "------------":
				member.country = AvailableCountry.objects.get(name =country)
			# print "Avail Country :", member.country

			marketing_member  = request.POST.get('marketing_member')
			if marketing_member != "------------":
				# print "marketing_member :", marketing_member
				member.marketing_member = MarketingMember.objects.get(storefront_name =marketing_member)
			# print "marketing_member :", marketing_member

			member.save()
			messages.success(request, 'Local Distribution Member added successfully')

			return redirect(request.META['HTTP_REFERER'])
		else:
			messages.error(request, 'Please correct the error below.')

	context['dist_member'] = dist_member
	context['loc_dist_mem'] = loc_dist_mem
	context['avail_country'] = avail_country
	context['mark_mem'] = mark_mem
	return render(request, 'sokohali/LocalDistMember.html', context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_member_edit(request):
	context = {}
	# mem_form = LocalDistributionMemberForm()
	if request.method =="POST":

		item_id = request.POST.get('item_id')
		print "item_id :", item_id

		mem_form = get_object_or_404(LocalDistributionMember, id=item_id)
		print"mem_form is : ", mem_form
		avail_country = AvailableCountry.objects.all()
		print "avail_country :", avail_country
		mark_mem = MarketingMember.objects.all()
		print "mark_mem :", mark_mem
	else:
		# mem_form = LocalDistributionMemberForm()
		print"Error"

	context['mem_form'] = mem_form
	context['avail_country'] = avail_country
	context['mark_mem'] = mark_mem
	return render(request, 'sokohali/LocalDistMember.html', context)




@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def edit_local_dist_member(request):
	context={}
	rp = request.POST
	print "rp", rp
	if request.method == "POST":
		item_id=rp.get('id')
		print "item_id :",item_id

		itemToEdit=get_object_or_404(LocalDistributionMember , id=item_id)
		itemToEdit.courier_name = rp.get('courier_name')
		country  = rp.get('country').partition(' ')[0]
		if country != "------------":
			itemToEdit.country = AvailableCountry.objects.get(name =country)

		itemToEdit.active = rp.get('active')
		itemToEdit.has_api = rp.get('has_api')
		itemToEdit.has_configured_rates = rp.get('has_configured_rates')
		marketing_member  = rp.get('marketing_member')
		if marketing_member != "------------":
			itemToEdit.marketing_member  = MarketingMember.objects.get(storefront_name =marketing_member)

		itemToEdit.save()

	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def view_region(request):
	context = {}
	# mem_form = LocalDistributionMemberForm()
	if request.method =="POST":
		if request.is_ajax():

			item_id = request.POST.get('item_id')
			print "item_id :", item_id
			value = request.POST.get('value')
			print "value :", value

			regions = LocalDistributorRegion.objects.filter(courier__courier_name=value)
			print "regions :",regions
	else:
		print"Error"

	context['regions'] = regions
	return render(request, 'sokohali/LocalDistMember.html', context)



@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def shoppingManager(request):
	mm = marketing_member(request)
	context = {}
	template_name = 'sokohaliAdmin/shoppingManager.html'
	items = ShippingItem.objects.filter(deleted=False,archive=False)
	context['shopping_obj'] = items
	context['shoppingRequest'] = paginate_list(request, items, 10)
	return render(request, template_name, context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def view_location(request):
	context = {}
	# mem_form = LocalDistributionMemberForm()
	if request.method =="POST":
		if request.is_ajax():

			item_id = request.POST.get('item_id')
			print "item_id :", item_id
			value = request.POST.get('value')
			print "value :", value

			locations = LocalDistributorLocation.objects.filter(region__name=value)
			print "locations :",locations
	else:
		print"Error"

	context['locations'] = locations
	return render(request, 'sokohali/LocalDistRegion.html', context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_region(request):
	context = {}
	dist_region = LocalDistributorRegion.objects.all()
	dist_member = LocalDistributionMember.objects.filter(has_api=False)

	loc_dist_reg = LocalDistributorRegionForm()
	if request.method=='POST':
		region_form = LocalDistributorRegionForm(request.POST or None)
		rp=request.POST
		# print "rP",rp

		if region_form.is_valid():
			region = region_form.save(commit=False)

			if LocalDistributorRegion.objects.filter(name = rp.get('name')).exists():
				print 'name exists'
				messages.error(request, 'Name already exist.')
				return redirect(request.META['HTTP_REFERER'])

			courier  = request.POST.get('courier')
			region.courier = LocalDistributionMember.objects.get(courier_name =courier)
			print "courier :", courier

			region.save()
			messages.success(request, 'Local Distributor Location added successfully')

			return redirect(request.META['HTTP_REFERER'])
		else:
			messages.error(request, 'Please correct the error below.')

	context['dist_region'] = dist_region
	context['dist_member'] = dist_member
	context['loc_dist_reg'] = loc_dist_reg
	return render(request, 'sokohali/LocalDistRegion.html', context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_region_edit(request):
	context = {}
	# mem_form = LocalDistributionMemberForm()
	if request.method =="POST":

		item_id = request.POST.get('item_id')
		print "item_id :", item_id

		mem_form = get_object_or_404(LocalDistributorRegion, id=item_id)
		print"mem_form is : ", mem_form
		mark_mem = LocalDistributionMember.objects.all()
		print "mark_mem :", mark_mem
	else:
		# mem_form = LocalDistributionMemberForm()
		print"Error"

	context['mem_form'] = mem_form
	context['mark_mem'] = mark_mem
	return render(request, 'sokohali/LocalDistRegion.html', context)




@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def edit_local_dist_region(request):
	context={}
	rp = request.POST
	print "rp", rp
	if request.method == "POST":
		item_id=rp.get('id')
		print "item_id :",item_id

		itemToEdit=get_object_or_404(LocalDistributorRegion , id=item_id)

		courier=rp.get('courier')
		# print "Name",courier
		itemToEdit.courier = LocalDistributionMember.objects.get(courier_name =courier)

		itemToEdit.name = rp.get('name')

		itemToEdit.save()

	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_location(request):
	context = {}
	dist_location = LocalDistributorLocation.objects.all()
	# dist_members = LocalDistributionMember.objects.all()
	dist_member = LocalDistributionMember.objects.filter(has_api=False)
	# print "dist_member", dist_member
	dist_region = LocalDistributorRegion.objects.all()
	loc_dist_loc = LocalDistributorLocationForm()

	if request.method=='POST':
		location_form = LocalDistributorLocationForm(request.POST or None)
		rp=request.POST
		# print "rP",rp

		if location_form.is_valid():
			location = location_form.save(commit=False)
			location.name = request.POST.get('name')
			location.country = request.POST.get('country')
			location.state = request.POST.get('state')
			name = request.POST.get('name')
			regions = request.POST.get('region')#.rsplit(' ')
			print "Region :",regions
			reg = regions.replace(location.name, '')
			print "New Region :", reg
			if  name in regions:
				location.region = LocalDistributorRegion.objects.get(name = reg, courier__courier_name = name)
				location.save()

				messages.success(request, 'Local Distributor Location added successfully')
			else:
				messages.error(request, 'Courier Name did not match with Selected Region.')

			return redirect(request.META['HTTP_REFERER'])
		else:
			messages.error(request, 'Please correct the error below.')

	page=request.GET.get('page',1)
	paginator=Paginator(dist_location,50)

	try:
		location=paginator.page(page)
	except PageNotAnInteger:
		location=paginator.page(1)
	except EmptyPage:
		location=paginator.page(paginator.num_pages)

	context['location'] = location
	context['dist_member'] = dist_member
	context['loc_dist_loc'] = loc_dist_loc
	context['dist_region'] = dist_region
	return render(request, 'sokohali/LocalDistLocation.html', context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_location_edit(request):
	context = {}
	# mem_form = LocalDistributionMemberForm()
	if request.method =="POST":

		item_id = request.POST.get('item_id')
		print "item_id :", item_id

		loc_form = get_object_or_404(LocalDistributorLocation, id=item_id)
		# print"mem_form is : ", mem_form
		mark_mem = LocalDistributionMember.objects.filter(has_api=False)
		# print "mark_mem :", mark_mem
		dist_reg = LocalDistributorRegion.objects.all()
	else:
		# mem_form = LocalDistributionMemberForm()
		print"Error"

	context['loc_form'] = loc_form
	context['mark_mem'] = mark_mem
	context['dist_reg'] = dist_reg
	return render(request, 'sokohali/LocalDistLocation.html', context)


def edit_local_dist_location(request):
	context={}
	rp = request.POST
	print "rp", rp
	if request.method == "POST":
		item_id=rp.get('id')
		print "item_id :",item_id

		itemToEdit=get_object_or_404(LocalDistributorLocation , id=item_id)
		itemToEdit.name = rp.get('name')
		itemToEdit.address1 = rp.get('address1')
		itemToEdit.address2 = rp.get('address2')
		itemToEdit.city = rp.get('city')
		itemToEdit.state = rp.get('state')
		itemToEdit.country = rp.get('country')
		itemToEdit.phone_number = rp.get('phone_number')
		itemToEdit.zip_code = rp.get('zip_code')
		itemToEdit.pickup_available = rp.get('pickup_available')
		itemToEdit.drop_off_available = rp.get('drop_off_available')
		itemToEdit.offered_location = rp.get('offered_location')

		name = request.POST.get('name')
		regions = request.POST.get('region')#.rsplit(' ')
		print "Region :",regions
		reg = regions.replace(name, '')
		print "New Region :", reg
		if  name in regions:
			itemToEdit.region = LocalDistributorRegion.objects.get(name = reg, courier__courier_name = name)
			itemToEdit.save()

			messages.success(request, 'Local Distributor Location edited successfully')
		else:
			messages.error(request, 'Courier Name did not match with Selected Region.')

		return redirect(request.META['HTTP_REFERER'])

	return render(request, 'sokohali/LocalDistLocation.html', context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def local_dist_price(request):
	context = {}
	# dist_region = LocalDistributorRegion.objects.all()
	dist_price = LocalDistributorPrice.objects.all()
	# print "LocalDistributionLocation :",dist_location
	loc_dist_pr = LocalDistributorPriceForm()
	dist_member = LocalDistributionMember.objects.filter(has_api=False)

	regions = LocalDistributorRegion.objects.filter(courier__courier_name=request.GET.get('member')).values_list('name', flat=True)
	print "RE", regions
	## for region in regions:
	## 	print "Regions", region.name
	context['regions'] = regions

	if request.method=='POST':
		price_form = LocalDistributorPriceForm(request.POST or None)
		rp=request.POST
		# print "rP",rp

		if price_form.is_valid():
			loc_price = price_form.save(commit=False)
			region = request.POST.get('name')
			print "Region :", region
			if  region:
				# loc_price.region = LocalDistributorRegion.objects.get(name = region, courier__courier_name in region)
				# loc_price.save()

				messages.success(request, 'Local Distributor Price added successfully')
			else:
				messages.error(request, 'Courier Name Error.')

			return redirect(request.META['HTTP_REFERER'])
		else:
			messages.error(request, 'Please correct the error below.')

	page=request.GET.get('page',1)
	paginator=Paginator(dist_price,100)

	try:
		price=paginator.page(page)
	except PageNotAnInteger:
		price=paginator.page(1)
	except EmptyPage:
		price=paginator.page(paginator.num_pages)

	context['price'] = price
	context['loc_dist_pr'] = loc_dist_pr
	context['dist_member'] = dist_member

	return render(request, 'sokohali/LocalDistPrice.html', context)


@login_required
def get_pkg_dimens(request):

	rg = request.GET
	lb_country = rg.get('destination')
	origin = rg.get('origin')
	shipping_method = rg.get('shipping_method')

	marketer = marketing_member(request)

	costcalc = marketingmember_costcalc(request,lb_country)

	item_shipping_chain = marketer.get_shipping_chain_route(origin,lb_country)

	if shipping_method == "Air Freight":
		ship_method = "Air"
	elif shipping_method == "Sea Freight":
		ship_method = "Sea"
	else:
		ship_method = "Express"

	quantity = 1

	new_custom_sizes = str(rg.get('custom_sizes')).replace('"','').split('x')
	print "dimensions: ",rg.get('custom_sizes')
	length = float(new_custom_sizes[0])
	width  = float(new_custom_sizes[1])
	height = float(new_custom_sizes[2])
	weight = float(new_custom_sizes[3])

	weightFactor   = costcalc.dim_weight_factor
	lb_kg_factor   = costcalc.lb_kg_factor
	kg_lb_factor   = costcalc.kg_lb_factor
	exchange_rate  = costcalc.dollar_exchange_rate

	dim_weight = quantity * (length * width * height) / weightFactor #in lbs
	entered_weight = weight
	weight_unit = str(rg.get("unit"))

	box_weight_Dim = dim_weight #* in lbs
	box_weight_Dim_K = dim_weight * lb_kg_factor
	box_weight_K = weight * lb_kg_factor

	shippingWght = 0.0

	# if weight_unit == "lb":
	box_weight_Actual = entered_weight * quantity
	print "dim weight: ",dim_weight
	print "actual weight: ",box_weight_Actual
	# box_weight_Actual_K = entered_weight * lb_kg_factor * quantity

	if box_weight_Actual > box_weight_Dim:
		shippingWght = round(box_weight_Actual,2)
	else:
		shippingWght = round(box_weight_Dim,2)

	the_rate = marketer.get_route_delivery_method_range_rate(origin, lb_country, ship_method, shippingWght)

	print "the rate: ", the_rate

	est_shipping_amount = round(float(the_rate * shippingWght),2)

	return JsonResponse({'result':est_shipping_amount})


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def help(request):
	context = {}
	return render(request, 'sokohaliAdmin/help.html', {})


@login_required
def security_question(request, username=None):
	rp = request.POST
	if request.method == 'POST':
		# form = PasswordChangeForm(request.POST)
		question = request.POST.get('question')
		# print "Question :",question
		# answer1 = request.POST.get('answer')
		# print "Answer :", answer
		# answer = value_encryption(answer1)
		# print "Answers :",answer
		profile = SecurityQuestion.objects.create(
			user =request.user.useraccount,
			question = rp.get('question'),
			answer = value_encryption(rp.get('answer')),
			created = rp.get('created')
			)
		# print "Profile :",profile

		profile.save()
	else:
		print "Form not valid"
		# form = CreateQuestionForm()
	return redirect(request.META['HTTP_REFERER'])



@login_required
def get_user_account(request):
	context = {}
	# mem_form = LocalDistributionMemberForm()

	if request.method =="POST":

		obj_id = request.POST.get('obj_id')
		decision = request.POST.get('decision')

		user = request.user.useraccount.securityquestion.user
		print "User :",user
		users = request.POST.get('users')
		print "users :", users

		staff_form = get_object_or_404(SecurityQuestion, user =user).question
		print"staff_form is : ", staff_form
	else:
		# mem_form = LocalDistributionMemberForm()
		print"Error"

	context['staff_form'] = staff_form
	context['obj_id'] = obj_id
	context['decision'] = decision

	return render(request, 'sokohaliAdmin/payments_log.html',context)


@login_required
def crud_shopping_manager(request,item_id,action):
	shipping_obj = ShippingItem.objects.get(pk=item_id)
	print action
	print item_id
	if action == "purchased":
		shipping_obj.status_2 = "purchased"
		shipping_obj.status = "Recieved"
		shipping_obj.archive = False
		shipping_obj.deleted = False
		shipping_obj.save()
	elif action == "archive":
		shipping_obj.archive = True
		shipping_obj.save()
	else:
		shipping_obj.deleted = True
		shipping_obj.save()
	return redirect(request.META['HTTP_REFERER'])


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def trucking_service(request):
	
	context = {}
	truckigObjects = Trucking.objects.filter(deleted=False,archive=False)
	context['truck_obj'] = truckigObjects
	print 'see here'
	if request.method == "POST":
		print 'got here'
		print request.POST
		form = TruckingForm(request.POST, request.FILES)
		if form.is_valid():
			truckForm = form.save(commit=False)
			truckForm.created_by = request.user.username
			truckForm.save()
		else:
			print form.errors
		return redirect(request.META['HTTP_REFERER'])
	else:
		form = TruckingForm()
		context['form'] = form
	template_name = 'sokohaliAdmin/truckingservice.html'
	trucking = paginate_list(request, truckigObjects, 10)
	context['trucking'] = trucking
	return render(request, template_name, context)


@login_required
@request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def trucking_edit(request):
	
	print request.POST
	truckigObjects = Trucking.objects.get(pk=request.POST.get('item_id'))
	if request.method == "POST":
		form = TruckingForm(request.POST, request.FILES, instance=truckigObjects)
		if form.is_valid():
			truckForm = form.save(commit=False)
			truckForm.created_by = request.user.username
			truckForm.save()
		else:
			print form.errors
		return redirect(request.META['HTTP_REFERER'])
	else:
		return redirect(request.META['HTTP_REFERER'])


@login_required
def archive_delete_truck(request,item_id,action):
	truck_obj = Trucking.objects.get(pk=item_id)
	if action == 'delete':
		truck_obj.deleted = True
	else:
		truck_obj.archive = True
	truck_obj.save()
	return redirect(request.META['HTTP_REFERER'])


@login_required
def shopping_edit(request):
	print request.POST
	shippingObjects = ShippingItem.objects.get(pk=request.POST.get('item_id'))
	if request.method == "POST":
		form = ShippingItemForm(request.POST, request.FILES, instance=shippingObjects)
		if form.is_valid():
			form.save()
		else:
			print form.errors
		if request.POST.get('status') == "Recieved":
			user_id = shippingObjects.user.pk
			description = shippingObjects.description
			user = User.objects.get(useraccount__pk = user_id)
			print user.username, description
			title = "Package Creation Notification"
			text = 'email/notify_user.html'
			try:
				sokohali_sendmail(request, user, title, text, description)
			except Exception as e:
				print "message was not sent because of ", e
		else:
			pass
		return redirect(request.META['HTTP_REFERER'])
	else:
		return redirect(request.META['HTTP_REFERER'])


@login_required
def sidebarTruck(request,action):
	context = {}
	template_name = 'sokohaliAdmin/truckingservice.html'
	if action == "all":
		truck_obj = Trucking.objects.filter(deleted=False,archive=False)
	elif action == "ongoing":
		truck_obj = Trucking.objects.filter(status="Ongoing",deleted=False,archive=False)
	elif action == "new":
		truck_obj = Trucking.objects.filter(status="New",deleted=False,archive=False)
	else:
		truck_obj = Trucking.objects.filter(status="Completed",deleted=False,archive=False)
	context['truck_obj'] = truck_obj
	context['trucking'] = paginate_list(request, truck_obj, 10)
	return render(request,template_name,context)


@login_required
def sidebarNotify(request,action):
	mm = marketing_member(request)
	context = {}
	template_name = 'sokohaliAdmin/user_item_received_notification.html'
	if action == "all":
		shipping_item = ShippingItem.objects.filter(~Q(tag="Shopping"), user__useraccount__marketer=mm)
	elif action == "received":
		shipping_item = ShippingItem.objects.filter(~Q(tag="Shopping"), user__useraccount__marketer=mm, status="Received")
	context['shipping_item'] = shipping_item
	context['items_to_ship'] = paginate_list(request, shipping_item, 10)
	return render(request,template_name,context)


@login_required
def sidebarShopper(request,action):
	context = {}
	template_name = 'sokohaliAdmin/shoppingManager.html'
	if action == "all":
		shopping_obj = ShippingItem.objects.filter(deleted=False,archive=False)
	elif action == "received":
		shopping_obj = ShippingItem.objects.filter(status="Received",deleted=False,archive=False)
	context['shopping_obj'] = shopping_obj
	context['shoppingRequest'] = paginate_list(request, shopping_obj, 10)
	return render(request,template_name,context)


@login_required
def edit_process_trucking_form(request):
	context = {}
	template_name = 'sokohaliAdmin/editProcessTruckingForm.html'
	truckingObject = Trucking.objects.get(pk=request.GET.get('item_id'))
	truckForm = TruckingForm(instance=truckingObject)
	context['form'] = truckForm
	context['item_id'] = truckingObject.pk
	return render(request,template_name,context)


@login_required
def edit_process_shopping_form(request):
	context = {}
	template_name = 'sokohaliAdmin/editProcessShoppingForm.html'
	shippingObject = ShippingItem.objects.get(pk=request.GET.get('item_id'))
	print shippingObject
	shoppingForm = ShippingItemForm(instance=shippingObject)
	context['form'] = shoppingForm
	context['item_id'] = shippingObject.pk
	return render(request,template_name,context)
















