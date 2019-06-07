import os
from xml.etree import ElementTree as ET
import requests
from django.http import JsonResponse
from django.shortcuts import render_to_response, render, redirect
from django.core.urlresolvers import reverse
#from export.ExportPackageCalculator import ExportPackageCostCalc
from general.custom_functions import marketingmember_costcalc, get_local_freight_from_state, get_marketing_member_shipping_rate, \
                                    has_special_rate_for_route
import base64
from django.contrib import messages
from django.utils import timezone
from general.image_helpers import convert_base64_to_image
from service_provider.models import WarehouseLocation

def state_code_abbreviation(state, country):
    if country == 'United States':
        from localflavor.us.us_states import CONTIGUOUS_STATES
        for state_list in CONTIGUOUS_STATES:
            cs_abb, cs_state = state_list
            if cs_state == state:
                return cs_abb


def get_url(request, action):
    rp = request.POST
    print rp
    url = "http://production.shippingapis.com/ShippingApi.dll?API="
    xml = ""
    USERID          = "250CIRCU3854" #"593CIRCU5990"
    # USERID2         = "20194120"
    item_container  = 'Rectangular'

    if rp['destination_country'].lower() == "united states":
        mail_type       = 'Letter' #Letter/Package
    else:
        mail_type = 'Package'
    size            = 'Large' #Regular/Large
    originZipCode   = '20706' #Maryland Zip Code
    destZipCode     = rp["destZipCode"]
    #destZipCode     = '20785'
    request.session['pkg_weight_lbs'] = float(rp['weight_lbs'])
    request.session['naira_value']    = float(rp['naira_value'])
    if action == "ShippingEstimate":
        API_name = ""
        request_type = ""
        zipdestination = ""
        if rp['destination_country'].lower() == "usa" or rp['destination_country'].lower() == "united states":
            API_name = "RateV4"
            request_type = "RateV4Request"
            zipdestination = "<ZipDestination>" + destZipCode + "</ZipDestination>"

            ounce_weight = float(rp['weight_lbs']) * 16
            #print 'ounce_weight: ',ounce_weight

            xml += API_name + '''&XML=<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
            <''' + request_type + ''' USERID="''' + USERID + '''">
            <Revision>2</Revision>
            <Package ID="0">
            <Service>''' + rp['usps_delivery_speed'] + '''</Service><FirstClassMailType>''' + mail_type + '''</FirstClassMailType>
            <ZipOrigination>''' + originZipCode + '''</ZipOrigination>''' + zipdestination + '''
            <Pounds> ''' + rp['weight_lbs'] + '''</Pounds>
            <Ounces>''' + str(ounce_weight) + '''</Ounces>
            <Container>''' + item_container + '''</Container>
            <Size>''' + size + '''</Size>
            <Width>''' + rp['box_width'] + '''</Width>
            <Length>''' + rp['box_length'] + '''</Length>
            <Height>''' + rp['box_height'] + '''</Height>
            <Value>''' + rp['value_of_content_D'] + '''</Value>
            <Machinable>True</Machinable>
            </Package>
            </''' + request_type + '''>'''
        else:
            API_name = "IntlRateV2"
            request_type = "IntlRateV2Request"
            zipdestination = ""

            ounce_weight = float(rp['weight_lbs']) * 16
            xml += API_name + '''&XML=<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
            <''' + request_type + ''' USERID="''' + USERID + '''">
            <Revision>2</Revision>
            <Package ID="0">
            <Pounds> ''' + rp['weight_lbs'] + '''</Pounds>
            <Ounces>''' + str(ounce_weight) + '''</Ounces>
            <Machinable>True</Machinable>
            <MailType>''' + mail_type + '''</MailType>
            <ValueOfContents>''' + rp['value_of_content_D'] + '''</ValueOfContents>
            <Country>''' + rp['destination_country'] + '''</Country>
            <Container>''' + item_container + '''</Container>
            <Size>''' + size + '''</Size>
            <Width>''' + rp['box_width'] + '''</Width>
            <Length>''' + rp['box_length'] + '''</Length>
            <Height>''' + rp['box_height'] + '''</Height>
            <Girth>0</Girth>
            <OriginZip>''' + originZipCode + '''</OriginZip>
            <CommercialFlag>Y</CommercialFlag>
            <ExtraServices>
            <ExtraService>1</ExtraService>
            </ExtraServices>
            </Package>
            </''' + request_type + '''>'''
    elif action == "Tracking":
        xml = '''TrackV2&XML=<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
        <TrackFieldRequest USERID="''' + USERID + '''">
        <Revision>0</Revision>
        <TrackID ID="''' + rp['trackingID'] + '''"></TrackID></TrackFieldRequest>'''

    elif action == "address_verification":
        xml = '''Verify&XML=<?xml version='1.0' encoding="UTF-8" standalone='yes' ?>
        <AddressValidateRequest USERID="''' + USERID + '''">
        <Address>
        <Address1></Address1>
        <Address2>6406 Ivy Lane</Address2>
        <City>Greenbelt</City>
        <State>MD</State>
        <Zip5></Zip5>
        <Zip4></Zip4>
        </Address>
        </AddressValidateRequest>'''
    #print url + xml
    return url + xml






