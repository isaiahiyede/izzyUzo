from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from models import MarketingMember, ShippingChain,\
					WarehouseMember, CustomClearingAgent, ShippingMember, LocalDistributionMember, LocalDistributorLocation, \
					AvailableCountry, BankAccount, ShippingRate, FixedShipment, WarehouseLocation

from django.contrib.auth.decorators import login_required
from forms import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from general.custom_passes_test import request_passes_test
from general.custom_functions import marketing_member, generate_mm_random_code
#from service_provider.forms import EditMarketingMemberForm, BankAccountForm, ConfigureRateForm
from general.staff_access import staff_check
from django.forms.formsets import formset_factory
from django.forms import modelformset_factory
from django.contrib import messages
from django.apps import apps
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
#from operator import itemgetter
import collections
from django.forms.models import model_to_dict
from sokohaliAdmin.models import CostCalcSettings

# from service_provider.forms import CreateQuestionForm


def request_subscriber(request):
	return request.user.subscriber


def subscriber_marketer(request):
	try:
		return request_subscriber(request).marketingmember
	except:
		return None


def deactivate_rented_service(subscriber, service, identifier_name):
	service_model = apps.get_model('service_provider', service.__class__.__name__)
	print service_model, service, subscriber, identifier_name
	try:
		offered_service = service_model.objects.get(offered_by = subscriber)#, offered_for_rent = True)#, country=service.country)
		print "offered_service", offered_service
		offered_service.offered_for_rent = False
		offered_service.save()

		print 'offered_service: ',offered_service
		'''Remove this service from customers who have rented it'''
		filter_dict = {}
		filter_dict[identifier_name] = service
		update_dict = {}
		update_dict[identifier_name] = None
		ShippingChain.objects.filter(**filter_dict).update(**update_dict)
		'''Deactivate service'''
	except Exception as e:
		print 'Offered service not found: ',e
		pass


def offered_services_form(subscriber):
	try:
		my_offered_warehouse = WarehouseMember.objects.get(offered_by = subscriber)
		#my_offered_warehouse = direction_services.mm_offered_warehouse(mm)
		#print "my_offered_warehouse", my_offered_warehouse
		offer_warehouse_form = OfferWarehouseForm(instance = my_offered_warehouse)
	except Exception as e:
		print "e:", e
		offer_warehouse_form = OfferWarehouseForm()
		#print "offer_warehouse_form", offer_warehouse_form
	try:
		my_shipping_member = ShippingMember.objects.get(offered_by = subscriber)
		#my_shipping_member = direction_services.mm_offered_shipping_member(mm)
		offer_shipping_service = OfferShippingServiceForm(instance = my_shipping_member)
	except:
		offer_shipping_service = OfferShippingServiceForm()

	try:
		my_clearing_agent = CustomClearingAgent.objects.get(offered_by = subscriber)
		#print 'my_clearing_agent: ',my_clearing_agent
		#my_clearing_agent = direction_services.mm_offered_clearing_agent(mm)
		offer_customs_clearing_form = OfferCustomClearingForm(instance = my_clearing_agent)
	except Exception as e:
		#print 'e: ',e
		offer_customs_clearing_form = OfferCustomClearingForm()

	return offer_warehouse_form, offer_shipping_service, offer_customs_clearing_form

def offer_service(request, subscriber, shipping_chain):
	  rp                = request.POST
	  print "rp", rp
	  # model_name_dict   = {'warehouse': WarehouseMember, 'shipper': ShippingMember, 'clearing_agent': CustomClearingAgent}
	  model_name_dict   = {'warehouse': WarehouseMember, 'shipper': ShippingMember, 'clearing_agent': CustomClearingAgent}
	  model_form_dict   = {'warehouse': OfferWarehouseForm, 'shipper': OfferShippingServiceForm, 'clearing_agent': OfferCustomClearingForm}
	  service_direction = {'warehouse': 'origin_warehouse', 'shipper': 'origin_shipper', 'clearing_agent': 'destination_clearing_agent'}
	  service_name      = rp.get('service_name')
	  print "model_name_dict", model_name_dict
	  service_model     = model_name_dict[service_name]
	  service_form      = model_form_dict[service_name]

	  try:
		  service = service_model.objects.get(offered_by = subscriber)
		  form = service_form(rp, instance = service)
		  #print "form :", form
	  except service_model.DoesNotExist:
		  form = service_form(rp)
		  #print "form", form
	  if form.is_valid():
		  service_direction_field = service_direction.get(service_name)
		  print "service_direction_field", service_direction_field
		  service = form.save(commit = False)
		  service.offered_by = subscriber
		  service.save()

		  # if shipping_chain:
		  #     setattr(shipping_chain, service_direction_field, service)
		  #     shipping_chain.save()
		  # 
		  if not rp.has_key('offered_for_rent'):
			 deactivate_rented_service(subscriber, service, service_direction_field)
	  print form.errors

# def check_active_service(service_dict, service_name, direction):
#     if direction in ["import", "export"]:
#         service_name_obj = service_dict[0].get(service_name)
#         if service_name_obj != None:
#             return service_name_obj.offered_for_rent
#         return False
#     else:
#         service_name_count = 0
#         for service in service_dict:
#             service_name_obj = service.get(service_name)
#             if service_name_obj != None and service_name_obj.offered_for_rent:
#                 service_name_count+=1
#         if service_name_count == 2:
#             return True
#         return False

