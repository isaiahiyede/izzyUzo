from sokohaliAdmin.models import PreDefinedBoxes, CostCalcSettings
from general.models import UserAccount
from datetime import datetime
import math
from general.custom_functions import country_freight_costs, country_exchange_rate, new_fedex_data,\
                                   costcalc_settings, total_SelectBoxWeight, total_EnterDimensionWeight, shipping_Weight, \
                                   get_marketing_member_shipping_rate, get_local_freight_from_state, get_local_freight_from_state_hd, \
                                   has_special_rate_for_route, marketingmember_costcalc



def PackageCostCalc(request, shippingWeight, shippingWeight_kg, origin, destination, costcalc, lb_country):

    print "country chain: ",lb_country
    print "costcalc: ", costcalc

    if costcalc is None:
        costcalc = marketingmember_costcalc(request,lb_country)

    #weightFactor                  = costcalc.dim_weight_factor
    #lb_kg_factor                  = costcalc.lb_kg_factor

    exchange_rate                 = costcalc.dollar_exchange_rate

    is_promo_on                   = costcalc.is_promo_on

    VAT_rate                      = costcalc.vat_rate / 100.0
    INS_rate                      = costcalc.insurance_rate / 100.0
    handling_charge_fee           = costcalc.handling_charge_fee

    Consolidation_Fee             = costcalc.consolidation_fee
    Unit_Strip_My_Package_Fee     = costcalc.unit_strip_package_fee
    Min_Strip_My_Package_Fee      = costcalc.strip_package_fee_min


    shipping_rate_air_D = get_marketing_member_shipping_rate(request, origin, destination, 'air', shippingWeight)
    shipping_rate_sea_D = get_marketing_member_shipping_rate(request, origin, destination, 'sea', shippingWeight_kg)
    shipping_rate_express_D = get_marketing_member_shipping_rate(request, origin, destination, 'express', shippingWeight_kg)

    class DeliveryCostOptions(object):

        def __init__(self, shipping_weight, shipping_weight_kg):

            self.shippingWeight                = shipping_weight
            self.shippingWeight_kg             = shipping_weight_kg

        def local_freight_D(self):
            shipping_option = request.session['handling_option']

            if shipping_option == 'send-from-shop':
                return 0

            elif shipping_option == 'drop-at-location':
                #drop_at_location_id = request.session['drop_at_location_id']
                return 0

            elif shipping_option == 'drop-at-postoffice':
                return 0

            elif shipping_option == 'pick-up-package':
                return 0


        def air_freight(self):
            #default value
            shipping_rate_D = shipping_rate_air_D
            print 'shipping_rate_air_D: ',shipping_rate_D

            user_special_rate = has_special_rate_for_route(request, origin, destination, 'air')
            if user_special_rate[0] == True:
                shipping_rate_D = user_special_rate[1]
                print 'user_special_rate|air|shipping_rate_D: ',shipping_rate_D

            try:
               return (shipping_rate_D  * self.shippingWeight * 100)/100
            except:
               return 0


        def sea_freight(self):
            #default value
            shipping_rate_D = shipping_rate_sea_D
            print 'shipping_rate_sea_D: ',shipping_rate_D

            user_special_rate = has_special_rate_for_route(request, origin, destination, 'sea')
            if user_special_rate[0] == True:
                shipping_rate_D = user_special_rate[1]
                print 'user_special_rate|sea|shipping_rate_D: ',shipping_rate_D

            try:
                return (shipping_rate_D * self.shippingWeight * 100)/100
            except:
                return 0


        def express_freight(self):
            #default value
            shipping_rate_D = shipping_rate_express_D
            print 'shipping_rate_express_D: ',shipping_rate_D

            user_special_rate = has_special_rate_for_route(request, origin, destination, 'express')
            if user_special_rate[0] == True:
                shipping_rate_D = user_special_rate[1]
                print 'user_special_rate|air|shipping_rate_D: ',shipping_rate_D

            try:
               return (shipping_rate_D  * self.shippingWeight * 100)/100
            except:
               return 0


        def cost_per_lb_air(self):
           costPerLbAir = shipping_rate_air_D
           if costPerLbAir == None:
                return 0
           print 'ca:',costPerLbAir
           return costPerLbAir

        def cost_per_lb_sea(self):
           costPerLbSea = shipping_rate_sea_D
           if costPerLbSea == None:
                return 0
           print 'cs:',costPerLbSea
           return costPerLbSea

        def cost_per_lb_express(self):
           costPerLbExpress = shipping_rate_express_D
           if costPerLbExpress == None:
                return 0
           print 'ce:',costPerLbExpress
           return costPerLbExpress



    #Creation of an instance with the name 'calc'
    calc = DeliveryCostOptions(shippingWeight, shippingWeight_kg)
                               # totalSelectBoxWeight, totalSelectBoxWeight_kg,
                               # totalEnterDimensionWeight, totalEnterDimensionWeight_kg,
                               # totalUserShipmentWeight, totalUserShipmentWeight_kg)

    # shippingWeight      = calc.shippingWeight
    # shippingWeight_kg   = calc.shippingWeight_kg
    # totalSelectBoxWeight          = calc.totalSelectBoxWeight
    # totalSelectBoxWeight_kg       = calc.totalSelectBoxWeight_kg
    # totalEnterDimensionWeight     = calc.totalEnterDimensionWeight
    # totalEnterDimensionWeight_kg  = calc.totalEnterDimensionWeight_kg
    # totalUserShipmentWeight        = calc.totalUserShipmentWeight
    # totalUserShipmentWeight_kg     = calc.totalUserShipmentWeight_kg

    airFreight          = calc.air_freight()

    localFreight_D      = calc.local_freight_D()

    print "Local Freight Cost: ", localFreight_D

    airFreight_N        = math.ceil((airFreight * exchange_rate) * 100)/100
    seaFreight          = calc.sea_freight()
    seaFreight_N        = math.ceil((seaFreight * exchange_rate) * 100)/100

    expressFreight          = calc.express_freight()
    expressFreight_N        = math.ceil((expressFreight * exchange_rate) * 100)/100

    costPerLbAir        = calc.cost_per_lb_air()
    costPerLbSea        = calc.cost_per_lb_sea()
    costPerLbExpress    = calc.cost_per_lb_express()

    #officePickupOutLag, officePickupOutLag_N, homeDelivInLag, homeDelivInLag_N, homeDelivOutLag, homeDelivOutLag_N = new_fedex_data().localShippingCharges(shippingWeight_kg, exchange_rate)

    # return shippingWeight, shippingWeight_kg, totalSelectBoxWeight, totalSelectBoxWeight_kg, \
    #     totalEnterDimensionWeight, totalEnterDimensionWeight_kg, totalUserShipmentWeight   , totalUserShipmentWeight_kg, \
    #     localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
    #     costPerLbAir, costPerLbSea, exchange_rate
    return localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
        costPerLbAir, costPerLbSea, costPerLbExpress, exchange_rate, expressFreight, expressFreight_N
        #officePickupOutLag, officePickupOutLag_N, homeDelivInLag, homeDelivInLag_N, \
        #homeDelivOutLag, homeDelivOutLag_N,