# def process_api_response(request, xml_response, action, delivery_speed):
#     #print xml_response
#     context = {}
#     context['got_response']   =   True
#     context['action']         =   action
#     try:
#         root = ET.fromstring(xml_response)
#     except:
#         return HttpResponse("Could not parse XML object")
#
#     if action == "ShippingEstimate":
#         print 'hereh'
#         try:
#             # International shipping
#             context["has_express_speed"]      =   True
#             context["has_normal_speed"]       =   True
#             context['destination']          =   root.findall(".//Service[@ID='1']/Country")[0].text
#
#             #  Normal delivery
#             if delivery_speed == "Priority Mail":
#                 try:
#                     context['normal_postage']       =   root.findall(".//Service[@ID='2']/Postage")[0].text
#                     context['normal_commercial']    =   root.findall(".//Service[@ID='2']/CommercialPostage")[0].text
#                     context['normal_duration']      =   root.findall(".//Service[@ID='2']/SvcCommitments")[0].text
#                     context['normal_desc']          =   root.findall(".//Service[@ID='2']/SvcDescription")[0].text.split('&')[0]
#                 except:
#                     context["has_normal_speed"]  =  False
#             if delivery_speed == "Priority Mail Express":
#                 # Express delivery
#                 try:
#                     context['express_postage']      =   root.findall(".//Service[@ID='1']/Postage")[0].text
#                     context['express_commercial']   =   root.findall(".//Service[@ID='1']/CommercialPostage")[0].text
#                     context['express_duration']     =   root.findall(".//Service[@ID='1']/SvcCommitments")[0].text
#                     context['express_desc']         =   root.findall(".//Service[@ID='1']/SvcDescription")[0].text.split('&')[0]
#                 except:
#                     context["has_express_speed"]    =   False
#
#         except Exception as e:
#             #print 'exception: ',e
#             #  Domestic shipping
#             try:
#                 context['domestic_description']        =   root.findall(".//Postage[@CLASSID='1']/MailService")[0].text.split('&')[0]
#                 context['domestic_shipping_charge']    =   root.findall(".//Postage[@CLASSID='1']/Rate")[0].text
#             except:
#                 context['domestic_description']        =   root.findall(".//Postage[@CLASSID='3']/MailService")[0].text.split('&')[0]
#                 context['domestic_shipping_charge']    =   root.findall(".//Postage[@CLASSID='3']/Rate")[0].text
#             context['domestic_shipping']           =   True
#
#     print 'context 1: ',context
#     if context.has_key('normal_postage') or context.has_key('express_postage') or context.has_key('domestic_shipping_charge'):
#         if delivery_speed == "Priority Mail":
#             courier_cost_D = float(context['normal_postage'])
#         elif delivery_speed == "Priority Mail Express":
#             courier_cost_D = float(context['express_postage'])
#         else:
#             courier_cost_D = float(context['domestic_shipping_charge'])
#
#         request.session['courier_cost_D'] = courier_cost_D
#
#         #retrieve values from session
#         dim_weight_lbs  = request.session['pkg_weight_lbs']
#         naira_value     = request.session['naira_value']
#         drop_off        = request.session['drop_off_state']
#         export_cost_calc = ExportPackageCostCalc(dim_weight_lbs, None, drop_off, naira_value, courier_cost_D)
#         local_freight_D, local_freight_N = export_cost_calc.localFreight()
#         intl_freight_D, intl_freight_N = export_cost_calc.internationalFreight()
#
#         total_shipping_cost_D = local_freight_D + intl_freight_D
#         total_shipping_cost_N = local_freight_N + intl_freight_N
#
#         #print total_shipping_cost_D, total_shipping_cost_N
#         context.update({'total_shipping_cost_D': total_shipping_cost_D,
#                          'total_shipping_cost_N': total_shipping_cost_N})
#     print 'context 2: ',context
#     return JsonResponse(context)





