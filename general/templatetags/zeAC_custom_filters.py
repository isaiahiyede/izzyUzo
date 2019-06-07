from django import template
from django.template.defaultfilters import stringfilter
from general.custom_functions import marketing_member
from datetime import date, timedelta
from general.models import *
import datetime
import time
import pytz
from django.db.models import Q, Sum
from itertools import chain
from operator import attrgetter


register = template.Library()


@register.simple_tag
def get_user_cart_items_count(request):
	if request.user.is_anonymous:
		return 0
	else:
		get_cart_items_count = Cart.objects.filter(client=request.user,ordered=False).count()
		if (get_cart_items_count == None):
			return 0
		else:
			return get_cart_items_count



@register.simple_tag
def get_user_total_unordered_cart_items_value(request):
	if request.user.is_anonymous:
		return 0
	else:
		get_cart_items_count_sum = Cart.objects.filter(client=request.user,ordered=False).aggregate(Sum('quantity'))
		if (get_cart_items_count_sum == None):
			return 0.0
		else:
			return get_cart_items_count_sum
