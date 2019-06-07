from django.db import models
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from django.utils import timezone
from cities_light.models import *
from django.template.defaultfilters import slugify
from forex_python.converter import CurrencyCodes
from general.modelfield_choices import COUNTRY, STATE, SERVICE_TYPE, DIRECTION_TYPE, WEIGHT_UNIT, CURRENCY, ShippingMethod,\
                                        MARKETINGMEMBER_COLORS, BANK_CURRENCY, OFFERED_SERVICES, SHIPPING_METHOD




'''Services Marketplace'''
class BaseName(models.Model):
    name                =    models.CharField(max_length = 75, null=True, blank=True)

    class Meta:
        abstract = True

class BaseAddress_Info(models.Model):
    address1            =    models.CharField(max_length = 100)
    address2            =    models.CharField(max_length = 100)
    city                =    models.CharField(max_length = 75)
    state               =    models.CharField(max_length = 125)
    country             =    models.CharField(max_length = 125)
    phone_number        =    models.CharField(max_length = 50)
    zip_code            =    models.CharField(max_length = 10)

    def complete_address(self):
        return "%s, %s, %s, %s, %s" %(self.address1, self.address2, self.city, self.state, self.country)

    class Meta:
        abstract = True


class BaseAddressInfo(BaseName, BaseAddress_Info):

    class Meta:
        abstract = True


class Subscriber(BaseAddress_Info):
    user        =  models.OneToOneField(User)
    photo_id    =  models.ImageField(upload_to = "subscriber-photo-id/%Y/%m/%d", null=True, blank=True)
    #service               =  models.ForeignKey('Service', null=True, blank=True)

    def __unicode__(self):
        return self.user.get_full_name()

    def get_warehouses(self):
        return self.warehousemember_set.all()

    def get_shippers(self):
        return self.shippingmember_set.all()

    def get_clearing_agents(self):
        return self.customclearingagent_set.all()
    #
    def get_all_shipping_chains(self):
        return self.shippingchain_set.all()

    def get_marketer(self):
        return self.marketingmember

    def get_all_packages(self):
       return self.get_all_shipping_chains().count()

    def get_services_offered_by_subscriber(self):
        services_list = [{'warehousemember__offered_by':self},{'shippingmember__offered_by':self},{'customclearingagent__offered_by':self}]
        services_offered = []
        for service in services_list:
            kwargs = service
            services_offered.append(Subscriber.objects.filter(**kwargs))
        return services_offered

    def get_subscriber_shipping_chain_route(self, origin, destination):
        #print 'direction, origin, destination: ', origin, destination
        #return self.get_service(service_type).shipping_chain.get(Q(direction__icontains = direction), Q(origin = origin) |  Q(destination = destination) | Q(origin = destination) |  Q(destination = origin))
        return self.shippingchain_set.get(Q(origin = origin),  Q(destination = destination))



class BaseImportantInfo(models.Model):
    key_official_name               =       models.CharField(max_length = 50)
    key_official_address            =       models.TextField(null=True)
    iac_license                     =       models.FileField(upload_to = "warehouse-member/IAC-License", null=True, blank=True)
    incorportation_doc              =       models.FileField(upload_to = "warehouse-member/Incorportation-Doc", null=True, blank=True)
    key_official_passport_id        =       models.FileField(upload_to = "warehouse-member/Key-Official-Passport-ID", null=True, blank=True)
    key_official_photo              =       models.FileField(upload_to = "warehouse-member/Key-Official-Photo", null=True, blank=True)
    contract_doc                    =       models.FileField(upload_to = "warehouse-member/Contract-Doc", null=True, blank=True)
    registration_time               =       models.DateTimeField(default = timezone.now)

    def __unicode__(self):
        return str(self.key_official_name)

    class Meta:
        abstract = True