# def process_api_response(request, xml_response, delivery_speed, action ):
#     print 'xml_response: ',xml_response
#     context = {}
#     context['got_response']   =   True
#     context['action']         =   action
#     try:
#         root = ET.fromstring(xml_response)
#     except:
#         return HttpResponse("Could not parse XML object")

#     if action == "ShippingEstimate":
#         try:
#             # International shipping
#             context["has_express_speed"]    =   True
#             context["has_normal_speed"]     =   True
#             #  Normal delivery
#             if delivery_speed in ["Priority Mail", "Online"]:
#                 print "root.findall('country')",root.findall(".//Service[@ID='2']/Country")[0]
#                 try:
#                     # print "second try"
#                     context['destination']          =   root.findall(".//Service[@ID='2']/Country")[0].text
#                     #context['normal_postage']      =   root.findall(".//Service[@ID='2']/Postage")[0].text
#                     context['duration']             =   root.findall(".//Service[@ID='2']/SvcCommitments")[0].text
#                     context['shipping_charge']      =   root.findall(".//Service[@ID='2']/CommercialPostage")[0].text
#                     context['normal_desc']          =   root.findall(".//Service[@ID='2']/SvcDescription")[0].text.split('&')[0]
#                 except Exception as e:
#                     print 'e1: ',e
#                     context["has_normal_speed"]  =  False

#             if delivery_speed == "Priority Mail Express":
#                 # Express delivery
#                 try:
#                     # print "third try"
#                     context['destination']          =   root.findall(".//Service[@ID='1']/Country")[0].text
#                     #context['express_postage']      =   root.findall(".//Service[@ID='1']/Postage")[0].text
#                     context['duration']             =   root.findall(".//Service[@ID='1']/SvcCommitments")[0].text
#                     context['shipping_charge']      =   root.findall(".//Service[@ID='1']/CommercialPostage")[0].text
#                     context['express_desc']         =   root.findall(".//Service[@ID='1']/SvcDescription")[0].text.split('&')[0]
#                 except Exception as e:
#                     print 'e2: ',e
#                     context["has_express_speed"]    =   False

#         except Exception as e:
#             print 'exception: ',e
#             #  Domestic shipping
#             try:
#                 context['description']        =   root.findall(".//Postage[@CLASSID='1']/MailService")[0].text.split('&')[0]
#                 context['shipping_charge']    =   root.findall(".//Postage[@CLASSID='1']/Rate")[0].text
#             except Exception as e:
#                 print 'e3: ',e
#                 context['description']        =   root.findall(".//Postage[@CLASSID='3']/MailService")[0].text.split('&')[0]
#                 context['shipping_charge']    =   root.findall(".//Postage[@CLASSID='3']/Rate")[0].text
#             context['domestic_shipping']           =   True

#     #print 'context 1: ',context
#     # if context.has_key('normal_postage') or context.has_key('express_postage') or context.has_key('domestic_shipping_charge'):
#     #     if delivery_speed == "Priority Mail":
#     #         courier_cost_D = float(context['normal_postage'])
#     #     elif delivery_speed == "Priority Mail Express":
#     #         courier_cost_D = float(context['express_postage'])
#     #     else:
#     courier_cost_D = float(context['shipping_charge'])
#     request.session['courier_cost_D'] = courier_cost_D
#     #print 'context: ',context
#     #retrieve values from session
#     dim_weight_lbs  = request.session['pkg_weight_lbs']
#     naira_value     = request.session['naira_value']
#     drop_off_state        = request.session['drop_off_state']
#     drop_off_country      = request.session['drop_off_country']
#     costcalc = marketingmember_costcalc(request)
#     lb_kg_factor = 0.45359
#     weight_kg = dim_weight_lbs * lb_kg_factor

#     origin = 'United States'
#     destination = 'Nigeria'
#     shipping_rate_air_D = get_marketing_member_shipping_rate(request, origin, destination, 'air', weight_kg)
#     local_freight_cost_D, local_freight_cost_N = get_local_freight_from_state(request, dim_weight_lbs, drop_off_state, drop_off_country)
#     #print "local_freight_cost_D, local_freight_cost_N : ",local_freight_cost_D, local_freight_cost_N
#     export_cost_calc = ExportPackageCostCalc(dim_weight_lbs, None, drop_off_state, naira_value, courier_cost_D, shipping_rate_air_D, local_freight_cost_D, costcalc)
#     local_freight_D, local_freight_N = export_cost_calc.localFreight()
#     intl_freight_D, intl_freight_N = export_cost_calc.internationalFreight()