def services_active(shipping_chain, origin_field, destination_field):
	active_count = 0
	if getattr(shipping_chain, origin_field):
		active_count += 1
	if getattr(shipping_chain, destination_field):
		active_count += 1

	return active_count == 2


def sh_services_active(shipping_chain, client_type):
	active_count = 0
	if getattr(shipping_chain, client_type):
		active_count += 1

	return active_count == 1


@login_required
def country_settings(request):
	available_countries = AvailableCountry.objects.prefetch_related('localdistributionmember_set__localdistributorregion_set__localdistributorlocation_set', 'localdistributionmember_set__localdistributorregion_set__localdistributorprice_set').all()
	#mm = MarketingMember.objects.get(pk = 1)
	#print mm.get_route_delivery_method_range_rate('shipping', 'import_export', 'United States', 'Nigeria', 'air', 3.4)
	return render(request, 'setup/country_settings.html', {'available_countries': available_countries})


def get_serv_prov_info(class_name, id):
	if class_name == "WarehouseMember":
		field_names = [#'name', 'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number',
			'company_name', 'warehouse_size', 'process_charge_per_kg', 'storage_charge_per_day', 'working_hrs_start', 
			 'working_hrs_end', 'offered_for_rent', 'auto_subscriber_approval', 'publish_reviews', 'about_service']
	else:
		field_names = ['name', 'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number',
			  'storage_charge_per_day', 'working_hrs_start', 'working_hrs_end', 'offered_for_rent', 'auto_subscriber_approval', 'publish_reviews', 'about_service']
	
	
	
	service_model = apps.get_model('service_provider', class_name)
	print "Service Model", service_model
	row = service_model.objects.filter(pk = id).values(*field_names)[0]
	#WHM = WarehouseMember.objects.filter(pk = id)
	#print "row",
	ordered_dict = collections.OrderedDict()
	for field in field_names:
		ordered_dict[field] = row[field]

	return ordered_dict


