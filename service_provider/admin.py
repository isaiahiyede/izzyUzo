from django.contrib import admin
from models import *


admin.site.register(Subscriber)

class ServiceAdminBase(admin.ModelAdmin):
    list_display = ('name', 'country',)
    list_filter = ('country', )


class MarketingMemberAdmin(admin.ModelAdmin):
    list_display = ('storefront_name', 'active')


class ShippingChainAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'subscriber')

    def subscriber(self,obj):
        return obj.subscriber.name
    subscriber.admin_order_field = 'subscriber__name'


admin.site.register(MarketingMember, MarketingMemberAdmin)

#admin.site.register(PostalCenter, ServiceAdminBase)
#admin.site.register(Service)
admin.site.register(ShippingChain, ShippingChainAdmin)

class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('shipping_chain', 'shipping_method','from_range', 'to_range', 'rate_D','subscriber')

    def subscriber(self,obj):
        return obj.shipping_chain.subscriber
    subscriber.admin_order_field = 'subscriber__name'

admin.site.register(ShippingRate, ShippingRateAdmin)
#admin.site.register(OfferedServiceChain)

class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state','country')
    list_filter = ('state', 'country',)
 
    
class WarehouseMemberAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'offered_by')
    

admin.site.register(WarehouseLocation, WarehouseLocationAdmin)
admin.site.register(WarehouseMember, WarehouseMemberAdmin)
admin.site.register(ShippingMember, ServiceAdminBase)
admin.site.register(ShippingMemberRoute)
admin.site.register(ClearingPrice)
admin.site.register(Pricing)
admin.site.register(TariffZone)


class LocalDistributorLocationAdmin(admin.ModelAdmin):
    list_display = ('region', 'country', 'state', 'city', 'drop_off_available')
    list_filter = ('state', 'country',)

admin.site.register(LocalDistributorLocation, LocalDistributorLocationAdmin)

admin.site.register(CustomClearingAgent, ServiceAdminBase)

admin.site.register(AvailableCountry)
admin.site.register(ConfiguredPayment)

class LocalDistributionMemberAdmin(admin.ModelAdmin):
    list_display = ('courier_name', 'country', 'active', 'has_api', 'has_configured_rates',)
    list_filter  = ('courier_name', 'country', 'active', 'has_api', 'has_configured_rates',)

admin.site.register(LocalDistributionMember, LocalDistributionMemberAdmin)

admin.site.register(LocalDistributorRegion)

class LocalDistributorPriceAdmin(admin.ModelAdmin):
    #list_display = ('weight', 'weight_unit', 'price', 'region',)
    list_filter = ('region',)

admin.site.register(LocalDistributorPrice, LocalDistributorPriceAdmin)

admin.site.register(BankAccount)



class FixedShipmentAdmin(admin.ModelAdmin):
    list_display = ('description','unit_price_D','chain','subscriber',)

    def chain(self,obj):
        return "%s - %s" %(obj.chain.origin, obj.chain.destination)
    chain.admin_order_field = 'chain__origin' + "-" + 'chain__destination'

    def subscriber(self,obj):
        return obj.subscriber.name
    subscriber.admin_order_field = 'subscriber__name'

admin.site.register(FixedShipment,FixedShipmentAdmin)

class OfferedServiceRateAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'offered_by', 'rented_by')
    
    
admin.site.register(OfferedServiceRate, OfferedServiceRateAdmin)