#     local_intl_freight_cost_D = local_freight_D + intl_freight_D
#     local_intl_freight_cost_N = local_freight_N + intl_freight_N
#     #print "total_shipping_cost_D, total_shipping_cost_N: ",total_shipping_cost_D, total_shipping_cost_N

#     context.update({'local_intl_freight_cost_D': local_intl_freight_cost_D,
#                      'local_intl_freight_cost_N': local_intl_freight_cost_N})

#     #print 'context 2: ',context
#     return JsonResponse(context)





def process_api_response(request, xml_response, delivery_speed, action ):
    #print 'xml_response: ',xml_response
    context = {}
    context['got_response']   =   True
    context['action']         =   action
    try:
        root = ET.fromstring(xml_response)
    except:
        return HttpResponse("Could not parse XML object")
    if action == "ShippingEstimate":
        try:
            # International shipping
            context["has_express_speed"]    =   True
            context["has_normal_speed"]     =   True
            # if delivery_speed in ["Priority Mail", "Online"]:
            try:
                context['destination']          =   root.findall(".//Service[@ID='2']/Country")[0].text
                context['duration']             =   root.findall(".//Service[@ID='2']/SvcCommitments")[0].text
                context['shipping_charge']      =   root.findall(".//Service[@ID='2']/CommercialPostage")[0].text
                context['normal_desc']          =   root.findall(".//Service[@ID='2']/SvcDescription")[0].text.split('&')[0]
            except Exception as e:
                context['destination']          =   root.findall(".//Service[@ID='1']/Country")[0].text
                context['duration']             =   root.findall(".//Service[@ID='1']/SvcCommitments")[0].text
                context['shipping_charge']      =   root.findall(".//Service[@ID='1']/CommercialPostage")[0].text
                context['express_desc']         =   root.findall(".//Service[@ID='1']/SvcDescription")[0].text.split('&')[0]
        except Exception as e:
            try:
                context['description']        =   root.findall(".//Postage[@CLASSID='1']/MailService")[0].text.split('&')[0]
                context['shipping_charge']    =   root.findall(".//Postage[@CLASSID='1']/Rate")[0].text
            except Exception as e:
                print 'e3: ',e
                context['description']        =   root.findall(".//Postage[@CLASSID='3']/MailService")[0].text.split('&')[0]
                context['shipping_charge']    =   root.findall(".//Postage[@CLASSID='3']/Rate")[0].text
            context['domestic_shipping']           =   True


    courier_cost_D                      = float(context['shipping_charge'])
    print 'usps_helper|courier_cost_D: ',courier_cost_D
    request.session['courier_cost_D']   = courier_cost_D
    higher_weight_lbs                   = request.session['pkg_weight_lbs']
    naira_value                         = request.session['naira_value']
    drop_off_state                      = request.session['drop_off_state']
    drop_off_country                    = request.session['drop_off_country']
    costcalc                            = marketingmember_costcalc(request)
    lb_kg_factor                        = 0.45359
    weight_kg                           = higher_weight_lbs * lb_kg_factor

    #origin                              = request.session['shipping_destination']
    #destination                         = request.session['shipping_origin']

    origin                              = 'United States'
    destination                         = 'Nigeria'

    drop_off_id                         = request.session['drop_off_id']

    user_special_rate = has_special_rate_for_route(request, origin, destination, 'air')
    if user_special_rate[0] == True:
        shipping_rate_air_D = user_special_rate[1]
        print 'export|user_special_rate|air|shipping_rate_D: ',shipping_rate_air_D
    else:
        shipping_rate_air_D     = get_marketing_member_shipping_rate(request, origin, destination, 'air', weight_kg)

    #local_freight_cost_D, local_freight_cost_N = get_local_freight_from_state(request, dim_weight_lbs, drop_off_state, drop_off_country)
    local_freight_cost_D, local_freight_cost_N = get_local_freight_from_state(request, higher_weight_lbs, drop_off_id)
    print 'local_freight_cost_D, local_freight_cost_N : ',local_freight_cost_D, local_freight_cost_N

    export_cost_calc                    = ExportPackageCostCalc(request, higher_weight_lbs, None, drop_off_state, naira_value, courier_cost_D, shipping_rate_air_D, local_freight_cost_D, costcalc)

    service_charge_D, service_charge_N  = export_cost_calc.serviceCharge()

    local_freight_D, local_freight_N    = export_cost_calc.localFreight()
    intl_freight_D, intl_freight_N      = export_cost_calc.internationalFreight()

    #local_intl_freight_cost_D           = local_freight_D + intl_freight_D
    #local_intl_freight_cost_N           = local_freight_N + intl_freight_N

    local_intl_freight_cost_D           = local_freight_cost_D + intl_freight_D + service_charge_D
    local_intl_freight_cost_N           = local_freight_cost_N + intl_freight_N + service_charge_N

    context.update({'local_intl_freight_cost_D': local_intl_freight_cost_D,
                     'local_intl_freight_cost_N': local_intl_freight_cost_N})
    return JsonResponse(context)





