from django.contrib import admin
from models import SokoPay, SubscriberPayment, MarketerPayment
# Register your models here.

class SokoPayAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'ref_no', 'teller_no', 'status', 'purchase_type_1', 'purchase_type_2', 'payment_gateway_tranx_id', 'message',)
    list_filter = ('purchase_type_1', 'purchase_type_2', )
    search_fields = ('ref_no', 'user__username', 'user__email',)

admin.site.register(SokoPay, SokoPayAdmin)
admin.site.register(SubscriberPayment)
admin.site.register(MarketerPayment)
