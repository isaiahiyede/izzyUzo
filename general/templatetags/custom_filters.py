from django import template
from django.template.defaultfilters import stringfilter
from general.custom_functions import costcalc_settings, remove_, get_marketing_member_users , marketing_member
from datetime import date, timedelta
from general.models import pkg_statuses, UserAccount, ActionHistory, MessageCenter, MessageCenterComment
from sokohaliAdmin.models import *
from shipping.models import *
from service_provider.models import *
#from export.models import *
import datetime
import time
import pytz
from django.db.models import Q, Sum
from itertools import chain
from operator import attrgetter
from service_provider.forms import EditMarketingMemberForm
from service_provider.views import subscriber_marketer, request_subscriber
from django.contrib.auth.models import Group 



register = template.Library()


@register.filter
@stringfilter
def uppercase(value):
    return value.upper()



@register.simple_tag
def get_affiliate_address(affiliate, suite_no):
    return affiliate.full_address(suite_no)


@register.filter
def remove_from_val(val):
    return remove_(val)

# @register.simple_tag
# def items_filter(obj):
#     if hasattr(obj, 'order_balance_D'):
#         return obj.orderproduct_set.filter(package = None)
#     return obj.shipmentitem_set.filter(package = None)



def cap_first_letter(value):
    new_value = value[0].upper() + value[1:]
    return remove_(new_value)


@register.simple_tag
def shipment_objs_info(linked_objs, list_type, tag):
    linked_objs_dict = dict()
    for entry in linked_objs:
        entry_val = entry['status']
        if entry_val in linked_objs_dict.keys():
            new_entry_val = linked_objs_dict[entry_val]
            linked_objs_dict[entry_val] = new_entry_val + 1
        else:
            linked_objs_dict[entry_val] = 1
    #return linked_pkgs_dict
    result = ''
    for key,val in linked_objs_dict.iteritems():
        if val > 1:
            obj_type = list_type+'s'#'Packages'
        else:
            obj_type = list_type#'Package'
        if key != None:
            if tag == 'p':
                result +='%s %s %s' %(val, obj_type, cap_first_letter(key))
            else:
                result +='%s %s %s /' %(val, obj_type, cap_first_letter(key))
    #print result
    return result


#@register.inclusion_tag('zaposta_snippet/pkg_other_statuses.html')
@register.simple_tag
def pkg_other_statuses(current_status):
    try:
        current_status = current_status.lower()
    except:
        pass

    # pkg_statuses = ['Delivered', 'Ready for Collection', 'Enroute to Delivery', 'Prepared for Delivery',
    #                     'Processing for Delivery', 'Clearing Customs', 'Departed', 'Delivered to Carrier',
    #                     'Assigned to batch', 'Prepared for Shipping', 'Received']
    pkg_statuses_copy = list(pkg_statuses)
    pkg_statuses_copy.reverse()
    current_status_index = [index for index, status in enumerate(pkg_statuses_copy) if status.lower() == current_status]
    #print "current_status: ",current_status
    #print "current_status_index: ",current_status_index
    #print "current_status_index[0]: ",current_status_index[0]
    #print pkg_statuses[:current_status_index[0]]
    try:
        other_statuses = pkg_statuses_copy[:current_status_index[0]]
    except:
        other_statuses = pkg_statuses_copy#[]

    #print 'other_statuses: ',other_statuses

    other_statuses_div = ''
    for status in other_statuses:
        other_statuses_div += '<div class="col-md-12"><p>??-??-??- ??:?? GMT - '+status+'</p> </div>'

    return other_statuses_div
    #return {'other_statuses': other_statuses}


@register.simple_tag
def get_price(qty):
    return float(qty * 399)



@register.simple_tag
def pkg_statuses(pkg_pk):
    all_pkg_statuses = ActionHistory.objects.filter(obj_id=pkg_pk)
    other_statuses_div = ''
    for statuses in all_pkg_statuses:
        format_date = datetime.datetime.strptime(str(statuses.created_on).split(" ")[0],'%Y-%m-%d')
        new_date = format_date.strftime('%b %d, %Y')
        other_statuses_div += '<div class="col-md-12"><p>' + new_date + ' - ' + statuses.action +'</p> </div>'

    return other_statuses_div



