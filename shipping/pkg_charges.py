from general.custom_functions import get_local_freight_from_state, get_local_freight_from_state_hd, marketingmember_costcalc, marketing_member
from service_provider.models import LocalDistributorLocation, WarehouseLocation
from usps_helpers import get_pickup_charge
import itertools
from django.forms.models import model_to_dict


def calculate_pickup_charge(request, handling_option, pkg, pkg_warehouse):

    if handling_option == 'drop-at-location':
        location_id = request.session['dropoff_location_id']
        location = LocalDistributorLocation.objects.get(pk = location_id)
        location_member = location.region.courier
        if location_member.has_configured_rates:
            return get_local_freight_from_state(request, pkg.box_weight_higher(), location_id)

    elif handling_option in ['drop-at-postoffice', 'pick-up-package']:
        shipping_origin = request.session.get('shipping_origin',"None")
        shipping_destination = request.session.get('shipping_destination',"None")
        WHaddress = request.session.get('WHaddress')
        location_id = WarehouseLocation.objects.get(id=WHaddress)
        if shipping_origin == 'United States':
            lb_country = shipping_destination
        else:
            lb_country = shipping_origin
        costcalc = marketingmember_costcalc(request,lb_country)
        destZipCode = location_id.zip_code
        pick_up_charge_D = get_pickup_charge(request, pkg, "usps", destZipCode)

        print 'pick_up_charge_D: ',pick_up_charge_D
        pick_up_charge_N = float(pick_up_charge_D) * float(costcalc.dollar_exchange_rate)
        return pick_up_charge_D, pick_up_charge_N


def calculate_last_mile_charges(request, pkg, origin, destination, direction):
    mm = marketing_member(request)

    print 'origin -- destination:', origin , destination
    if origin == 'United States':
        lb_country = destination
    elif request.session.has_key('lb_country'):
        lb_country = request.session.get('lb_country')
    else:
        lb_country = origin

    costcalc = marketingmember_costcalc(request,lb_country)
    WHaddress = request.session.get('WHaddress')
    print "wha2:",WHaddress
    Location = WarehouseLocation.objects.get(id = WHaddress)
    print "la:",Location
    distributor = mm.get_route_shipping_distributor(origin, destination, direction)
    print 'calculate_last_mile_charges | distributor: ',distributor
    if distributor == None:
        pick_up_charge_D = pick_up_charge_N = 0.0
        return pick_up_charge_D, pick_up_charge_N
    elif distributor.has_api:
        print "its here"
        destZipCode = Location.zip_code
        print "DZC:", destZipCode
        pick_up_charge_D = get_pickup_charge(request, pkg, "usps", destZipCode)
        print "pick_up_charge_D: ",pick_up_charge_D
        print type(pick_up_charge_D)
        if type(pick_up_charge_D) != str or type(pick_up_charge_D) != int:
            pick_up_charge_D = 0.0
        else:
            pass
        pick_up_charge_N = float(pick_up_charge_D) * float(costcalc.dollar_exchange_rate)
        # del request.session['WHaddress']
        return pick_up_charge_D, pick_up_charge_N
    else:
        #return get_local_freight_from_state(request, pkg.box_weight_higher(), distributor.id)
        # print "pkg: ",pkg
        # print "got here"
        print "state of origin:", pkg.delivery_address.state
        # print "weight:",pkg.box_weight_higher()
        return get_local_freight_from_state_hd(request, pkg.box_weight_higher(), pkg.delivery_address.state, destination)




        #found = any(itertools.ifilter(lambda x:x[1] == state, CONTIGUOUS_STATES))
        # print CONTIGUOUS_STATES
        # for k, v in CONTIGUOUS_STATES:
        #     print k, v