class MarketingMember(BaseAddress_Info):
    subscriber            =    models.OneToOneField('Subscriber', null=True, blank=True)
    active                =    models.BooleanField(default = False)

    #name                  =    models.CharField(max_length = 100)
    email                 =    models.EmailField()
    #user                  =    models.OneToOneField(User, null=True, blank=True)
    subdomain_name        =    models.CharField(max_length = 30, null=True, blank=True)

    storefront            =    models.BooleanField(verbose_name="Do you want a Customisable Storefront?", default = False)
    storefront_name       =    models.CharField(max_length = 50, help_text="***Example: storefront_name.sokohali.com***")
    storefront_color      =    models.CharField(max_length = 20, choices = MARKETINGMEMBER_COLORS, default='blue')

    logo                  =    models.ImageField(verbose_name="Storefront Logo", upload_to = "marketer_logos/%Y/%m/%d")
    ico                   =    models.ImageField(verbose_name="Storefront Icon", upload_to='marketer_icons/%Y/%m/%d')

    package_pickup        =    models.BooleanField(default = False)
    package_dropoff       =    models.BooleanField(default = False)

    #payment services
    store                 =    models.BooleanField(default = False)
    bank_deposit          =    models.BooleanField(verbose_name="Bank Deposit", default = False)
    card_payment          =    models.BooleanField(verbose_name="Debit cards: Visa, Mastercard, Verve", default = False)
    stripe                =    models.BooleanField(verbose_name="Stripe", default = False)
    paypal                =    models.BooleanField(verbose_name="PayPal", default = False)

    facebook_link         =   models.CharField(max_length = 100, null=True, blank=True)
    twitter_link          =   models.CharField(max_length = 100, null=True, blank=True)
    googleplus_link       =   models.CharField(max_length = 100, null=True, blank=True)
    linkedin_link         =   models.CharField(max_length = 100, null=True, blank=True)

    fax_number            =   models.CharField(max_length = 50, null=True, blank=True)
    domestic_shipping     =   models.BooleanField(default=False)
    #dollar_exchange_rate  =     models.FloatField(default = 200)

    #services              =   models.ManyToManyField("Service", blank=True)
    email_text             =   models.TextField(null=True, blank=True)
    faq                    =   models.TextField(null=True, blank=True)
    terms_and_cond        =    models.TextField(null=True, blank=True)
    random_code           =    models.CharField(max_length = 5, null=True, blank=True)
    #costcalc_instance    =    models.ForeignKey('sokohaliAdmin.CostCalcSettings', null=True, blank=True)
    #service               =  models.ForeignKey('Service', null=True, blank=True)


    def __unicode__(self):
        return "%s" %self.storefront_name

    def payment_activated(self):
        return self.bank_deposit or self.card_payment or self.stripe or self.paypal

    def get_subscriber(self):
        #return Service.objects.get(service_type = service_type, marketing_member = self)
        subscriber = self.subscriber
        print "subcriber:", subscriber
        return subscriber
        #return self.services.get(service_type = service_type)

    def get_shipping_chains(self):
        #service_type = 'shipping'
        return self.get_subscriber().shippingchain_set.all()

    #def get_shipping_direction_chains(self, service_type, direction):
    #    return self.get_service(service_type).shippingchain_set.filter(direction__icontains = direction)

    #def get_shipping_chain_route(self, service_type, direction, origin, destination):
    def get_shipping_chain_route(self, origin, destination):
        #print 'direction, origin, destination: ', origin, destination
        #return self.get_service(service_type).shipping_chain.get(Q(direction__icontains = direction), Q(origin = origin) |  Q(destination = destination) | Q(origin = destination) |  Q(destination = origin))
        route = self.get_subscriber().shippingchain_set.get(Q(origin = origin),  Q(destination = destination))
        return route 


    def get_shipping_chain_routes_list(self, direction, origin, destination):
        route_chain = self.get_shipping_chain_route(service_type, direction, origin, destination)
        return route_chain.routes_list()

    #def get_shipping_chain_route_warehouse(self, service_type, service_direction, origin, destination, direction):
    def get_shipping_chain_route_warehouses(self, origin, destination):
        #route_chain = self.get_service(service_type).shipping_chain.get(direction = direction, origin = origin, destination = destination)
        route_chain = self.get_shipping_chain_route(origin, destination)
        return route_chain.origin_warehouse, route_chain.destination_warehouse
        # if direction == "origin":
        #     warehouse = route_chain.origin_warehouse
        # elif direction == "destination":
        #     warehouse = route_chain.destination_warehouse
        # return warehouse

    def get_shipping_chain_route_warehouse_destination(self, origin, destination):
        route_chain = self.get_shipping_chain_route(origin, destination)
        return route_chain.destination_warehouse


    def get_shipping_chain_route_warehouse_origin(self, origin, destination):
        route_chain = self.get_shipping_chain_route(origin, destination)
        return route_chain.origin_warehouse


    def get_shipping_chain_route_shipper(self, direction, origin, destination):
        route_chain = self.get_shipping_chain_route(direction, origin, destination)
        shipping_member = None
        if direction == "origin":
            shipping_member = route_chain.import_shipper
        elif direction == "destination":
            shipping_member = route_chain.export_shipper
        return shipping_member


    def get_shipping_chain_route_clearing_agent(self, service_type, direction, origin, destination):
        route_chain = self.get_shipping_chain_route(service_type, direction, origin, destination)
        clearing_agent = None
        if direction == "import":
            clearing_agent = route_chain.import_clearing_agent
        elif direction == "export":
            clearing_agent = route_chain.import_clearing_agent
        return clearing_agent


    def get_route_shipping_distributor(self, origin, destination, direction):
        print 'origin, destination, direction: ', origin, destination, direction
        route_chain = self.get_shipping_chain_route(origin, destination)
        if direction == 'origin':
            print 'me'
            return route_chain.origin_distributor
        else:
            return route_chain.destination_distributor

        #print 'route_chain: ',route_chain
        #print 'origin, destination, country: ',origin, destination, country
        #if direction == 'origin':
        #    distributors = route_chain.origin_distributor.all()
        #else:
        #    distributors = route_chain.destination_distributor.all()
        #print 'distributors: ',distributors
        #distributors = route_chain.origin_distributor.all()
        ##print 'distributors: ',distributors
        ##return distributors.filter(country__name = country, active=True).distinct()
        #return distributors.filter(country__name = country, active=True).distinct()


    #def get_route_distributors_locations(self, origin, destination, country, state=None):
    def get_route_distributors_locations(self, origin, destination, direction, state=None):
        print 'origin, destination, direction: ',origin, destination, direction
        #print 'origin, destination, country: ',origin, destination, country
        #distributors = self.get_local_distributors(country)
        distributors = self.get_route_shipping_distributor(origin, destination, direction)

        locations = LocalDistributorLocation.objects.filter(region__courier__in = [distributors])
        #print 'locations: ',locations

        if state == None:
            return locations.values('id', 'city', 'state')
        else:
            return locations.filter(state = state, drop_off_available = True)
        # for distributor in distributors:
        #     print 'distributor: ',distributor
        #     loc = LocalDistributorLocation.objects.filter(region__courier = distributor, state = state, drop_off_available = True)
        #     #loc = LocalDistributorLocation.objects.filter(state = state, drop_off_available = True)
        #     print 'loc: ',loc
        # #return [location for distributor in distributors for location in distributor.localdistributorlocation_set.all()]
        # if state == None:
        #     return [location for distributor in distributors for region in distributor.localdistributorregion_set.all() for location in region.localdistributorlocation_set.all()]
        # else:
        #     return [location for distributor in distributors for region in distributor.localdistributorregion_set.all() for location in region.localdistributorlocation_set.filter(state__iexact = state, drop_off_available = True)]

    def get_route_delivery_method_rates(self, origin, destination, shipping_method=None):
        route_chain = self.get_shipping_chain_route(origin, destination)
        print "route_chain:", route_chain.id
        if shipping_method == None:
            delivery_methods = route_chain.shippingrate_set.all()

            delivery_methods_dict = {}
            shipping_methods = [val[0] for val in ShippingMethod] #ShippingMethod choices
            for val in shipping_methods:
                return_delivery_methods = delivery_methods.filter(shipping_method = val)
                delivery_methods_dict.update({val: return_delivery_methods})
            return delivery_methods_dict
        else:
            return route_chain.shippingrate_set.filter(shipping_method = shipping_method)

    def get_route_delivery_method_range_rate(self, origin, destination, shipping_method, weight):
        route_chain = self.get_shipping_chain_route(origin, destination)
        print "route_chain"
        shipping_rates = route_chain.shippingrate_set.filter(shipping_method = shipping_method)#, from_range__gte = weight, to_range__lt = weight)
        print shipping_rates
        for rate in shipping_rates:
            if rate.from_range <= weight <= rate.to_range:
                return rate.rate_D

    def get_all_shipping_rates(self):
        service_chains = self.get_subscriber().shippingchain_set.all().values_list('id')
        return ShippingRate.objects.filter(shipping_chain__pk_in = service_chains)

    # def get_all_import_warehouses(self):
    #     service_chains = self.get_service('shipping').shippingchain_set.all()
    #     return [service.import_warehouse for service in service_chains]

    def get_all_import_warehouses(self):
        service_chains = self.get_subscriber().shippingchain_set.all()
        print "service_chains:",service_chains
        return [service.origin_warehouse for service in service_chains]

    
    def banking_details(self):
        return self.bankaccount_set.all()
    
    
    # def get_shipping_chain_route_local_distributors(self, service_type, direction, origin, destination):
    #     route_chain = self.get_shipping_chain_route(service_type, direction, origin, destination)
    #     origin_distributor = None
    #     destination_distributor = None
    #     #print "origin, destination: ",origin, destination
    #     if direction == "Import":
    #         distributors = route_chain.import_local_distributor.all()
    #         #print distributors
    #         origin_distributor = distributors.filter(localdistributorlocation__country = origin).distinct()
    #         destination_distributor = distributors.filter(localdistributorlocation__country = destination).distinct()
    #     elif direction == "Export":
    #         distributors = route_chain.export_local_distributor.all()
    #
    #     return origin_distributor, destination_distributor


