from django import template
from general.custom_functions import marketingmember_costcalc#costcalc_settings
from django.db.models import Q, Sum
from datetime import date
from sokopay.models import SubscriberPayment

register = template.Library()

# @register.simple_tag
# def dollarNairaRate():
#     return costcalc_settings().dollar_naira_rate

@register.simple_tag
def dollar_exchange_rate(request):
    costcalc = marketingmember_costcalc(request)
    return costcalc.dollar_exchange_rate


@register.simple_tag
def current_year():
    return date.today().year



@register.simple_tag
def multiply(rate, weight, unit):
    if unit == "lbs":
        #print "lbs",round((rate*weight),2)
        return round((rate*weight),2)
    else:
        #print "kg",round((rate*weight*0.45359),2)
        return round((rate*weight*0.45359),2)
    
@register.simple_tag
def amt_paid(chain, service, owner):
    if service == 'Origin-warehouse':
        service = 'ORIGIN WAREHOUSE'
    elif service == 'Destination-warehouse':
        service = 'DESTINATION WAREHOUSE'
    else:
        service = service
    payments = SubscriberPayment.objects.get_paid_rented_service(chain, service, owner).aggregate(Sum('amount'))
    if payments['amount__sum'] == None:
        amt_paid = 0
    else:
        amt_paid = payments['amount__sum']
    return amt_paid


@register.simple_tag
def amt_due(rate, weight, unit, chain,service,owner):
    amt_due = multiply(rate, weight, unit) - amt_paid(chain, service, owner)
    return amt_due