def get_member_info(request):
	member_type = request.GET.get('member_type')
	id          = request.GET.get('id')
	print member_type
	member_info = get_serv_prov_info(member_type, id)
	if member_type == "WarehouseMember":
		locations = WarehouseLocation.objects.filter(owned_by__pk=id)
	elif member_type == "ShippingMember":
		locations = ShippingMemberRoute.objects.filter(shipper__pk=id)
	elif member_type == "CustomClearingAgent":
		locations = ClearingPrice.objects.filter(clearing_agent__pk=id)
	else:
		locations = None

	return render(request, 'setup_snippet/member_info.html',
					{'member_info': member_info.iteritems(), 'member_type': member_type, 'locations':locations})


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def view_delivery_routes_rates(request):
	# mme = get_services_rented(request)
	try:
		mm = request.user.useraccount.marketer
		subscriber = mm.subscriber
	except:
		mm          = subscriber_marketer(request)
		subscriber  = request_subscriber(request)
	#marketingmember = marketing_member(request)
	#shipping_rates = marketingmember.get_all_shipping_rates()
	#print "mm: ", marketingmember
	shipping_chains = subscriber.marketingmember.get_shipping_chains()
	print "sC: ", shipping_chains
	form = ShippingRateForm(marketer = subscriber.marketingmember)

	if request.GET.has_key('delete'):
		obj_id = request.GET['delete']
		ShippingRate.objects.get(pk = obj_id).delete()

		messages.success(request, 'Rate successfully deleted')
		return redirect(request.META.get('HTTP_REFERER', '/'))

	if request.GET.has_key('service_chain_id'):
		service_chain = ShippingChain.objects.get(pk = request.GET['service_chain_id'])
		return JsonResponse({'route_direction': service_chain.direction})


	if request.method == "POST":
		print request.POST
		if request.POST.has_key('edit_route'):
			instance = ShippingRate.objects.get(pk = request.POST['edit_route'])
			instance.rate_D = request.POST.get('rate_D', 0)
			instance.save()
			#form = ShippingRateForm(request.POST, instance=instance, marketer = marketingmember)
			#action = 'edited'
			messages.success(request, 'Rate successfully edited')
			return redirect(request.META.get('HTTP_REFERER', '/'))
		else:
			marketingmember = MarketingMember.objects.get(subscriber = subscriber)
			form = ShippingRateForm(request.POST, marketer = marketingmember)
			#action = 'added'

			if form.is_valid():
				form.save()

				messages.success(request, 'Rate successfully added')
				return redirect(request.META.get('HTTP_REFERER', '/'))

		print 'form.errors: ',form.errors


	return render(request, 'setup/view_delivery_routes_rates.html', {'shipping_chains': shipping_chains,
																	'form': form})


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def configure_setup(request):
	#print 'rp: ',request.POST
	#marketingmember = marketing_member(request)

	# Create the formset, specifying the form and formset we want to use.
	#BankAccountFormSet = formset_factory(BankAccountForm, formset=BaseBankAccountFormSet)
	BankAccountFormSet = modelformset_factory(BankAccount, form = BankAccountForm,
													can_delete=True)
	# BankAccountFormSet = modelformset_factory(BankAccount, fields = ('bank', 'account_name', 'account_no', 'currency'),
	#                                             can_delete=True)


	if request.GET.has_key('remove_obj'):
		BankAccount.objects.get(pk = request.GET['obj_id'])
		return JsonResponse({'response': 'success'})

	#marketingmember = get_object_or_404(MarketingMember, pk = 1)

	setup_form                  = StartSetupForm()
	marketingmemberinfo_form    = MarketingMemberInfo()

	marketingmember             = subscriber_marketer(request)

	if marketingmember == None:
		marketingmember = request.user.useraccount.marketer
	else:
		pass
	# print "mm1: ",marketingmember

	if marketingmember is not None:
		setup_form              = StartSetupForm(instance = marketingmember)
		marketingmemberinfo_form    = EditMarketingMemberInfo(instance = marketingmember)
	#print form
	#print request.POST
	if request.method == "POST":

		rp = request.POST
		rf = request.FILES

		setup_form = StartSetupForm(rp)

		marketingmemberinfo_form    = MarketingMemberInfo(rp, rf)

		print 'marketingmember: ',marketingmember
		if marketingmember is not None:
			#print 'marketingmember is not None'
			setup_form                  = StartSetupForm(rp, instance = marketingmember)
			marketingmemberinfo_form    = EditMarketingMemberInfo(rp, rf, instance = marketingmember)


		bankaccount_formset             = BankAccountFormSet(request.POST)

		#if setup_form.is_valid() and bankaccount_formset.is_valid():
		if setup_form.is_valid():
			#print 'setup_form.is_valid: ',setup_form.is_valid()


			if marketingmemberinfo_form.is_valid():
				#print 'marketingmemberinfo_form.is_valid: ',marketingmemberinfo_form.is_valid()


				mm_other = marketingmemberinfo_form.save(commit = False)

				if mm_other.random_code == None:
					mm_other.random_code = generate_mm_random_code()

				active = False
				if rp.has_key('storefront'):
					active = True

				try:
					marketingmember.active = active
				except:
					pass

				mm_other.subscriber = request_subscriber(request)

				'''
					setup_form not saved because it creates a duplicate MarketingMember object.
					setup_form and marketingmemberinfo_form both have the same model.
					#setup_form.save()
					Below is custom save.
				'''
				fields = ['bank_depost', 'card_payment', 'stripe', 'paypal']
				for field in fields:
					if field in rp.keys():
						setattr(mm_other, field, rp.get(field))

				mm_other.save()
				print mm_other.subscriber.marketingmember


			if bankaccount_formset.is_valid():
				formset_instance = bankaccount_formset.save(commit = False)
				for obj in formset_instance:
					obj.marketing_member = mm_other.subscriber.marketingmember
					obj.save()

				for obj in bankaccount_formset.deleted_objects:
					obj.delete()


	# Get our existing link data for this user.  This is used as initial data.
	bank_accounts = BankAccount.objects.filter(marketing_member = marketingmember)#.values('bank', 'account_name', 'account_no')
	#print 'bank_accounts: ',bank_accounts
	bankaccount_formset = BankAccountFormSet(queryset = bank_accounts)
	context_dict = {'form': setup_form, 'bank_accounts': bank_accounts,
					'marketingmemberinfo_form': marketingmemberinfo_form, 'bankaccount_formset': bankaccount_formset}
	# if marketingmember:
	#     context_dict.update({'marketingmember_name': marketingmember.name})
	return render(request, 'setup/configure_setup.html', context_dict)


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def select_service(request):
	return render(request, 'setup/select_service.html')



