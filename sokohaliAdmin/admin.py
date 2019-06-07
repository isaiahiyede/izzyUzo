from django.contrib import admin
from models import CostCalcSettings, NewFedExLocalFreightSettings,ShippingKeyword,PreDefinedBoxes, Batch, BatchEditHistory, ExportObjCostCalcSettings, AirwayBill, BatchPromo, NotifyUser, Trucking

# Register your models here.


class CostCalcSettingsAdmin(admin.ModelAdmin):
	list_display = ('dollar_exchange_rate', 'marketer', 'country')

admin.site.register(CostCalcSettings, CostCalcSettingsAdmin)
admin.site.register(NewFedExLocalFreightSettings)
admin.site.register(ShippingKeyword)
admin.site.register(PreDefinedBoxes)
admin.site.register(ExportObjCostCalcSettings)
admin.site.register(Batch)
admin.site.register(BatchEditHistory)
admin.site.register(AirwayBill)
admin.site.register(BatchPromo)
admin.site.register(NotifyUser)
admin.site.register(Trucking)