def process_error_response(request, xml_response):
    root = ET.fromstring(xml_response)
    try:
        error_msg = root.findall(".//Error/Description")[0].text
    except Exception as e:
        print 'e: ',e
        error_msg = 'Oops! Something went wrong. Please try again'
    print 'error_msg: ',error_msg
    return JsonResponse({'error_msg': error_msg})




def usps_query(request):
    rp = request.POST
    try:
        r = requests.post(get_url(request, rp['action']), headers = {'Content-Type': 'application/xml'})
        if r.status_code == 200:
            try:
                return process_api_response(request, r.content,  rp['usps_delivery_speed'], rp['action'])
            except Exception as e:
                print "this is the error line e", e
                return process_error_response(request, r.content) # attempt error processing
        else:
            pass
    except Exception as e:
        return JsonResponse({'error_msg': "Connection Timeout. Please review your internet settings and try again."})






# ------------------------------------------------------------------------------
#    SHIPPING ESTIMATE

def get_url_for_estimate(request, weight_lbs):
    rp = request.POST
    url = "http://production.shippingapis.com/ShippingApi.dll?API="
    xml = ""
    USERID          = "250CIRCU3854"
    item_container  = 'Rectangular'

    if rp['country_to'].lower() == "united states":
        mail_type       = 'Letter'
    else:
        mail_type = 'Package'
    size            = 'Large' #Regular/Large
    originZipCode   = rp['zip_code_from']
    destZipCode     = rp["zip_code_to"]
    if rp['country_to'].lower() == "usa" or rp['country_to'].lower() == "united states":
        API_name = "RateV4"
        request_type = "RateV4Request"
        zipdestination = "<ZipDestination>" + destZipCode + "</ZipDestination>"
        ounce_weight = float(weight_lbs) * 16
        # print "ounce weight ", ounce_weight
        xml += API_name + '''&XML=<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
        <''' + request_type + ''' USERID="''' + USERID + '''">
        <Revision>2</Revision>
        <Package ID="0">
        <Service>''' + rp['usps_delivery_speed'] + '''</Service><FirstClassMailType>''' + mail_type + '''</FirstClassMailType>
        <ZipOrigination>''' + originZipCode + '''</ZipOrigination>''' + destZipCode + '''
        <Pounds> ''' + str(weight_lbs) + '''</Pounds>
        <Ounces>''' + str(ounce_weight) + '''</Ounces>
        <Container>''' + item_container + '''</Container>
        <Size>''' + size + '''</Size>
        <Width>''' + rp['box_width'] + '''</Width>
        <Length>''' + rp['box_length'] + '''</Length>
        <Height>''' + rp['box_height'] + '''</Height>
        <Value>''' + rp['value_of_item'] + '''</Value>
        <Machinable>True</Machinable>
        </Package>
        </''' + request_type + '''>'''
    else:
        # print "it came here instaed . . ."
        API_name        = "IntlRateV2"
        request_type    = "IntlRateV2Request"
        ounce_weight = float(weight_lbs) * 16
        # print "ounce weight ", ounce_weight
        xml += API_name + '''&XML=<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
        <''' + request_type + ''' USERID="''' + USERID + '''">
        <Revision>2</Revision>
        <Package ID="0">
        <Pounds> ''' + str(weight_lbs) + '''</Pounds>
        <Ounces>''' + str(ounce_weight) + '''</Ounces>
        <Machinable>True</Machinable>
        <MailType>''' + mail_type + '''</MailType>
        <ValueOfContents>''' + rp['value_of_item'] + '''</ValueOfContents>
        <Country>''' + rp['country_to'] + '''</Country>
        <Container>''' + item_container + '''</Container>
        <Size>''' + size + '''</Size>
        <Width>''' + rp['box_width'] + '''</Width>
        <Length>''' + rp['box_length'] + '''</Length>
        <Height>''' + rp['box_height'] + '''</Height>
        <Girth>0</Girth>
        <OriginZip>''' + originZipCode + '''</OriginZip>
        <CommercialFlag>Y</CommercialFlag>
        <ExtraServices>
        <ExtraService>1</ExtraService>
        </ExtraServices>
        </Package>
        </''' + request_type + '''>'''
    return url + xml



