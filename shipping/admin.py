from django.contrib import admin
from models import DeliveryAddress, ShippingItem, ShippingPackage,PickupLocation, ShippingPackageInvoice, CourierLabel, DropOffPostOffice, DockReceipt, DomesticPackage


class ShippingPackageAdmin(admin.ModelAdmin):
	list_display = ['tracking_number', 'ordered', 'local_freight_D', 'intl_freight_D', 'admin_total_payable_D', 'admin_total_payable_N']
# Register your models here.

class AddressAdmin(admin.ModelAdmin):
	list_display = ['user', 'address_line1', 'address_line2', 'city', 'state', 'country', 'zip_code']

admin.site.register(DeliveryAddress)
admin.site.register(ShippingItem)
admin.site.register(ShippingPackage, ShippingPackageAdmin)
admin.site.register(PickupLocation, AddressAdmin)
admin.site.register(DropOffPostOffice, AddressAdmin)
admin.site.register(ShippingPackageInvoice)
admin.site.register(CourierLabel)
admin.site.register(DockReceipt)
admin.site.register(DomesticPackage)