#class PostalCenter(BaseAddressInfo):
#    marketing_member    = models.ForeignKey(MarketingMember, null=True, blank=True)




# class Service(models.Model):
#     service_type          =       models.CharField(max_length = 75, choices = SERVICE_TYPE)
#     #shipping_chain        =       models.ManyToManyField("ShippingChain")
#     # marketing_member      =       models.ForeignKey(MarketingMember, null=True, blank=True)
#     #
#     # def __unicode__(self):
#     #     return "%s - %s" %(self.marketing_member.subdomain_name, self.service_type)
#     def __unicode__(self):
#         return self.service_type

# class OfferedService(models.Model):
#     service_type          =       models.CharField(max_length = 75, choices = SERVICE_TYPE)
#     service_chain        =       models.ManyToManyField("OfferedShippingChain")
#
#     def __unicode__(self):
#         return "%s" %(self.service_type)


class Direction(models.Model):
    origin                          =       models.CharField(max_length = 100, null=True, blank=True)
    destination                     =       models.CharField(max_length = 100, null=True, blank=True)
    #direction                       =       models.CharField(max_length = 20, choices = DIRECTION_TYPE, null=True, blank=True)

    class Meta():
        abstract = True

    def __unicode__(self):
        return "%s - %s" %(self.origin, self.destination)#, self.direction)