def usps_estimate(request, weight_lbs):
    rp = request.POST

    r = requests.post(get_url_for_estimate(request, weight_lbs), headers = {'Content-Type': 'application/xml'})
    if r.status_code == 200:
        # print r.content
        try:
            return process_api_estimate_response(request, r.content,  rp['usps_delivery_speed'])
        except Exception as e:
            print "this is the error line e", e
            return process_error_response(request, r.content) # attempt error processing
    else:
        pass
    return JsonResponse({'error_msg': "Connection Timeout. Please review your internet settings and try again."})


def process_api_estimate_response(request, xml_response, delivery_speed):
    context = {}
    context['got_response']   =   True
    try:
        root = ET.fromstring(xml_response)
    except:
        return HttpResponse("Could not parse XML object")
    try:
        # International shipping
        context["has_express_speed"]    =   True
        context["has_normal_speed"]     =   True
        #  Normal delivery
        if delivery_speed in ["Priority Mail", "Online","Priority Mail Express"]:
            # print "root.findall('country')", root.findall(".//Service[@ID='2']/Country")[0]
            try:
                context['destination']          =   root.findall(".//Service[@ID='2']/Country")[0].text
                context['duration']             =   root.findall(".//Service[@ID='2']/SvcCommitments")[0].text
                context['shipping_charge']      =   root.findall(".//Service[@ID='2']/CommercialPostage")[0].text
                context['normal_desc']          =   root.findall(".//Service[@ID='2']/SvcDescription")[0].text.split('&')[0]
            except:
                context["has_normal_speed"]  =  False
        if delivery_speed == "Priority Mail Express":
            try:
                context['destination']          =   root.findall(".//Service[@ID='1']/Country")[0].text
                context['duration']             =   root.findall(".//Service[@ID='1']/SvcCommitments")[0].text
                context['shipping_charge']      =   root.findall(".//Service[@ID='1']/CommercialPostage")[0].text
                context['express_desc']         =   root.findall(".//Service[@ID='1']/SvcDescription")[0].text.split('&')[0]
            except:
                context["has_express_speed"]    =   False
    except Exception as e:
        try:
            context['description']        =   root.findall(".//Postage[@CLASSID='1']/MailService")[0].text.split('&')[0]
            context['shipping_charge']    =   root.findall(".//Postage[@CLASSID='1']/Rate")[0].text
        except:
            context['description']        =   root.findall(".//Postage[@CLASSID='3']/MailService")[0].text.split('&')[0]
            context['shipping_charge']    =   root.findall(".//Postage[@CLASSID='3']/Rate")[0].text
        context['domestic_shipping']           =   True
    courier_cost_D = float(context['shipping_charge'])
    print 'cost:', courier_cost_D
    return courier_cost_D





# -------------------------------------------------------------
#  PACKAGE PICKUP CHARGE