def offer_services(request):
	try:
		subscriber = request_subscriber(request)
		mm          = subscriber_marketer(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
		mm         = subscriber.marketer

	country = subscriber.country
	print "country here:",country
	if request.POST:
		offer_service(request, subscriber, None)
		offer_warehouse_form, offer_shipping_service_form, offer_customs_clearing_form = offered_services_form(subscriber)#, country, country)
		service_name = request.POST.get('service_name')
		chain_id = "offer"
		return redirect('service_provider:service_location', service_name, chain_id)
		
	else:
		 offer_warehouse_form, offer_shipping_service_form, offer_customs_clearing_form = offered_services_form(subscriber)#, country, country)

	return render(request, 'setup/chain_setup_page_2.html',
				{'subscriber': subscriber, 'country': country,
				'offer_warehouse_form': offer_warehouse_form,
				'offer_shipping_service_form': offer_shipping_service_form, 'offer_customs_clearing_form': offer_customs_clearing_form})


@login_required
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def setup(request):

	try:
		mm = request.user.useraccount.marketer
		subscriber = mm.subscriber
	except:
		mm          = subscriber_marketer(request)
		subscriber  = request_subscriber(request)

	rG = request.GET
	print "rg: ",rG
	print "mm",mm
	print 'subscriber',subscriber
	#print mm.get_service_chain_route_warehouse('shipping', 'import_export', 'USA', 'Nigeria', 'export')

	service_type = 'shipping'
	if request.method == "GET":
		context = {'service_type': service_type}

		page = rG.get('page')

		if page != None:
			page_int = int(page)

			if (1 <= page_int <= 5):


				if page_int == 1:
					'''check if subscriber has a storefront or not'''
					print "here"
					if not mm:
						print "here again"
						return redirect(reverse('service_provider:offer_services'))

					service_chains = mm.get_shipping_chains()
					print "service_chains: ",service_chains
					context.update({'service_chains': service_chains})
				else:
					origin          = rG.get('origin', '')
					destination     = rG.get('destination', '')
					direction       = rG.get('direction', '')
					chain           = rG.get('chain')
					#print rG
					print "chain:", chain
					try:
						service_chain = ShippingChain.objects.get(pk = chain, subscriber=subscriber)
						print "sc: ",service_chain.shipper
						context.update({'service_chain': service_chain})
					except Exception as e:
						print 'page 1 e: ',e
						raise Http404

					if page_int > 1:
						context.update({'chain_id': chain, 'origin': origin, 'destination': destination}), #'direction': service_chain.direction,

					#print rG

					if page_int == 2:
						offer_warehouse_form, offer_shipping_service_form, offer_customs_clearing_form = offered_services_form(subscriber)

						issues_to_fix = 3
						form_list = [offer_warehouse_form, offer_shipping_service_form, offer_customs_clearing_form]
						for form in form_list:
							if form.instance.id and form.instance.offered_for_rent:
								issues_to_fix -= 1
						
						#location_form = OfferWarehouseLocationForm()
						#locations = WarehouseMember.objects.get(offered_by = subscriber).get_all_warehouses()
						context.update({'offer_warehouse_form': offer_warehouse_form, 'offer_customs_clearing_form': offer_customs_clearing_form, 
										'offer_shipping_service_form': offer_shipping_service_form,  'issues_to_fix': issues_to_fix})

					if page_int == 3:
						#marketingmember_form = MarketingMemberForm(instance = mm)
						#paymentservices_form = PaymentServicesForm(instance = mm)
						rent_service_form       = RentServiceForm(instance = service_chain, origin=service_chain.origin, destination=service_chain.destination, subscriber=service_chain.subscriber)
						#print "form:", rent_service_form.changed_data
						warehouses_active       = services_active(service_chain, 'origin_warehouse', 'destination_warehouse')
						shippers_active         = sh_services_active(service_chain, 'shipper')#'origin_shipper', 'destination_shipper')
						customsagents_active    = sh_services_active(service_chain, 'clearing_agent')#'origin_clearing_agent', 'origin_clearing_agent')
						#print "customsactive", customsagents_active
						#print warehouses_active, rent_service_form
						#print 'active_warehouses_status: ',active_warehouses_status
						context.update({'rent_service_form': rent_service_form,
										'warehouses_active': warehouses_active, 'shippers_active': shippers_active,
										'customsagents_active': customsagents_active,
										'active_origin_distributor': service_chain.origin_distributor,
										'active_dest_distributor': service_chain.destination_distributor})


					if page_int == 4:
						context.update({'form': ShippingRateForm(marketer = mm, instance = service_chain)})

					if page_int == 5:
						cost_settings = CostCalcSettings.objects.filter(marketer=mm)
						context.update({'costform': CostCalcSettingsForm(), 'costcalc': cost_settings})
						
				context.update({'page': page_int})

				template_name = 'setup/chain_setup_page_%s.html' %page
				return render(request, template_name, context)
		raise Http404

	if request.method == "POST":
		rp = request.POST
		#print 'rP: ',rp
		action = rp.get("action")
		print "action: ", action
		form_id = rp.get('form_id')
		print form_id

		origin          = rG.get('origin', '')
		destination     = rG.get('destination', '')
		direction       = rG.get('direction', '')
		chain           = rG.get('chain', '')

		try:
			shipping_chain = ShippingChain.objects.get(pk = chain,  subscriber = subscriber)#, origin = origin, destination = destination)#, direction = direction)
		except:
			pass
		#print 'rp: ',rp
		# shipping_chain = ShippingChain.objects.get(pk = chain,  subscriber = subscriber)#, origin = origin, destination = destination)#, direction = direction)
		action = rp.get("action")
		# print 'rp: ',rp

		if action == "add_route":
			origin      = rp["origin"]
			destination = rp["destination"]
			#service, created = Service.objects.get_or_create(service_type = service_type, marketing_member = mm)
			subscriber = subscriber#.service
			shipping_chain, created = ShippingChain.objects.get_or_create(subscriber = subscriber, origin = origin, destination = destination,
																		defaults={'air': rp.get('air', False), 'sea': rp.get("sea", False), #'ground': rp.get('ground', False),
																		'air_delivery_time': rp.get('air_delivery_time', '2 - Days'),#, rp.get('air_duration', '')),
																		'sea_delivery_time': rp.get('sea_delivery_time', '2 - Weeks'), #rp.get('sea_duration', '')),
																		})

			if not created:
				messages.warning(request, "%s to %s Delivery Route already exist. Please add another route." %(origin, destination))
			else:
				messages.success(request, '%s - %s successfully added' %(origin, destination))
			return redirect(request.META.get('HTTP_REFERER'), '/')


		elif action == "edit_route":
			shipping_chain, created = ShippingChain.objects.update_or_create(id = rp['route_id'],
																		defaults={'origin': rp["origin"], 'destination': rp["destination"], 'air': rp.get('air', False), 'sea': rp.get("sea", False), #'ground': rp.get('ground', False),
																		'air_delivery_time': rp.get('air_delivery_time', '2 - Days'),#, rp.get('air_duration', '')),
																		'sea_delivery_time': rp.get('sea_delivery_time', '2 - Weeks'), #rp.get('sea_duration', '')),
																		#'ground_delivery_time': "%s - %s" %(rp.get('ground_delivery_time', '2'), rp.get('ground_duration', '')),
																		})

			messages.success(request, '%s - %s successfully edited' %(rp["origin"], rp["destination"]))
			return redirect(request.META.get('HTTP_REFERER'), '/')

			#return render(request, 'setup_snippet/delivery_route.html', {'origin': service_chain.origin, 'destination': service_chain.destination,
			#                                                        'direction': service_chain.direction, "id": service_chain.id, 'edit': 'edit'})
		elif action == "offer":
			origin          = rG.get('origin', '')
			destination     = rG.get('destination', '')
			direction       = rG.get('direction', '')
			chain           = rG.get('chain')

			print "origin countrrrry: ", origin
			country = origin
			form_id = rp.get('form_id')
			print form_id
			if form_id == 'offer_clearing_service':
				country = destination
			#print form_id
			offer_service(request, subscriber, shipping_chain)
			service_name = rp.get('service_name')
			shipping_chain = ShippingChain.objects.get(pk = chain,  subscriber = subscriber)#, origin = origin, destination = destination)#, direction = direction)
			
			# model_name_dict   = {'warehouse': WarehouseMember, 'shipper': ShippingMember, 'clearing_agent': CustomClearingAgent}
			# model_form_dict   = {'warehouse':  OfferWarehouseLocationForm, 'shipper': ShippingRouteForm, 'clearing_agent': ClearingLocationForm}
			# service_name      = rp.get('service_name')
			# print "model_name_dict", model_name_dict
			# service_model     = model_name_dict[service_name]
			# service_form      = model_form_dict[service_name]
			# print service_form
			# if service_name == "warehouse":
			#     #location_form = OfferWarehouseLocationForm()
			#     service = service_model.objects.get(offered_by = subscriber).get_all_warehouses()
			# else:
			#     service = service_model.objects.get(offered_by = subscriber).get_all_locations()
			# context = {'form':service_form, 'service': service, 'service_name': service_name}
				#request.session['setup'] = "from-setup"
			return redirect('service_provider:service_location', service_name,chain)


		elif action == "rent":
			form_id = rp.get('form_id')

			if form_id == "rent_facility_form":
				#print 'form_id: ',form_id, rp

				model_name_dict = {'warehouse': WarehouseMember, 'shipper': ShippingMember, 'clearing_agent': CustomClearingAgent, 'distributor': LocalDistributionMember}

				new_rp_dict = dict((k,v) for k,v in rp.iteritems() if v)

				for key in ['form_id', 'action', 'csrfmiddlewaretoken']:
					new_rp_dict.pop(key)

				model_identifiers = new_rp_dict

				print 'model_identifiers: ', model_identifiers

				'''select option and val in post'''
				for identifier_name, identifier_id in model_identifiers.iteritems():

					'''get say identifier(warehouse) from identifier_name(origin_warehouse)'''
					if identifier_name == "clearing_agent":
						identifier = identifier_name
					elif identifier_name == "shipper":
						identifier = identifier_name
					else:
						identifier   = identifier_name.split('_')[1]
					print identifier, identifier_id

					# if not identifier_name in ['origin_distributor', 'destination_distributor']:
					#     #service_model = apps.get_model('service_provider', model_name_dict[identifier])
					#     service_model = model_name_dict[identifier]
					#     service = service_model.objects.get(pk = identifier_id)
					#     #print service.offered_by
					#     #print service.offered_by == mm
					#     '''Check if selected service is not offered by user and deactivate offered service by user, if any.'''
					#     if not service.offered_by == mm:
					#         '''deactivate shipping chains using this service, if any'''
					#         #deactivate_rented_service(mm, service, identifier_name)
					#         deactivate_rented_service(subscriber, service, identifier_name)

					#service_model = apps.get_model('service_provider', model_name_dict[identifier])
					service_model = model_name_dict[identifier]
					service = service_model.objects.get(pk = identifier_id)
					print "service", service
					setattr(shipping_chain, identifier_name, service)
					shipping_chain.save()

				return redirect(request.META.get('HTTP_REFERER'))

	raise Http404



@login_required
def editTermsConditions(request):
	try:
		mm = marketing_member(request)
	except:
		mm = request.user.useraccount.marketer
	print "i reach o"
	form = EditMarketingMemberForm(instance=mm)
	if request.user.is_authenticated():
		if request.method == "POST":
			print request.POST
			#form = EditMarketingMemberForm()
			form = EditMarketingMemberForm(request.POST, instance=mm)
			if form.is_valid():
				form.save()
				print "i reach 2 o"
				return redirect(reverse('general:legal'))
			else:
				print form.errors
	else:
		form = EditMarketingMemberForm(instance=mm)
	return render (request, 'sokohaliAdmin/legalform.html', {'form': form})


def edit_emailtemplate(request):
	try:
		mm = marketing_member(request)
	except:
		mm = request.user.useraccount.marketer
	if request.user.is_authenticated():
		if request.method == "POST":
			form = EmailTextForm(request.POST, instance = mm)
			if form.is_valid():
				form.save()
				return redirect(reverse('service_provider:emailtemplate_setup'))
			else:
				print form.errors
		else:
			form = EmailTextForm(instance=mm)
		return render (request, 'sokohaliAdmin/emailform.html', {'form':form})

def emailtemplate(request):
	try:
		mm = marketing_member(request)
	except:
		mm = request.user.useraccount.marketer
	emailtext = mm.email_text
	return render(request, 'general_client/emaildemo.html', {'emailtext': emailtext})


def editFAQ(request):
	try:
		mm = marketing_member(request)
	except:
		mm = request.user.useraccount.marketer
	if request.user.is_authenticated():
		if request.method == "POST":
			form = FAQForm(request.POST, instance = mm)
			if form.is_valid():
				form.save()
				return redirect(reverse('general:faq'))
			else:
				print form.errors
		else:
			form = FAQForm(instance=mm)
		return render (request, 'sokohaliAdmin/faqform.html', {'form':form})
 
   

	

@login_required
@csrf_exempt
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def add_fixed_weight_shipment(request):
	template_name = 'setup/fixedWeight.html'
	context = {}
	print "fixed weight"
	
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	fixed_wgt_items = FixedShipment.objects.filter(subscriber=subscriber)
	context['fixed_wgt_items'] = fixed_wgt_items
	context['routes'] = routes
	return render(request,template_name,context)



@login_required
@csrf_exempt
# @request_passes_test(staff_check, login_url='/access-denied/', redirect_field_name=None)
def fixed_weight_shipment_items(request):
	template_name = 'setup_snippet/fixedwgtshipping.html'
	context = {}
	
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	routes = ShippingChain.objects.filter(Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber))
	fixed_wgt_items = FixedShipment.objects.filter(subscriber=subscriber)
	context['fixed_wgt_items'] = fixed_wgt_items
	context['routes'] = routes
	rp = request.POST
	print rp
	if request.method == "POST":
		if rp.has_key('create'):
			shipping_chain = ShippingChain.objects.get(id=rp.get('chain'))
			create_fixed_shipping = FixedShipment.objects.create(subscriber=subscriber,description=rp.get('fxd_wgt_desc'),unit_price_D=rp.get('fxd_wgt_unit_price_D'),chain=shipping_chain)
			create_fixed_shipping.save()
			fixed_wgt_items = FixedShipment.objects.filter(subscriber=subscriber)
			context['fixed_wgt_items'] = fixed_wgt_items

		elif rp.has_key('edit'):
			get_fixed_wgt_itm = FixedShipment.objects.get(subscriber=subscriber,id=rp.get('item_id'))
			get_fixed_wgt_itm.description = rp.get('edit_fxd_wgt_desc')
			get_fixed_wgt_itm.unit_price_D = rp.get('edit_fxd_wgt_unit_price_D')
			get_fixed_wgt_itm.save()
			fixed_wgt_items = FixedShipment.objects.filter(subscriber=subscriber)
			messages.success(request,"Rate was successfully edited")
			return redirect(request.META.get('HTTP_REFERER'))

		else:
			get_fixed_wgt_itm = FixedShipment.objects.get(subscriber=subscriber,id=rp.get('fxd_wgt_shipment_id')).delete()
			fixed_wgt_items = FixedShipment.objects.filter(subscriber=subscriber)
			context['fixed_wgt_items'] = fixed_wgt_items
		return render(request,template_name,context)
	return render(request,template_name,context)