class ShippingChain(Direction):
    #service                        =       models.ForeignKey("Service", null=True, blank=True)
    subscriber                      =       models.ForeignKey('Subscriber', null=True, blank=True)

    origin_warehouse                =       models.ForeignKey("WarehouseMember", related_name = "origin_warehouse", null = True, blank=True)
    destination_warehouse           =       models.ForeignKey("WarehouseMember", related_name = "destination_warehouse", null = True, blank=True)

    shipper                         =       models.ForeignKey("ShippingMember", related_name = "origin_shipper", null = True, blank=True)
    #destination_shipper            =       models.ForeignKey("ShippingMember", related_name = "destination_shipper", null = True, blank=True)

    origin_distributor              =       models.ForeignKey("LocalDistributionMember", related_name="origin_distributor", null = True, blank=True)
    destination_distributor         =       models.ForeignKey("LocalDistributionMember", related_name="destination_distributor", null = True, blank=True)

    clearing_agent                  =       models.ForeignKey("CustomClearingAgent", related_name = "origin_clearing_agent", null = True, blank=True)
    #destination_clearing_agent     =       models.ForeignKey("CustomClearingAgent", related_name = "destination_clearing_agent", null = True, blank=True)

    complete                        =       models.BooleanField(default = False)

    air                             =       models.BooleanField(default = False)
    air_delivery_time               =       models.CharField(max_length = 50, null=True, blank=True)
    sea                             =       models.BooleanField(default = False)
    sea_delivery_time               =       models.CharField(max_length = 50, null=True, blank=True)
    ground                          =       models.BooleanField(default = False)
    ground_delivery_time            =       models.CharField(max_length = 50, null=True, blank=True)
    express                         =       models.BooleanField(default = False)
    express_delivery_time           =       models.CharField(max_length = 50, null=True, blank=True)


    #def description(self):
    #    return "%s - %s" %(self.origin, self.destination)

    # def direction_val(self):
    #     if self.direction == "import_export":
    #         return "Import & Export"
    #     return self.direction

    def routes_list(self):
        direction_list = [{'origin': self.origin, 'destination': self.destination,
                               #'direction': self.direction.split('_')[0],
                               'my_active_warehouse': self.origin_warehouse,
                               'my_active_shipping_member': self.origin_shipper, 'my_active_clearing_agent': self.origin_clearing_agent,
                               }]
        # direction_list = []
        # if self.direction in ["import", "export", "import_export"]:
        #     direction_list.append({'origin': self.origin, 'destination': self.destination,
        #                            'direction': self.direction.split('_')[0],
        #                            'my_active_warehouse': self.import_warehouse,
        #                            'my_active_shipping_member': self.import_shipper, 'my_active_clearing_agent': self.import_clearing_agent,
        #                            })
        #
        # if self.direction == "import_export":
        #     direction_list.append({'origin': self.destination, 'destination': self.origin,
        #                            'direction': 'export',
        #                            'my_active_warehouse': self.export_warehouse,
        #                            'my_active_shipping_member': self.export_shipper, 'my_active_clearing_agent': self.export_clearing_agent})

        return direction_list

    def get_pkgs_in_chain(self):
        return self.shippingpackage_set.all()

    def get_pkgs_in_chain_processed(self):
        return self.shippingpackage_set.filter(Q(deleted=False), prepared_for_shipping=True)

    def get_pkgs_processed(self):
        return self.shippingpackage_set.filter(Q(deleted=False), prepared_for_shipping=True).count()

    def get_pkg_processed_by_sub_air_exp(self):
        return self.shippingpackage_set.filter(Q(origin_warehouse__offered_by=self.subscriber), Q(deleted=False), (Q(shipping_method="Air Freight") | Q(shipping_method="Express Air")), Q(prepared_for_shipping=True)).count()

    def get_pkg_processed_by_sub_sea(self):
        return self.shippingpackage_set.filter(Q(origin_warehouse__offered_by=self.subscriber), Q(deleted=False), Q(shipping_method="Sea Freight"), Q(prepared_for_shipping=True)).count()

    def get_pkg_processed_by_sub_revoked(self):
        return self.shippingpackage_set.filter(Q(origin_warehouse__offered_by=self.subscriber), Q(deleted=True), Q(prepared_for_shipping=True)).count()

    def get_pkg_processed_for_sub(self):
        return self.shippingpackage_set.filter(~Q(origin_warehouse__offered_by=self.subscriber), Q(prepared_for_shipping=True)).count()

    def get_pkg_total_val_processed_by_sub_air_exp(self):
        return self.shippingpackage_set.filter(Q(origin_warehouse__offered_by=self.subscriber), Q(deleted=False), (Q(shipping_method="Air Freight") | Q(shipping_method="Express Air")), Q(prepared_for_shipping=True)).aggregate(Sum('admin_total_payable_D'))['admin_total_payable_D__sum']

    def get_pkg_total_val_processed_by_sub_sea(self):
        return self.shippingpackage_set.filter(Q(origin_warehouse__offered_by=self.subscriber), Q(deleted=False), Q(shipping_method="Sea Freight"), Q(prepared_for_shipping=True)).aggregate(Sum('admin_total_payable_D'))['admin_total_payable_D__sum']

    def get_pkg_total_val_processed_for_sub(self):
        return self.shippingpackage_set.filter(~Q(origin_warehouse__offered_by=self.subscriber), Q(prepared_for_shipping=True)).aggregate(Sum('admin_total_payable_D'))['admin_total_payable_D__sum']

    def get_total_val_of_local_delivery_in_route(self):
        return self.get_pkgs_in_chain_processed().aggregate(Sum('local_freight_D'))['local_freight_D__sum']

    def get_pkgs_in_chain_unprocessed(self):
        return self.shippingpackage_set.filter(prepared_for_shipping=False)

    def get_pkgs_in_chain_total_amount_payable(self):
        return self.shippingpackage_set.aggregate(Sum('admin_total_payable_D'))['admin_total_payable_D__sum']

    def get_pkgs_in_chain_total_amount_paid(self):
        return self.shippingpackage_set.aggregate(Sum('balance_paid_D'))['balance_paid_D__sum']

    def get_pkgs_in_chain_total_balance(self):
        return self.shippingpackage_set.aggregate(Sum('balance_D'))['balance_D__sum']

    def get_pkgs_in_chain_processing_fee(self):
        return self.shippingpackage_set.aggregate(Sum('intl_freight_D'))['intl_freight_D__sum']

    def get_gross_income(self):
        try:
            total_amount_payable = self.get_pkgs_in_chain_total_amount_payable()
            total_processing_fee = self.get_pkgs_in_chain_processing_fee()
            return total_amount_payable - total_processing_fee
        except:
            return 0.00

    # def get_shipping_chain_distributors(self):
    #     origin_import_distributor           = self.origin_import_distributor.all()
    #     origin_export_distributor           = self.origin_export_distributor.all()
    #     destination_import_distributor      = self.destination_import_distributor.all()
    #     destination_export_distributor      = self.destination_export_distributor.all()
    #
    #     return origin_import_distributor, origin_export_distributor, destination_import_distributor, destination_export_distributor
    def get_shipping_chain_distributors(self):
        origin_distributor                  = self.origin_distributor
        destination_distributor             = self.destination_distributor

        return origin_distributor, destination_distributor

    def get_fixed_weights(self):
        return self.fixedshipment_set.all()

    
    def get_pkgs_weight(self):
        weight_list=[]
        for pkg in self.shippingpackage_set.all():
            weight_list.append(pkg.box_weight_higher())
        return sum(weight_list)


    def get_route_code_from_country_names(self):
        route_name = self.origin + "-" + self.destination
        value = route_name.split('-')
        code = []
        for i in value:
            val = i.strip()
            get_code = Country.objects.get(name=val)
            code.append(str(get_code.code3))
        return code[0] + "-" + code[1]

    def get_shipping_rates(self):
        return self.shippingrate_set.all()        


