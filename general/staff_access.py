from django.contrib.auth.models import User
from general.models import UserAccount
from general.custom_functions import marketing_member

def staff_check(request):
    if request.user.is_staff:
        try:
            return marketing_member(request) == request.user.useraccount.marketer
        except:
            return True
    return False

def superuser_check(user):
    return user.is_superuser

def limited_access_check(user):
    return user.useraccount.limited_access or user.is_superuser

def oms_access(user):
    try:
        return user.useraccount.oms_access or user.useraccount.fulfilment_company.ordermanager or user.is_superuser
    except:
        return user.useraccount.oms_access or  user.is_superuser

def cm_access_check(user):
    return user.useraccount.cm_access or user.is_superuser

def cm_authorization_check(user):
    return user.useraccount.cm_authorization or user.is_superuser

def batchmanager_check(user):
    try:
        return user.useraccount.batchmanager or user.useraccount.fulfilment_company.shipmentmanager or user.is_superuser
    except:
        return user.useraccount.batchmanager or user.is_superuser

def creditmanager_check(user):
    return user.useraccount.cm_access#creditmanager

def messagecenter_check(user):
    return user.useraccount.messagecenter

def shipmentmanager_check(user):
    try:
        return user.useraccount.shipmentmanager or user.useraccount.fulfilment_company.shipmentmanager or user.is_superuser
    except:
        return user.useraccount.shipmentmanager or user.is_superuser

def usermanager_check(user):
    try:
        return user.useraccount.usermanager or user.useraccount.fulfilment_company.shipmentmanager or user.is_superuser
    except:
        return user.useraccount.usermanager or user.is_superuser

def feedback_check(user):
    return user.useraccount.feedback

def fulfilment_company(user):
    return user.useraccount.is_fulfilment

def staff_check_for_booking(user):
    if not user.is_staff:
        return True
    else:
        return False

def check_zeAc_auth_user(user):
    if not user.is_authenticated():
        return False
    else:
        return True

def address_activated(user):
    if user.is_authenticated():
        return user.useraccount.address_activation
    return False

def address_activated_new(user):
    if user.is_authenticated():
        if user.useraccount.address_activation == True:
            return True
        else:
            return False
    return False

def fedex_check(user):
    return user.useraccount.is_fedex

def flagged_check(user):
    if not user.useraccount.flagged:
        return True
    else:
        return False

def invited_to_zpn(user):
    return user.useraccount.is_invited_to_zpn