def freight_cost_dict(request, shippingWeight, shippingWeight_kg, origin, destination, costcalc):

    print "origin - destination: ", origin,destination    

    shipping_origin        = request.session.get('shipping_origin',"None")
    shipping_destination   = request.session.get('shipping_destination',"None")

    print "O - D: ", shipping_origin, shipping_destination

    if shipping_origin == 'United States':
        lb_country = shipping_destination
    else:
        lb_country = shipping_origin

    localFreight_D, airFreight, airFreight_N, seaFreight, seaFreight_N, \
    costPerLbAir, costPerLbSea, costPerLbExpress, exchange_rate, expressFreight, expressFreight_N = PackageCostCalc(request, shippingWeight, shippingWeight_kg, origin, destination, costcalc, lb_country)

    # return {'AF': airFreight, 'SF': seaFreight,
    #         'OP': 0.0, 'AP': officePickupOutLag, 'WL': homeDelivInLag, 'AL': homeDelivOutLag}

    return {'AF': airFreight, 'SF': seaFreight, 'EX': expressFreight, 'localFreight_D': localFreight_D, 'exchange_rate': exchange_rate}#, 'HD': homeDelivOutLag}



def get_freight_costs(request, packages, origin, destination, costcalc):
    delivery_intl_freight_D = delivery_local_freight_D = 0
    try:
        dvm = request.session['dvm']
        print "dvm:",dvm
    except:
        dvm = 'AF - HD'
    #shipping_weight = None


    for pkg in packages:
         print "here now"
         shippingWeight     = pkg.box_weight_higher()
         shippingWeight_kg  = pkg.box_weight_higher_K()
         print "here again"
         shipping_cost_dict = freight_cost_dict(request, shippingWeight, shippingWeight_kg, origin, destination, costcalc)
         exchange_rate      = shipping_cost_dict['exchange_rate']
         print "shipWght,shipWght_k,ship_cost_dict,exh_rate:",shippingWeight, shippingWeight_kg,shipping_cost_dict, exchange_rate

         intl_freight_D     = shipping_cost_dict[dvm.split(' - ')[0]]
         print "intl_freight_D:",intl_freight_D
         delivery_intl_freight_D += intl_freight_D
         print "delivery_intl_freight_D: ",delivery_intl_freight_D
         pkg.intl_freight_D = intl_freight_D
         pkg.intl_freight_N = intl_freight_D * exchange_rate

         local_freight_D = shipping_cost_dict['localFreight_D']
         delivery_local_freight_D += local_freight_D
         pkg.local_freight_D = local_freight_D
         pkg.local_freight_N = local_freight_D * exchange_rate

         if dvm[0] == "S":
            pkg.shipping_method = "Sea Freight"
         elif dvm[0] == "A":
            pkg.shipping_method = "Air Freight"
         else:
            pkg.shipping_method = "Express"

         # pkg.shipping_method =

         pkg.save()

    delivery_total_freight_D = delivery_intl_freight_D + delivery_local_freight_D

    request.session['delivery_total_freight_D'] = delivery_total_freight_D

    print 'delivery_total_freight_D: ', request.session['delivery_total_freight_D']

    print 'getting here'
    #request.session['delivery_intl_freight_D'] = intl_freight_D
    #request.session['delivery_local_freight_D'] = local_freight_D

    request.session['delivery_intl_freight_D'] = delivery_intl_freight_D
    request.session['delivery_local_freight_D'] = delivery_local_freight_D

    return delivery_intl_freight_D, delivery_local_freight_D, delivery_total_freight_D