class ShippingRate(models.Model):
    shipping_chain               = models.ForeignKey(ShippingChain, verbose_name="Delivery Route")

    #direction                   = models.CharField(max_length = 10, choices = ShippingMethod[:3], default='Air')
    shipping_method             = models.CharField(max_length = 30, choices = ShippingMethod[:3])

    weight_unit                 = models.CharField(max_length = 5, default="lbs")#, choices = WEIGHT_UNIT)
    from_range                  = models.FloatField(verbose_name="From Weight", default = 1.0)
    to_range                    = models.FloatField(verbose_name="To Weight", default = 1.0)
    rate_D                      = models.FloatField(verbose_name="Rate ($/lbs)", default = 1)

    def __unicode__(self):
        return "%s: %s - %s: %s, %s" %(self.shipping_chain, self.from_range, self.to_range, self.rate_D, self.shipping_chain.subscriber)

# class OfferedShippingChain(BaseShippingChain):
#     offered_warehouse               =       models.ManyToManyField("WarehouseMember", related_name = "offered_warehouse", blank=True)
#     offered_clearing_agent          =       models.ManyToManyField("CustomClearingAgent", related_name = "offered_clearing_agent", blank=True)
#     offered_shipping_member         =       models.ManyToManyField("ShippingMember", related_name = "offered_shipping_member", blank=True)
#     available_local_distributor     =       models.ManyToManyField("LocalDistributionMember", related_name="available_local_distributor", blank=True)
#
#     def mm_offered_warehouse(self, marketing_member):
#         return self.offered_warehouse.get(offered_by = marketing_member)
#
#     def mm_offered_clearing_agent(self, marketing_member):
#         return self.offered_clearing_agent.get(offered_by = marketing_member)
#
#     def mm_offered_shipping_member(self, marketing_member):
#         return self.offered_shipping_member.get(offered_by = marketing_member)
#
#     def offered_warehouses(self, country):
#         return self.offered_warehouse.filter(country = country)
#
#     def offered_clearing_agents(self, country):
#         return self.offered_clearing_agent.filter(country = country)
#
#     def offered_shipping_members(self, country):
#         return self.offered_shipping_member.filter(country = country)
#
#     def available_distributors(self, country):
#         return self.available_local_distributor.filter(localdistributorlocation__country = country).distinct()


