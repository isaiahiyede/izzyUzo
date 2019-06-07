from django.contrib import admin
from models import *



# Register your models here.


class UserAccountAdmin(admin.ModelAdmin):
    search_fields = ['user__email']
    list_filter = ('marketer',)

admin.site.register(UserAccount, UserAccountAdmin)

class UserSpecialRateAdmin(admin.ModelAdmin):
    list_display = ('user', 'origin', 'destination', 'freight_type', 'rate_per_lb_D',)

admin.site.register(UserSpecialRate, UserSpecialRateAdmin)
admin.site.register(JoinWaitingList)
admin.site.register(MessageCenterComment)
admin.site.register(ActionHistory)




class SecurityQuestionAdmin(admin.ModelAdmin):
	list_display = ('user','question','answer','created',)

admin.site.register(SecurityQuestion, SecurityQuestionAdmin)