def build_packages_xml(pkg_dict): #build xml url for usps API from package(s) information
    url = "http://production.shippingapis.com/ShippingApi.dll?API="
    xml = ""
    USERID          =  "250CIRCU3854" #"593CIRCU5990"
    item_container  =  'Rectangular'
    mail_type       =  'Package'
    size            =  'Large' #Regular/Large
    API_name        =  "RateV4"
    request_type    =  "RateV4Request"
    xml += API_name +  '''&XML=<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
    <''' + request_type + ''' USERID="''' + USERID + '''">
    <Revision>2</Revision>'''
    counter = 0
    # for pkg_dict in pkg_info_dicts_list:
    counter = 1
    xml += '''<Package ID="''' + str(counter) + '''">
        <Service>''' + pkg_dict['usps_delivery_speed'] + '''</Service><FirstClassMailType>''' + mail_type + '''</FirstClassMailType>
        <ZipOrigination>''' + pkg_dict["originZipCode"] + '''</ZipOrigination><ZipDestination>''' +  pkg_dict["destZipCode"] + '''</ZipDestination>
        <Pounds> ''' + str(pkg_dict['weight_lbs']) + '''</Pounds>
        <Ounces>''' + str(float(pkg_dict['weight_lbs']) * 16) + '''</Ounces>
        <Container>''' + item_container + '''</Container>
        <Size>''' + size + '''</Size>
        <Width>''' + str(pkg_dict['box_width']) + '''</Width>
        <Length>''' + str(pkg_dict['box_length']) + '''</Length>
        <Height>''' + str(pkg_dict['box_height']) + '''</Height>
        <Value>''' + str(pkg_dict['value_of_content_D']) + '''</Value>
        <Machinable>True</Machinable>
    </Package>'''
    final_xml = url + xml + '''</''' + request_type + '''>'''
    print final_xml
    return final_xml


# def get_pkg_info_dict(packages_list,local_distributor):
#     pkg_info_dict = {}
#     all_pkg_info_list = []
#     for pkg in packages_list:
#         pkg_info_dict.update({'originZipCode':pkg.pickup_location.zip_code,'destZipCode':pkg.warehouse.zip_code,
#         'weight_lbs':pkg.box_weight_Dim,'usps_delivery_speed':"PRIORITY",'box_width':pkg.box_width,'box_length':pkg.box_length,
#         'box_height':pkg.box_height, 'value_of_content_D':pkg.total_package_value})
#         all_pkg_info_list.append(pkg_info_dict)
#     print "package dict ", all_pkg_info_list
#     return all_pkg_info_list


def get_pkg_info_dict(pkg, local_distributor, destZipCode):
    print "package weight .......", pkg.box_weight_Dim
    pkg_info_dict = {}

    try:
        try:
            originZipCode = pkg.pickup_location.zip_code
            print 'pkg.pickup_location.zip_code:',pkg.pickup_location.zip_code
        except:
            originZipCode = pkg.dropoff_postoffice.zip_code
            print 'pkg.dropoff_postoffice.zip_code:',pkg.dropoff_postoffice.zip_code
    except:
        try:
            originZipCode = pkg.delivery_address.zip_code
            print 'pkg.delivery_address.zip_code:',pkg.delivery_address.zip_code
        except:
            warehouse_location = WarehouseLocation.objects.get(zip_code=destZipCode)
            originZipCode = warehouse_location.zip_code
            print 'pkg.origin_warehouse.zip_code:',originZipCode

    pkg_info_dict.update({'originZipCode': originZipCode,'destZipCode':destZipCode,
    'weight_lbs':pkg.box_weight_Dim,'usps_delivery_speed':"PRIORITY",'box_width':pkg.box_width,'box_length':pkg.box_length,
    'box_height':pkg.box_height, 'value_of_content_D':pkg.total_package_value})
    return pkg_info_dict


# def extract_calc_pkgs_shipping_rate(xml_response):
#     total_charge = 0.0
#     root = ET.fromstring(xml_response)
#     pkg_info = root.findall(".//Package/Postage/Rate")
#     # print "root: ", root
#     for info in pkg_info:
#         total_charge += float(info.text)
#     return total_charge


def extract_calc_pkgs_shipping_rate(xml_response):
    total_charge = 0.0
    root = ET.fromstring(xml_response)
    total_charge = root.findall(".//Package/Postage/Rate")[0].text
    return total_charge


# def get_pickup_charge(request, packages_list,local_distributor):
#     print "getting pick up charge"

#     url = build_packages_xml(get_pkg_info_dict(packages_list,local_distributor))
#     r = requests.post(url, headers = {'Content-Type': 'application/xml'})
#     if r.status_code == 200:
#         try:
#             # print r.content
#             return extract_calc_pkgs_shipping_rate(r.content)
#         except Exception as e:
#             return process_error_response(request, r.content) # attempt error processing



def get_pickup_charge(request, package,local_distributor, destZipCode):
    url = build_packages_xml(get_pkg_info_dict(package, local_distributor, destZipCode))
    r = requests.post(url, headers = {'Content-Type': 'application/xml'})
    if r.status_code == 200:
        try:
            return extract_calc_pkgs_shipping_rate(r.content)
        except Exception as e:
            print "exception", e
            return process_error_response(request, r.content) # attempt error processing