class BaseWarehouseInfo(models.Model):
    #shipping_chain                  = models.ForeignKey(ShippingChain, null=True, blank=True)

    process_charge_per_kg           = models.FloatField(max_length = 10, default=0) #USD
    storage_charge_per_day          = models.FloatField(max_length = 10, default=0) #USD
    working_hrs_start               = models.CharField(max_length = 5)
    working_hrs_end                 = models.CharField(max_length = 5)
    auto_subscriber_approval        = models.BooleanField(default = False)
    publish_reviews                 = models.BooleanField(default = False)
    about_service                   = models.TextField()

    offered_for_rent                = models.BooleanField(default = True)
    #offered_by                     = models.ForeignKey(MarketingMember, null=True, blank=True)
    offered_by                      = models.OneToOneField(Subscriber, null=True, blank=True)
    activated_for_offerer           = models.BooleanField(default = True)
    active                          = models.BooleanField(default = True)

    created_on                      = models.DateTimeField(default = timezone.now)

    class Meta:
        abstract = True





class WarehouseMember(BaseImportantInfo, BaseWarehouseInfo):

    warehouse_size                  = models.CharField(max_length = 10)
    country                         = models.CharField(max_length = 100, null=True, blank=True)
    company_name                    = models.CharField(max_length = 50)
    company_name_slug               = models.SlugField(editable = False)
    logo                            = models.ImageField(upload_to = "warehouse-member/Logo", null=True, blank=True)

    #suite_no_prefix                 = models.CharField(max_length = 10)

    # address                         =       models.TextField(null=True)
    # city                            =       models.CharField(max_length=50, null=True)
    # state                           =       models.CharField(max_length=50, null=True)
    # telephone                       =       models.CharField(max_length=50, null=True)
    # country                         =       models.CharField(max_length = 10, choices = COUNTRY, default = "us")

    #drop_off_location               =       models.ManyToManyField(DropOffLocation)



    # warehouse_size                  = models.CharField(max_length = 10)
    # process_charge_per_kg           = models.FloatField(max_length = 10, default=0) #USD
    # storage_charge_per_day          = models.FloatField(max_length = 10, default=0) #USD
    # working_hrs_start               = models.CharField(max_length = 5)
    # working_hrs_end                 = models.CharField(max_length = 5)
    # auto_subscriber_approval         = models.BooleanField(default = False)
    # publish_reviews                 = models.BooleanField(default = False)
    # about_service                   = models.TextField()
    #
    # offered_for_rent                = models.BooleanField(default = False)

    class Meta:
        ordering = ["-registration_time"]
        verbose_name_plural = "Warehouse Member"


    # def save(self, *args, **kwargs):
    #     self.company_name_slug = slugify(self.company_name)
    #     super(WarehouseMember, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.company_name)

    def full_address(self):
        delivery_address = "%s %s, %s, %s, %s, %s" %(self.address1, self.address2, self.suite_no_prefix, self.city, self.state, self.country)        #print delivery_address
        return delivery_address
    
    def get_all_warehouses(self):
        return self.warehouselocation_set.all()