def add_warehouse_address(request, service_name,chain_id):
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	
	model_name_dict   = {'warehouse': WarehouseMember, 'shipper': ShippingMember, 'clearing_agent': CustomClearingAgent}
	model_form_dict   = {'warehouse':  OfferWarehouseLocationForm, 'shipper': ShippingRouteForm, 'clearing_agent': ClearingLocationForm}
	service_name      = service_name
	print "model_name_dict", model_name_dict
	service_model     = model_name_dict[service_name]
	service_form      = model_form_dict[service_name]
	print service_form
	service = service_model.objects.get(offered_by = subscriber)
	
	context = {'form':service_form, 'service': service, 'service_name': service_name, 'chain_id': chain_id}
	# the if condition is to determine where the call is coming from. either from setup page or just the menu barand to know where to redirect to
	print "chain:",chain_id
	if chain_id != "offer":
		shipping_chain = ShippingChain.objects.get(pk=chain_id, subscriber=subscriber)
		chain = shipping_chain.pk
		origin = shipping_chain.origin
		destination = shipping_chain.destination
		context.update({'chain_id': chain, 'origin': origin, 'destination': destination}),
	
	if request.method == "GET" and 'obj_id' in request.GET:
		model_name_dict   = {'warehouse': WarehouseLocation, 'shipper': ShippingMemberRoute, 'clearing_agent': ClearingPrice}
		service_model     = model_name_dict[service_name]
		obj_id = request.GET.get('obj_id')
		edit = service_model.objects.get(pk=obj_id)
		form = service_form(instance=edit)
		context.update({'form': form, 'edit':edit})

	if request.user.is_authenticated():
		if request.method == "POST" and 'edit_id' in request.POST:
			print "this is editing"
			model_name_dict   = {'warehouse': WarehouseLocation, 'shipper': ShippingMemberRoute, 'clearing_agent': ClearingPrice}
			service_model     = model_name_dict[service_name]
			obj_id = request.POST.get('edit_id')
			edit_id = service_model.objects.get(pk=obj_id)
			form = service_form(request.POST, instance=edit_id)
			if form.is_valid():
				locationform = form.save(commit=False)
				locationform.save()
				return redirect(request.META.get('HTTP_REFERER'))
			else:
				print form.errors
		if request.method == "POST":
			form = service_form(request.POST)
			if form.is_valid():
				locationform = form.save(commit=False)
				if service_name == "warehouse":
					locationform.owned_by = service
					locationform.name = service.company_name
				elif service_name == "shipper":
					locationform.shipper = service
				else:
					locationform.clearing_agent = service
				locationform.save()
				return redirect(request.META.get('HTTP_REFERER'))

			else:
				print form.errors
	else:
		return render(request, 'setup/add_warehouse_location.html', context)
			
	return render(request, 'setup/add_warehouse_location.html', context)


