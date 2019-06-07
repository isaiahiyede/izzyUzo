from sokohaliAdmin.models import newFedExShippingCosts, costcalc_settings
from django.db.models import Sum

class BaseCostCalc(object):
    
    def __init__(self, costcalc):
        
        self.dim_weight_factor    = costcalc.dim_weight_factor
        self.lb_kg_factor         = costcalc.lb_kg_factor
        self.kg_lb_factor         = costcalc.kg_lb_factor
        
        self.exchange_rate        = costcalc.dollar_exchange_rate
        
        self.insuranceRate        = costcalc.export_insurance_rate
        self.consolidationRate    = costcalc.export_consolidation_rate
        
        # self.unitAirFreight1Cost       = costcalc.unit_cost_export_air_freight_1
        # self.unitAirFreight2Cost       = costcalc.unit_cost_export_air_freight_2
        # self.unitAirFreight3Cost       = costcalc.unit_cost_export_air_freight_3
        # self.unitAirFreight4Cost       = costcalc.unit_cost_export_air_freight_4
        # self.unitAirFreight5Cost       = costcalc.unit_cost_export_air_freight_5
        self.export_min_shipping_charge = costcalc.export_min_shipping_charge
    