# class WarehouseMember(BaseWarehouse):
#
#     class Meta:
#         ordering = ["-registration_time"]
#         verbose_name_plural = "Warehouse Member"
#
# class OfferedWarehouse(BaseWarehouse):
#
#     class Meta:
#         ordering = ["-registration_time"]
#         verbose_name_plural = "Offered Member"


class WarehouseLocation(BaseAddressInfo):
    owned_by = models.ForeignKey(WarehouseMember)
    location_prefix  = models.CharField(max_length = 10)
    
    def __unicode__(self):
        return "%s" %(self.name)

    def full_address(self):
        delivery_address = "%s %s, %s, %s, %s, %s" %(self.address1, self.address2, self.city, self.state, self.country, self.location_prefix)        #print delivery_address
        return delivery_address


class ShippingMember(BaseImportantInfo, BaseWarehouseInfo, BaseAddressInfo):
    #name     =    models.CharField(max_length = 75)


    def __unicode__(self):
        return "%s" %self.name
    
    
    def get_all_locations(self):
        return self.shippingmemberroute_set.all()
    
    
class ShippingMemberRoute(models.Model):
    origin      = models.CharField(max_length = 50)
    destination = models.CharField(max_length = 50)
    rate        = models.FloatField(max_length = 10, default = 0)
    shipping_method = models.CharField(max_length=20, default="Air Freight", choices=SHIPPING_METHOD)
    shipper     = models.ForeignKey(ShippingMember)
    
    def __unicode__(self):
        return "%s ---> %s:  $%s/lb" %(self.origin, self.destination, self.rate)


class CustomClearingAgent(BaseImportantInfo, BaseWarehouseInfo, BaseAddressInfo):
    clearing_per_kg             = models.FloatField(max_length = 10, default=0)
    quote_per_cosignment        = models.BooleanField(default = False)
    #storage_per_pound_per_day   = models.FloatField(max_length = 10, default=0)
    # working_hrs_start           = models.CharField(max_length = 5)
    # working_hrs_end             = models.CharField(max_length = 5)
    # auto_subscriber_approval     = models.BooleanField(default = False)
    # publish_reviews             = models.BooleanField(default = False)
    # about_service               = models.TextField()
    #
    # activated_for_offerer           = models.BooleanField(default = True)
    # offered_by                      = models.ForeignKey(MarketingMember, null=True, blank=True)
    # offered_for_rent                = models.BooleanField(default = True)
    #
    # active                          = models.BooleanField(default = True)
    # created_on                      = models.DateTimeField(default = timezone.now)

    class Meta:
        verbose_name_plural = "Custom Clearing Agent"
        
    def __unicode__(self):
        return "%s" %self.name
    
    
    def get_all_locations(self):
        return self.clearingprice_set.all()
    
    
class ClearingPrice(models.Model):
    country          = models.CharField(max_length = 50)
    price            = models.FloatField(max_length = 10, default = 0)
    clearing_agent   = models.ForeignKey(CustomClearingAgent)
    
    def __unicode__(self):
        return "%s:- $%s per kg" %(self.country, self.price)

'''Services Marketplace'''


'''Sokohali Config'''

class AvailableCountry(models.Model):
    name                 =     models.CharField(max_length = 100, null = True)
    currency             =     models.CharField(max_length = 20, choices=CURRENCY)
    dollar_exchange_rate =     models.FloatField(default = 200)
    payment_options      =     models.ManyToManyField('ConfiguredPayment', blank=True)

    def __unicode__(self):
        return '%s - %s' %(self.name, self.dollar_exchange_rate)



class ConfiguredPayment(models.Model):
    name                =     models.CharField(max_length = 100, null = True)
    log                 =     models.ImageField(upload_to = 'configured_payments/%d/%m/%y/')

    def __unicode__(self):
        return self.name



class LocalDistributionMember(models.Model):
    courier_name        =  models.CharField(max_length = 50, null = True)
    country             =  models.ForeignKey(AvailableCountry, null=True, blank=True)
    active              =  models.BooleanField(default = False)
    has_api             =  models.BooleanField(default = False)
    has_configured_rates=  models.BooleanField(default = False)

    '''if marketing_member, instance is a postal center'''
    marketing_member    = models.ForeignKey(MarketingMember, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.courier_name)