def cost_settings(request):
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	mm = subscriber.marketingmember
	print "mm cost", mm
	if request.user.is_authenticated():
		if request.method == "POST":
			countries = ShippingChain.objects.filter(subscriber=subscriber)
			county = []
			for i in countries:
				county.append(i.origin)
				county.append(i.destination)
			country = list(set(county))
			print "country", country
			form_country = request.POST.get('country')
			if form_country in country:
				costset = CostCalcSettings.objects.filter(marketer=mm, country=form_country)
				if costset:
					messages.warning(request,"You already have a Cost Setting for this Country")
					return redirect(request.META.get('HTTP_REFERER'))
				elif form_country == "United States":
					messages.warning(request,"You cannot add a cost setting for the United States")
					return redirect(request.META.get('HTTP_REFERER'))
				else:
					form = CostCalcSettingsForm(request.POST)
					if form.is_valid():
						costform = form.save(commit = False)
						#print "mm here:", type(mm)
						costform.marketer = MarketingMember.objects.get(subscriber=subscriber)
						costform.save()
						#form.marketer = mm 
						return redirect(request.META.get('HTTP_REFERER'))
					else:
						print form.errors
						return redirect(request.META.get('HTTP_REFERER'))
			else:
				messages.warning(request, "You cannot add a cost setting for a country not on your Chain.")
				return redirect(request.META.get('HTTP_REFERER'))
		else:
			costform = CostCalcSettingsForm()
			costcalc = CostCalcSettings.objects.filter(marketer=mm)
			return render (request, 'setup/chain_setup_page_5.html', {'costform':costform, 'costcalc': costcalc})
			
			
			