@register.simple_tag
def invoice_name(invoice_full_path):
    splitted_invoice_name = invoice_full_path.split('/')[-1]
    return splitted_invoice_name[0].upper() + splitted_invoice_name[1:]


@register.assignment_tag
def zpn_available_slots_left():
    return costcalc_settings().zpn_available_slot_left()


@register.simple_tag
def months_and_year():
    months = ['January', 'February', 'March', 'April', 'May', \
                  'June', 'July', 'August', 'September', 'October', 'November', 'December']

    current_year = date.today().year
    months_and_year_opt = ''
    for month in months:
        months_and_year_opt += '<option value="%s-%s">%s %s</option>' %(month.lower(), current_year, month, current_year,)
    return months_and_year_opt
# @register.simple_tag
# def shipment_items_info(shipment_items):
#     print shipment_items
#     linked_dict = dict()
#     for entry in linked_pkgs:
#         entry_val = entry['status']
#         if entry_val in linked_pkgs_dict.keys():
#             new_entry_val = linked_pkgs_dict[entry_val]
#             linked_pkgs_dict[entry_val] = new_entry_val + 1
#         else:
#             linked_pkgs_dict[entry_val] = 1
#     #return linked_pkgs_dict
#     result = ''
#     for key,val in linked_pkgs_dict.iteritems():
#         if val > 1:
#             pkg = 'Packages'
#         else:
#             pkg = 'Package'
#         result +='<p>%s %s %s</p>' %(val, pkg, key)
#     #print result
#     return result



@register.simple_tag
def getBatchCount(request,status):
    try:
        marketer = marketing_member(request)
        subscriber = marketer.subscriber
    except:
        subscriber = request_subscriber(request)
    return Batch.objects.filter(deleted=False,subscriber=subscriber, status=status).count()



@register.simple_tag
def getPackageCount(request,action):

    packageCount = []
    if not action == "revoked":
        try:
            mm = marketing_member(request)
            subscriber = mm.subscriber
            imprt = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)),Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
        except:
            subscriber = request_subscriber(request)
            imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
        # Sub_WHM = subscriber.get_warehouses()
        # if Sub_WHM:
        # 	imprt  = ShippingPackage.objects.filter((Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
        # else:
        # 	imprt = ShippingPackage.objects.filter(Q(shipping_chain__subscriber=subscriber), Q(ordered = True), Q(is_estimate=False), Q(deleted=False))
    
        # export = ExportPackage.objects.filter(Q(user__useraccount__marketer = mm), Q(ordered = True), Q(is_estimate=False))
        # export_packages = export.filter(status=action).count()
        packageCount = imprt.filter(status=action).count()

    else:
        try:
            mm = marketing_member(request)
            subscriber = mm.subscriber
            imprt = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)),Q(ordered = True), Q(is_estimate=False), Q(deleted=True))
        except:
            subscriber = request_subscriber(request)
            imprt  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(deleted=True))

        packageCount = imprt.count()
    # packageCount = export_packages + import_packages
    return packageCount


@register.simple_tag
def userCount(request, action):
    users = 0
    useraccounts = get_marketing_member_users(request)
    if action == "Admin":
        users = useraccounts.filter(user__is_staff = True)
    elif action == "Flagged":
        users = useraccounts.filter(flagged = True)
    elif action == "De-Activated":
       users = useraccounts.filter(deactivated = True)
    elif action == "Address_activation":
        users = useraccounts.filter(address_activation = True)
    elif action == "New":
        time_24_hours_ago = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days=1)
        users = useraccounts.filter(registration_time__gte = time_24_hours_ago)
    elif action == "Unverified":
        users = useraccounts.filter(address_activation = False, address_activation_completed = True)
    else:
        users = useraccounts
    return users.count()


@register.simple_tag
def truckCount(request, action):
    counter = 0
    # useraccounts = get_marketing_member_users(request)
    if action == "All":
        counter = Trucking.objects.filter(deleted=False,archive=False).count()
    elif action == "New":
        counter = Trucking.objects.filter(status="New",deleted=False,archive=False).count()
    elif action == "Ongoing":
       counter = Trucking.objects.filter(status="Ongoing",deleted=False,archive=False).count()
    elif action == "Completed":
        counter = Trucking.objects.filter(status="Completed",deleted=False,archive=False).count()
    return counter