# ---------------------------------------------------------------------------
# PACKAGE LABEL EXTRACTION

def build_xml_for_label(request, pkg, total_pkg_count, pickup_add, counter):
    print 'build_xml_for_label'
    WHaddress = request.session.get('WHaddress')
    print WHaddress
    Location = WarehouseLocation.objects.get(id=WHaddress)
    marketer = request.user.useraccount.marketer
    pkg_weight_lb = pkg.box_weight_Actual
    pkg_weight_ounce = pkg_weight_lb * 16
    future_date = timezone.now() + timezone.timedelta(days=2)

    pickup_add_state        = state_code_abbreviation(pickup_add.state, pickup_add.country)
    origin_warehouse_state  = state_code_abbreviation(Location.state, Location.country)

    xml = '''https://secure.shippingapis.com/ShippingAPI.dll?API=SignatureConfirmationV4&XML=<?xml version="1.0" encoding="UTF-8" ?>
    <SignatureConfirmationV4.0Request USERID="250CIRCU3854">
      <Option>1</Option>
      <ImageParameters>
        <LabelSequence>
          <PackageNumber>''' + str(counter) + '''</PackageNumber>
          <TotalPackages>''' + str(total_pkg_count) + '''</TotalPackages>
        </LabelSequence>
      </ImageParameters>
      <FromName>''' + request.user.get_full_name() + '''</FromName>
      <FromFirm> </FromFirm>
      <FromAddress1>''' + pickup_add.address_line1 + '''</FromAddress1>
      <FromAddress2>''' + pickup_add.address_line2 + '''</FromAddress2>
      <FromCity>''' + pickup_add.city + '''</FromCity>
      <FromState>''' + pickup_add_state + '''</FromState>
      <FromZip5>''' + pickup_add.zip_code + '''</FromZip5>
      <FromZip4></FromZip4>
      <ToName>''' + marketer.storefront_name + '''</ToName>
      <ToFirm>''' + marketer.storefront_name + '''</ToFirm>
      <ToAddress1>''' + Location.address1 + '''</ToAddress1>
      <ToAddress2> ''' + Location.address2 + '''</ToAddress2>
      <ToCity>''' + Location.city + '''</ToCity>
      <ToState>''' + origin_warehouse_state + '''</ToState>
      <ToZip5>''' + Location.zip_code + '''</ToZip5>
      <ToZip4></ToZip4>
      <WeightInOunces>''' + str(pkg_weight_ounce) + '''</WeightInOunces>
      <ServiceType>PRIORITY</ServiceType>
      <InsuredAmount></InsuredAmount>
      <SeparateReceiptPage></SeparateReceiptPage>
      <POZipCode></POZipCode>
      <ImageType>PDF</ImageType>
      <LabelDate></LabelDate>
      <CustomerRefNo></CustomerRefNo>
      <AddressServiceRequested></AddressServiceRequested>
      <SenderName>''' + request.user.get_full_name() + '''</SenderName>
      <SenderEMail>''' + request.user.email + '''</SenderEMail>
      <RecipientName></RecipientName>
      <RecipientEMail></RecipientEMail>
      <Container>Variable</Container>
      <Size>Regular</Size>
      <CommercialPrice>True</CommercialPrice>
    </SignatureConfirmationV4.0Request>'''
    print 'xml: ',xml
    return xml


def extract_image_string(xml_response):
    root = ET.fromstring(xml_response)
    print 'xml_response: ',xml_response
    try:
        img_str = root.findall(".//SignatureConfirmationLabel")[0].text
        return img_str
    except Exception as e:
        print 'extract_image_string|e: ',e
        #print 'xml_response: ',xml_response
        return xml_response


def post_label_request(request, url):
    r = requests.post(url, headers = {'Content-Type': 'application/xml'})
    if r.status_code == 200:
        # print r.content
        try:
            return extract_image_string(r.content)
        except Exception as e:
            return process_error_response(request, r.content) # attempt error processing


def print_label(request, pkg, total_pkg_count, pickup_add, counter):
    #print "print_label traking number ", pkg.tracking_number
    xml = build_xml_for_label(request, pkg, total_pkg_count, pickup_add, counter)
    #print 'xml: ',xml
    image_str =  post_label_request(request, xml)
    return convert_base64_to_image(image_str, str(pkg.tracking_number) + ".pdf")