def edit_cost_settings(request):
	#print" i reach"
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	mm = subscriber.marketingmember
	#print "mm edit", mm
	if request.user.is_authenticated():
		if request.method == "POST":
			#print request.POST
			obj_id = request.POST.get('obj_id')
			edit = CostCalcSettings.objects.get(pk=obj_id)
			form = CostCalcSettingsForm(request.POST, instance=edit)
			if form.is_valid():
				form.save(commit = False)
				form.marketer = mm
				form.save()
				return redirect('service_provider:cost_settings')
			else:
				print form.errors
		else:
			obj_id = request.GET.get('obj_id')
			edit = CostCalcSettings.objects.get(pk=obj_id)
			costform = CostCalcSettingsForm(instance = edit)
			#print "i got here joor"
			return render(request, 'setup_snippet/edit-cost-modal.html', {'form':costform, 'edit':edit})
	else:
		return redirect(request.META.get('HTTP_REFERER'))
	
	
def get_services_offered(request):
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	services = {}
	warehouse = WarehouseMember.objects.filter(offered_by = subscriber)
	if warehouse:
		services["warehouse"] = warehouse
	shipper = ShippingMember.objects.filter(offered_by = subscriber)
	if shipper:
		services["shipper"] = shipper
	clearing = CustomClearingAgent.objects.filter(offered_by=subscriber)
	if clearing:
		services["clearing"] = clearing
	print services
	return services