@register.simple_tag
def add_space(word):
    the_new_word = list(word)
    new_word = []
    for i in the_new_word:
        if i.isupper():
            i = " " + i
        new_word.append(i)
    return "".join(new_word)


@register.simple_tag
def remove_space(word):
    new_word = str(word).replace('-',' ').replace('_',' ').title()
    return new_word

@register.assignment_tag
def get_active_batches(request):
    try:
        marketer = marketing_member(request)
        subscriber = marketer.subscriber
    except:
        subscriber = request_subscriber(request)
    # print "the subscriber: ",subscriber
    # print "marketer: ",marketer
    new_batch_count = Batch.objects.filter(deleted=False,subscriber=subscriber, status="New")
    return new_batch_count.count()


@register.assignment_tag
def get_unprocessed_packages(request):
    mm = marketing_member(request)
    try:
        mm = marketing_member(request)
        subscriber = mm.subscriber
        unprocessed_packages_count  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(prepared_for_shipping=False)).count()
    except:
        subscriber = request_subscriber(request)
        unprocessed_packages_count  = ShippingPackage.objects.filter((Q(shipping_chain__subscriber = subscriber) | Q(origin_warehouse__offered_by = subscriber) | Q(destination_warehouse__offered_by = subscriber)), Q(ordered = True), Q(is_estimate=False), Q(prepared_for_shipping=False)).count()
    return unprocessed_packages_count

@register.assignment_tag
def get_new_messages_count(request):
    mm = marketing_member(request)
    message_object = MessageCenter.objects.filter(user__useraccount__marketer=mm,new=True).count()
    return message_object


@register.assignment_tag
def editTermsConditions(request):
    mm = marketing_member(request)
    form = EditMarketingMemberForm(instance=mm)
    return form


@register.simple_tag
def getDifference(firstValue,secondValue):
    diff = firstValue - secondValue
    return round(diff,2)


@register.simple_tag
def getMessages(request,status):
    mm = marketing_member(request)
    messageObject = MessageCenter.objects.filter(user__useraccount__marketer = mm)
    if status == "New":
        message_count = messageObject.filter(new=True)
    elif status == "replied":
        message_count = messageObject.filter(replied=True)
    else:
        message_count = messageObject.filter(archive=True)
    return message_count.count()


@register.simple_tag
def remove_underscr(string):
    return remove_(string)


@register.simple_tag
def getReceivedItems(request):
    mm = marketing_member(request)
    return NotifyUser.objects.filter(user__useraccount__marketer = mm).count()


@register.simple_tag
def get_all_subscriber_values(subscriber,obj,value):
    if value == "pkg_processed_by_sub":
        pkgs = ShippingPackage.objects.filter((Q(shipping_chain = obj),Q(origin_warehouse__offered_by = subscriber),Q(ordered = True), Q(is_estimate=False), Q(prepared_for_shipping=True)))
    elif value == "pkg_processed_for_sub":
        pkgs = ShippingPackage.objects.filter((Q(shipping_chain = obj),Q(destination_warehouse__offered_by = subscriber),Q(ordered = True), Q(is_estimate=False), Q(prepared_for_shipping=True)))
    return pkgs.count()


@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all()



@register.simple_tag
def shoppingRequestCount(request, action):
    counter = 0
    # useraccounts = get_marketing_member_users(request)
    if action == "All":
        counter = ShippingItem.objects.filter(deleted=False,archive=False).count()
    elif action == "Received":
        counter = ShippingItem.objects.filter(status="Received",deleted=False,archive=False).count()
    return counter


@register.simple_tag
def notificationCount(request, action):
    mm = marketing_member(request)
    counter = 0
    # useraccounts = get_marketing_member_users(request)
    if action == "All":
        counter = ShippingItem.objects.filter(~Q(tag="Shopping"), user__useraccount__marketer=mm)
    elif action == "Received":
        counter = ShippingItem.objects.filter(~Q(tag="Shopping"), user__useraccount__marketer=mm, status="Received")
    return counter.count()













