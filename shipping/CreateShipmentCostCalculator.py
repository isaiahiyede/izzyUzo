from general.models import UserAccount
from datetime import datetime
import math
#from shipping_extra_dependencies.custom_functions import *
from general.custom_functions import currencyEquivalentOfDollar, costcalc_settings, country_exchange_rate, \
                                    country_freight_costs, marketingmember_costcalc



def CreateShipmentCostCalc(request, shipment_info, country, cost_calc=None):
    #cost_calc = costcalc_settings()
    print "country", country
    country = country
    '''check if cost_calc is sent for existing package'''
    if cost_calc == None:
        cost_calc                     = marketingmember_costcalc(request,country)

    weightFactor                  = cost_calc.dim_weight_factor
    lb_kg_factor                  = cost_calc.lb_kg_factor
    exchange_rate               = cost_calc.dollar_exchange_rate
    #exchange_rate                 = country_exchange_rate(country, cost_calc)

    admin_VAT             = cost_calc.vat_rate

    VAT_rate                = admin_VAT/100
    admin_INS               = cost_calc.insurance_rate
    INS_rate                = admin_INS/100
    #New Pricing Model for Service Charge (January 2014) start
    sc_dollar_rate_1        = cost_calc.sc_dollar_rate_1
    sc_dollar_rate_2        = cost_calc.sc_dollar_rate_2
    sc_dollar_rate_3        = cost_calc.sc_dollar_rate_3
    service_charge_min_fee  = cost_calc.service_charge_min_fee
    handling_charge_fee     = cost_calc.handling_charge_fee

    #New Pricing Model for Service Charge (January 2014) end
    Consolidation_Fee             = cost_calc.consolidation_fee
    Unit_Strip_My_Package_Fee     = cost_calc.unit_strip_package_fee
    Min_Strip_My_Package_Fee      = cost_calc.strip_package_fee_min

    customsClearing             = cost_calc.customs_clearing_fee

    pkg_count = shipment_info["pkg_count"]

    #item_count = get_no_of_items(request)
    item_count = shipment_info["item_count"]

    #shippingWeight           = shipping_Weight(request)
    shippingWeight           = shipment_info["shippingWeight"]
    shippingWeight_kg        = float(shippingWeight * lb_kg_factor)

    #cart_value               = cartWorth(request)
    try:
      cart_value               = shipment_info["cart_value"]
    except:
      cart_value               = 0.0
    #cart_value_N             = cart_value * dollarNairaRate

    total_freight_D               = shipment_info["total_freight_D"]
    total_freight_N               = total_freight_D  / exchange_rate

    class ShipmentCosts(object):

         def __init__(self, pkg_count, item_count, shippingWeight, shippingWeight_kg, cart_value, total_freight_D, total_freight_N, VAT_rate, \
                      INS_rate, sc_dollar_rate_1, sc_dollar_rate_2, sc_dollar_rate_3, Consolidation_Fee, Unit_Strip_My_Package_Fee, \
                      Min_Strip_My_Package_Fee, customsClearing):
              self.pkg_count                = pkg_count
              self.item_count               = item_count
              self.shippingWeight           = shippingWeight
              self.shippingWeight_kg        = shippingWeight_kg
              self.cart_value               = cart_value
              self.total_freight_D          = float(total_freight_D)
              self.total_freight_N          = float(total_freight_N)
              self.VAT_rate                 = VAT_rate
              self.INS_rate                 = INS_rate
              self.sc_dollar_rate_1         = sc_dollar_rate_1
              self.sc_dollar_rate_2         = sc_dollar_rate_2
              self.sc_dollar_rate_3         = sc_dollar_rate_3
              self.Consolidation_Fee        = Consolidation_Fee
              self.Unit_Strip_My_Package_Fee= Unit_Strip_My_Package_Fee
              self.Min_Strip_My_Package_Fee = Min_Strip_My_Package_Fee
              self.customs_clearing_fee     = customsClearing

         def package_count(self):
              return self.pkg_count

         def item_count(self):
              return self.item_count

         def lb_weight(self):
              return self.shippingWeight

         def kg_weight(self):
              return self.shippingWeight_kg

         def Freight_D(self):
              return self.total_freight_D

         def Freight_N(self):
              return self.total_freight_N

         #New Pricing Model for Service Charge (January 2014)
         def ServiceCharge_D(self):

              SC = handling_charge_fee
              #equivalentValue = currencyEquivalentOfDollar(exchange_rate, dollarNairaRate, SC)
              #return SC
              #return equivalentValue
              return SC


         def consolidation_charge(self):
              #equivalentValue = currencyEquivalentOfDollar(exchange_rate, dollarNairaRate, self.Consolidation_Fee)
              #return float(equivalentValue)
              return self.Consolidation_Fee

         def Insurance(self):
              ins = float(self.INS_rate) * (float(self.total_freight_D) + float(self.cart_value))
              return ins

         def StripMyPackageFee(self):
              #equivalentValue = currencyEquivalentOfDollar(exchange_rate, dollarNairaRate, Min_Strip_My_Package_Fee)
              equivalentValue = Min_Strip_My_Package_Fee

              if self.item_count < 6:
                   return float(equivalentValue)
              else:
                   fee = float(item_count * Unit_Strip_My_Package_Fee)
                   if fee < float(equivalentValue):
                        return float(equivalentValue)
                   else:
                        return fee

         def ValueAddedTax_D(self):
              vat_d = float(self.VAT_rate * (self.total_freight_D + self.Insurance() + self.ServiceCharge_D() + self.consolidation_charge() + self.StripMyPackageFee()))
              return vat_d

         def CustomsClearingFee(self):
            return float(self.customs_clearing_fee * shippingWeight_kg)

    paycalc = ShipmentCosts(pkg_count, item_count, shippingWeight, shippingWeight_kg, \
                            cart_value, total_freight_D, total_freight_N, VAT_rate, INS_rate, \
                            sc_dollar_rate_1, sc_dollar_rate_2, sc_dollar_rate_3, Consolidation_Fee, \
                            Unit_Strip_My_Package_Fee, Min_Strip_My_Package_Fee, customsClearing)

    total_freight_D          = paycalc.Freight_D()
    VAT_D                    = paycalc.ValueAddedTax_D()
    #VAT_N                    = VAT_D * exchange_rate
    totalServiceCharge_D     = paycalc.ServiceCharge_D()
    #totalServiceCharge_N     = totalServiceCharge_D * exchange_rate
    CON_D                    = paycalc.consolidation_charge()
    #CON_N                    = CON_D * exchange_rate
    PSDG_D                   = paycalc.Insurance()
    #PSDG_N                   = PSDG_D * exchange_rate
    SMP_D                    = paycalc.StripMyPackageFee()
    #SMP_N                    = SMP_D * exchange_rate

    #customsClearing_N        = paycalc.CustomsClearingFee()
    #customsClearing_D        = customsClearing_N / exchange_rate

    freight_VAT_SC_D         = total_freight_D + VAT_D + totalServiceCharge_D
    #freight_VAT_SC_N         = freight_VAT_SC_D * exchange_rate

    #print 'freight_VAT_SC_D: ',freight_VAT_SC_D
    #print 'total_freight_D, cart_value: ',total_freight_D, cart_value
    coverage_amount_D        = float(total_freight_D) + float(cart_value)
    #coverage_amount_N        = coverage_amount_D * exchange_rate

    return total_freight_D, VAT_D, totalServiceCharge_D, \
            CON_D, PSDG_D, SMP_D, freight_VAT_SC_D, coverage_amount_D, exchange_rate

    # return total_freight_D, VAT_D, VAT_N, totalServiceCharge_D, totalServiceCharge_N, \
    #         CON_D, CON_N, PSDG_D, PSDG_N, SMP_D, SMP_N, freight_VAT_SC_D, freight_VAT_SC_N, \
    #         coverage_amount_D, coverage_amount_N, exchange_rate