class LocalDistributorRegion(models.Model):
    name                =     models.CharField(max_length = 100, null = True, blank=True)
    courier             =     models.ForeignKey(LocalDistributionMember, blank=True, null=True)

    def __unicode__(self):
        return "%s %s " %(self.name, self.courier)



class LocalDistributorPrice(models.Model):
    weight_unit         =     models.CharField(max_length = 5, choices = WEIGHT_UNIT)
    weight              =     models.FloatField(default = 1)
    price               =     models.FloatField(default = 1)
    region              =     models.ForeignKey(LocalDistributorRegion, blank=True, null=True)
    mark_up_value       =     models.FloatField(default=30)
    
    class Meta:
        ordering = ['-weight']

    def __unicode__(self):
        return "%s%s - %s | %s" %(self.weight, self.weight_unit, self.price, self.region)

    def weight_info(self):
        return "%s%s" %(self.weight, self.weight_unit)



class LocalDistributorLocation(BaseAddressInfo):
    #courier             =     models.CharField(max_length = 30, null = True)
    #courier             =     models.ForeignKey(LocalDistributionMember, blank=True, null=True)

    region              =      models.ForeignKey(LocalDistributorRegion, blank=True, null=True)

    # '''if marketing_member, instance is a postal center'''
    # marketing_member    = models.ForeignKey(MarketingMember, null=True, blank=True)
    pickup_available    =     models.BooleanField(default = False)
    drop_off_available  =     models.BooleanField(default = False)

    offered_location    =     models.BooleanField(default = False)

    def __unicode__(self):
        return self.full_address()

    def brief_info(self):
        return "%s, %s" %(self.city, self.state)

    def full_address(self):
        return "%s, %s %s %s, %s, %s." %(self.address1, self.address2, self.city, self.state, self.country, self.phone_number)

    def drop_off_code(self):
        return "%s - %s" %(self.state[:4], self.id)

'''Sokohali Config'''

class FixedShipment(models.Model):
    description           =  models.CharField(max_length = 500, null=True, blank=True)
    unit_price_D          =  models.FloatField(default = 0)
    extra_charges         =  models.FloatField(default = 0)
    chain                 =  models.ForeignKey(ShippingChain, null=True,blank=True)
    subscriber            =  models.ForeignKey(Subscriber, null=True, blank=True)

    def __unicode__(self):
        return '%s-%s' %(self.description, self.unit_price_D)


class BankAccount(models.Model):
    marketing_member =       models.ForeignKey(MarketingMember, blank=True, null=True)
    account_name     =       models.CharField(max_length = 50)
    account_no       =       models.CharField(max_length = 50)
    bank             =       models.CharField(max_length = 50)
    address          =       models.CharField(max_length = 300, null=True, blank=True)
    currency         =       models.CharField(max_length = 50, choices=BANK_CURRENCY)
    routing_no       =       models.CharField(max_length = 50, null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" %(self.account_name, self.account_no)
    
    
class OfferedServiceRate(models.Model):
    service_name        = models.CharField(max_length = 50, choices = OFFERED_SERVICES)
    charge              = models.FloatField(default = 0)
    extra_charges       = models.FloatField(default = 0, null=True, blank=True)
    extra_charges_info  = models.CharField(max_length= 250, null = True, blank=True)
    unit                = models.CharField(max_length = 50, choices= WEIGHT_UNIT)
    offered_by          = models.ForeignKey(Subscriber, related_name="offered_by")
    rented_by           = models.ForeignKey(Subscriber, related_name = "rented_by")
    chain               = models.ForeignKey(ShippingChain, null=True, blank=True)
    
    
    def __unicode__(self):
        return self.service_name


class Pricing(models.Model):
    description         = models.CharField(max_length= 250, null = True, blank=True)
    price_range         = models.FloatField(default = 0)
    marketer            = models.ForeignKey(MarketingMember, null=True, blank=True)
    image               = models.ImageField(upload_to = "image-of-box/%Y/%m/%d", null=True, blank=True)
    currency            = models.CharField(max_length = 50, choices=BANK_CURRENCY)
    dimensions          = models.CharField(max_length= 150, null = True, blank=True)

    def __unicode__(self):
        return self.description


class TariffZone(models.Model):
    from_city           = models.CharField(max_length=100, null=True, blank=True)
    to_city             = models.CharField(max_length=100, null=True, blank=True)
    from_state          = models.CharField(max_length=100, null=True, blank=True)
    to_state            = models.CharField(max_length=100, null=True, blank=True)
    country             = models.CharField(max_length=100, null=True, blank=True)
    region              = models.ForeignKey(LocalDistributorRegion, null=True, blank=True)
    
    
    def __unicode__(self):
        return "%s - %s" %(self.from_city, self.to_city) 
    