def get_services_rented(request):
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
	#services = get_services_offered(request)
	chain = ShippingChain.objects.filter(subscriber=subscriber)
	rented_services = {}
	origin_warehouse = chain.filter(~Q(origin_warehouse__offered_by = subscriber))
	print "ow", origin_warehouse
	if origin_warehouse:
		warehouse = []
		for whm in origin_warehouse:
			warehouse.append(whm.origin_warehouse.offered_by)       
		rented_services["origin_warehouse"] = warehouse
	destination_warehouse = chain.filter(~Q(destination_warehouse__offered_by = subscriber))
	if destination_warehouse:
		warehouse = []
		for whm in destination_warehouse:
			warehouse.append(whm.destination_warehouse.offered_by) 
		rented_services["destination_warehouse"] = warehouse
	shipper = chain.filter(~Q(shipper__offered_by = subscriber))
	if shipper:
		shipping = []
		for whm in shipper:
			shipping.append(whm.shipper.offered_by) 
		rented_services["shipper"] = shipping
	clearing_agent = chain.filter(~Q(clearing_agent__offered_by = subscriber))
	if clearing_agent:
		clearing = []
		for whm in clearing_agent:
			clearing.append(whm.clearing_agent.offered_by) 
		rented_services["clearing_agent"] = clearing
	# for x in chain:
	#     if x.origin_warehouse != subscriber or x.destination_warehouse != subscriber or x.shipper != subscriber or x.clearing_agent != subscriber:
	#         print "i", x
	#     print "x again", x
	print "rented_services", rented_services
	return rented_services
	
	
# def get_chain_rented_services(request):
#     chain_id = request.GET.get('chain_id')
#     subscriber = request_subscriber(request)
#     chain = ShippingChain.objects.get(pk=chain_id)
#     service_name ={}
#     if chain.origin_warehouse.offered_by != subscriber:
#         service_name['origin warehouse'] = chain.origin_warehouse.offered_by
#     if chain.destination_warehouse.offered_by != subscriber:
#         service_name['destination warehouse'] = chain.destination_warehouse.offered_by
#     if chain.shipper.offered_by != subscriber:
#         service_name['shipper'] = chain.shipper.offered_by
#     if chain.clearing_agent.offered_by != subscriber:
#         service_name['clearing_agent'] = chain.clearing_agent.offered_by
	
	
def dashboard_details(request, chain_id):
	try:
		subscriber = request_subscriber(request)
	except:
		subscriber = request.user.useraccount.marketer.subscriber
		
	chain = ShippingChain.objects.get(pk = chain_id)
	own_service = {}
	services = []
	offered_services = []
	rented_services = {}
	fields_list = [chain.origin_warehouse, chain.destination_warehouse, chain.shipper, chain.clearing_agent]
	for field in fields_list:
		if field.offered_by != subscriber:
			services.append(field)
	print services
	if chain.origin_warehouse in services:
		origin_warehouse = chain.origin_warehouse
		rented_services['Origin-warehouse'] = origin_warehouse
	else:
		origin_warehouse = chain.origin_warehouse
		own_service['Origin-warehouse']= origin_warehouse
	
	if chain.destination_warehouse in services:
		destination_warehouse = chain.destination_warehouse
		rented_services['Destination-warehouse'] = destination_warehouse
	else:
		destination_warehouse = chain.destination_warehouse
		own_service['Destination-warehouse'] = destination_warehouse
		
	if chain.shipper in services:
		loc = chain.shipper.get_all_locations().get(origin=chain.origin, destination = chain.destination)
		rented_services['Shipper'] = loc
	else:
		loc = chain.shipper.get_all_locations().get(origin=chain.origin, destination = chain.destination)
		own_service['Shipper'] = loc
		
	if chain.clearing_agent in services:
		loc = chain.clearing_agent.get_all_locations().get(country=chain.destination)
		rented_services['Clearing'] = loc
	else:
		loc = chain.clearing_agent.get_all_locations().get(country=chain.destination)
		own_service['Clearing'] = loc
		
	
		
	# for k,v in rented_services.items():
	#     print k
	#     if k == "Clearing":
	#         print v.clearing_agent
	#     elif k == "Shipper":
	#         print v.shipper
	#     else:
	#         print v.offered_by
	# offered_services = ShippingChain.objects.filter(subscriber=subscriber)
	pkgs_weight = chain.get_pkgs_weight()
	
	# rented_services = OfferedServiceRate.objects.filter(chain=chain, rented_by=subscriber)
	# offered_services = OfferedServiceRate.objects.filter(offered_by = subscriber)
	# pkgs_weight = chain.get_pkgs_weight()
	# print "pkgs_weight", pkgs_weight
	# print "offer service", offered_services
	return render(request, 'setup/details.html', {'chain':chain, 'rented_services':rented_services, 'own_service':own_service, 'pkgs_weight':pkgs_weight})
 
@csrf_exempt    
def create_local_dist(request):
	print 'rP: ',request.POST
	context = {}
	lcl_distr = LocalDistributionMember.objects.create()
	lcl_distr.save()
	try:
		subs  = request.user.subscriber
	except:
		subs = request.user.useraccount.marketer.subscriber
	service_chain = ShippingChain.objects.get(pk=request.POST.get('service_chain'), subscriber=subs)
	rent_service_form = RentServiceForm(instance = service_chain, origin=request.POST.get('origin'), destination=request.POST.get('destination'), subscriber=subs)
	print "RSF: ", rent_service_form.destination_distributor
	return render(request,'setup_snippet/distributor_locs.html', {'rent_service_form':rent_service_form})




	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
