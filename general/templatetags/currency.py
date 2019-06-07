# -*- coding: utf-8 -*-
import random
from django import template
import pycountry
import moneyed
from cities_light.models import *
from general.modelfield_choices import COUNTRIES
from general.custom_functions import costcalc_settings
from forex_python.converter import CurrencyCodes

register = template.Library()

@register.simple_tag
def country_currency_v1(country):
    if country == COUNTRIES[0]:
        return "$"
    elif country == COUNTRIES[1]:
        return "£"
    elif country == COUNTRIES[2]:
        return "¥"


@register.simple_tag
def country_currency_v2(country):

    if country == COUNTRIES[0]:
        return "US Dollar"
    elif country == COUNTRIES[1]:
        return "UK Pound"
    elif country == COUNTRIES[2]:
        return "Chinese Yen"


@register.simple_tag
def country_currency_code(lb_country):
    country_name = lb_country.strip()
    for currency, data in moneyed.CURRENCIES.iteritems():
        if country_name.upper() in data.countries:
            symb = CurrencyCodes()
            symbol = symb.get_symbol(str(currency))
            new_symbol = symbol
            if new_symbol == "None":
                return currency
            else:
                return symbol


@register.simple_tag
def shipping_rate():
    return costcalc_settings().flat_cost_air_freight
