from django import forms
from models import *
from general.modelfield_choices import MARKETER_COUNTRIES
from django.forms.formsets import BaseFormSet
from cities_light import models as world_geo_data
from sokohaliAdmin.models import CostCalcSettings
from service_provider.models import Subscriber


attrs1 = {'class': 'long_input', 'required': 'true'}
attrs2 = {'class': 'small_input', 'required': 'true'}
attrs2_1 = {'class': 'small_input small_left', 'required': 'true'}
attrs2_2 = {'class': 'small_input_1', 'required': 'true'}
attrs3 = {'class': 'form-control', 'style': 'height: 70px', 'required': 'true'}
attrs4 = {'class': 'form-control', 'style': 'height: 40px', 'required': 'true'}


class BaseOfferWarehouseForm(forms.ModelForm):

    warehouse_size   = forms.CharField(label="What is the size of your availabe warehouse space (in square feet)?", widget=forms.TextInput(attrs = attrs1))
    process_charge_per_kg   = forms.FloatField(label="How much will you charge to process each package (average is $1.00)", widget=forms.TextInput(attrs = attrs1))
    storage_charge_per_day   = forms.FloatField(label="How much will you charge per pound for storage each day (average is $0.10)?", widget=forms.TextInput(attrs = attrs1))

    working_hrs_start   = forms.CharField(label="Working hours starts from?", widget=forms.TextInput(attrs = attrs2_2))
    working_hrs_end     = forms.CharField(label="Working hours ends at?", widget=forms.TextInput(attrs = attrs2_2))

    offered_for_rent            = forms.BooleanField(label="Allow other businesses to rent this service?", required=False)
    auto_subscriber_approval    = forms.BooleanField(label="Override automatic approval for customers who want to rent this service?", help_text="You will get notice to approve customers yourself", required=False)
    publish_reviews             = forms.BooleanField(label="Make the reviews your customers leave for you public?", required=False)


    #auto_subscriber_approval = forms.ChoiceField(choices=Yes_or_No, widget=forms.Select(), required=True)
    #publish_reviews = forms.ChoiceField(choices=Yes_or_No, widget=forms.Select(), required=True)

    about_service     = forms.CharField(label="Describe your service (100 words)", widget=forms.Textarea(attrs = attrs3))


    class Meta:
        model = WarehouseMember
        fields = (#'name', 'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number',
                'warehouse_size', 'process_charge_per_kg', 'storage_charge_per_day', 'working_hrs_start',
                 'working_hrs_end', 'offered_for_rent', 'auto_subscriber_approval', 'publish_reviews', 'about_service', 'offered_for_rent',)

    def __init__(self, *args, **kwargs):
        #country = kwargs.pop('country')
        super(BaseOfferWarehouseForm, self).__init__(*args, **kwargs)
        fields_list = ['name', 'address1', 'address2', 'city', 'zip_code', 'phone_number',]
        #attrs = {'class': 'long_input', 'required': 'true'}
        for key in self.fields:
            if key in fields_list:
                self.fields[key].widget.attrs = attrs1
        #self.fields['country']  = forms.ChoiceField(choices=((country, country),))
        #self.fields['state']    = forms.ChoiceField(choices=[(r.name, r.name) for r in world_geo_data.Region.objects.filter(country__name = country)])


class MarketingMemberForm(forms.ModelForm):

    class Meta:
        model = MarketingMember
        fields = ('storefront', 'package_pickup', 'package_dropoff',)


class EditMarketingMemberForm(forms.ModelForm):
    terms_and_cond     = forms.CharField(widget=forms.Textarea(attrs = {'value':'Enter Terms and Conditions', 'placeholder':'Enter Terms and Conditions', 'autofocus':'autofocus'}))

    class Meta:
        model = MarketingMember
        fields = ('terms_and_cond',)


class EmailTextForm(forms.ModelForm):
    email_text = forms.CharField(widget=forms.Textarea(attrs = {'value':'Enter Text to be displayed at the bottom of Emails', 'placeholder':'Enter Text to be displayed at the bottom of Emails', 'autofocus':'autofocus'}))
    
    class Meta:
        model = MarketingMember
        fields = ('email_text',)
        
class FAQForm(forms.ModelForm):
    faq = forms.CharField(widget=forms.Textarea(attrs = {'value':'Construct your frequently Asked Questions page here', 'placeholder':'Construct your frequently Asked Questions page here', 'autofocus':'autofocus'}))
    
    class Meta:
        model = MarketingMember
        fields = ('faq',)
        

class StartSetupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StartSetupForm, self).__init__(*args, **kwargs)
        field_dict = {'storefront': 'container_div', 'bank_deposit': 'container_div1'}
        for field, div in field_dict.iteritems():
            self.fields[field].widget.attrs.update({'class': 'hide_show', 'div': div})

    class Meta:
        model = MarketingMember
        fields = ('storefront', 'package_pickup', 'package_dropoff', 'bank_deposit', 'card_payment', 'stripe', 'paypal',)


class BaseMarketingMemberInfo(forms.ModelForm):

    class Meta:
        model = MarketingMember
        fields = ('storefront_name', 'storefront_color', 'logo', 'ico',
                'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number', 'email',
                'facebook_link', 'twitter_link', 'googleplus_link',)


class MarketingMemberInfo(BaseMarketingMemberInfo):

    def clean_storefront_name(self):
        storefront_name = self.cleaned_data['storefront_name']
        if MarketingMember.objects.filter(storefront_name=storefront_name).exists():
            raise forms.ValidationError('This Storefront name is already taken, please provide another.')

        return storefront_name


class EditMarketingMemberInfo(BaseMarketingMemberInfo):

    def __init__(self, *args, **kwargs):
        super(EditMarketingMemberInfo, self).__init__(*args, **kwargs)
        self.fields['storefront_name'].widget.attrs.update({'readonly': 'readonly'})
        #self.fields.pop('storefront_name')


class PaymentServicesForm(forms.ModelForm):

    class Meta:
        model = MarketingMember
        fields = ('bank_deposit', 'card_payment', 'stripe', 'paypal',)


'''Offer Services form'''
class OfferWarehouseForm(BaseOfferWarehouseForm):
    company_name   = forms.CharField(label="What is the name of your warehouse",widget=forms.TextInput(attrs = attrs1))

    pass
    class Meta:
         model = WarehouseMember
         fields = (#'name', 'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number',
                  'company_name','warehouse_size', 'process_charge_per_kg', 'storage_charge_per_day','working_hrs_start',
                  'working_hrs_end', 'offered_for_rent', 'auto_subscriber_approval', 'publish_reviews', 'about_service', 'offered_for_rent',)


class OfferWarehouseLocationForm(forms.ModelForm):
    #name = forms.CharField(label="What is the name of your warehouse", widget=forms.TextInput(attrs=attrs1))
    address1 = forms.CharField(label="Address 1", widget=forms.TextInput(attrs=attrs4))
    address2 = forms.CharField(label="Address 2", widget=forms.TextInput(attrs=attrs4))
    city = forms.CharField(label="City", widget=forms.TextInput(attrs=attrs4))
    state = forms.CharField(label="State", widget=forms.TextInput(attrs=attrs4))
    country = forms.CharField(label="Country", widget=forms.TextInput(attrs=attrs4))
    phone_number = forms.CharField(label="Phone number", widget=forms.TextInput(attrs=attrs4))
    zip_code = forms.CharField(label="Zip Code", widget=forms.TextInput(attrs=attrs4))
    
    class Meta():
        model = WarehouseLocation
        fields = ('address1', 'address2','city', 'state', 'country', 'phone_number', 'zip_code')
        
    # def __init__(self, *args, **kwargs):
    #     super(OfferWarehouseLocationForm, self).__init__(*args, **kwargs)
    #     self.fields['country']  = forms.ChoiceField(choices=[(r.name, r.name) for r in world_geo_data.Country.objects.all()])
    #     #self.fields['state']    = forms.ChoiceField(choices=[(r.name, r.name) for r in world_geo_data.Region.objects.filter(country__name = self.country)])

class OfferShippingServiceForm(BaseOfferWarehouseForm):

    def __init__(self, *args, **kwargs):
        super(OfferShippingServiceForm, self).__init__(*args, **kwargs)        
        pops_list = ['warehouse_size', 'process_charge_per_kg']
        for field in pops_list:
            self.fields.pop(field)

    class Meta():
        model = ShippingMember
        fields = ('name', 'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number',
                'warehouse_size', 'storage_charge_per_day','working_hrs_start',
                 'working_hrs_end', 'offered_for_rent', 'auto_subscriber_approval', 'publish_reviews', 'about_service')
        
    # class Meta:
    #     model = ShippingMember
    #     fields = ("name", 'process_charge_per_kg', 'storage_charge_per_day', 'working_hrs_start',
    #               'working_hrs_end', 'auto_subscriber_approval', 'publish_reviews', 'about_service', 'offered_for_rent', )

class ShippingRouteForm(forms.ModelForm):
    origin      = forms.ChoiceField(choices = MARKETER_COUNTRIES,label="Origin")
    destination = forms.ChoiceField(choices = MARKETER_COUNTRIES,label="Destination")
    rate        = forms.FloatField(label="Shipping rate ($/lb)", widget=forms.TextInput(attrs=attrs4))
    
    class Meta():
        model = ShippingMemberRoute
        fields = ('origin', 'destination', 'rate',)


class OfferCustomClearingForm(BaseOfferWarehouseForm):

    #clearing_per_kg             = forms.CharField(label="How much do you charge to clear per KG? (Average is $1.50)", widget=forms.TextInput(attrs = attrs1))
    quote_per_cosignment        = forms.BooleanField(label="I quote for each consignment or batch?", required=True)

    def __init__(self, *args, **kwargs):
        super(OfferCustomClearingForm, self).__init__(*args, **kwargs)
        pops_list = ['warehouse_size', 'process_charge_per_kg']
        for field in pops_list:
            self.fields.pop(field)

    class Meta(BaseOfferWarehouseForm.Meta):
        fields = ('name', 'address1', 'address2', 'city', 'state', 'country', 'zip_code', 'phone_number',
                'warehouse_size', 'process_charge_per_kg', 'storage_charge_per_day','working_hrs_start', 'working_hrs_end',
                  'offered_for_rent', 'quote_per_cosignment','auto_subscriber_approval', 'publish_reviews', 'about_service',)
        
        # fields_list = list(BaseOfferWarehouseForm.Meta.fields)
        # fields_list.insert(11, 'clearing_per_kg')
        # fields_list.insert(12, 'quote_per_cosignment')
        # #cast list back to tuple
        # fields = tuple(fields_list)
        model = CustomClearingAgent
        
        
class ClearingLocationForm(forms.ModelForm):
    country = forms.ChoiceField(choices = MARKETER_COUNTRIES,label="Country")
    price   = forms.CharField(label="Price per Kg($)", widget=forms.TextInput(attrs=attrs4))
    
    class Meta():
        model = ClearingPrice
        fields = ('country', 'price',)

    # class Meta:
    #     model = CustomClearingAgent
    #     fields = ('name', 'clearing_per_kg', 'storage_charge_per_day', 'working_hrs_start',
    #               'working_hrs_end', 'auto_subscriber_approval', 'publish_reviews', 'about_service', 'offered_for_rent',)
        #widgets = {'country': forms.HiddenInput()}

# class OfferCustomClearingForm(forms.ModelForm):
#     attrs1 = {'class': 'long_input', 'required': 'true'}
#     attrs2 = {'class': 'small_input', 'required': 'true'}
#     attrs2_1 = {'class': 'small_input small_left', 'required': 'true'}
#     attrs3 = {'class': 'form-control', 'style': 'height: 70px', 'required': 'true'}
#     attrs2_2 = {'class': 'small_input_1', 'required': 'true'}
#     name   = forms.CharField(widget=forms.TextInput(attrs = attrs1))
#     clearing_per_kg   = forms.CharField(widget=forms.TextInput(attrs = attrs1))
#     #storage_per_pound_per_day   = forms.FloatField(widget=forms.TextInput(attrs = attrs1))
#     storage_per_pound_per_day   = forms.FloatField(widget=forms.TextInput(attrs = attrs1))
#
#     working_hrs_start   = forms.CharField(widget=forms.TextInput(attrs = attrs2_2))
#     working_hrs_end     = forms.CharField(widget=forms.TextInput(attrs = attrs2_2))
#
#     about_service     = forms.CharField(widget=forms.Textarea(attrs = attrs3))
#
#     class Meta:
#         model = CustomClearingAgent
#         fields = ('name', 'clearing_per_kg', 'storage_per_pound_per_day', 'working_hrs_start',
#                   'working_hrs_end', 'auto_subscriber_approval', 'publish_reviews', 'about_service', 'offered_for_rent',)
#         #widgets = {'country': forms.HiddenInput()}
'''End Offer Services form'''


'''Rent Offer Services form'''
class RentServiceForm(forms.ModelForm):
    

    class Meta:
        model = ShippingChain
        fields = ('origin_warehouse', 'destination_warehouse',  'shipper', #'origin_shipper', 'destination_shipper',
                'origin_distributor', 'destination_distributor', 'clearing_agent', )#'origin_clearing_agent', 'destination_clearing_agent',)

    def __init__(self, *args, **kwargs):
        origin      = kwargs.pop('origin')
        destination = kwargs.pop('destination')
        subscriber = kwargs.pop('subscriber')
        super(RentServiceForm, self).__init__(*args, **kwargs)
        self.fields['origin_warehouse'].queryset            = WarehouseMember.objects.filter(warehouselocation__country = origin, offered_for_rent = True).distinct()
        self.fields['destination_warehouse'].queryset       = WarehouseMember.objects.filter(warehouselocation__country = destination, offered_for_rent = True).distinct()
         
        self.fields['shipper'].queryset                     = ShippingMember.objects.filter(shippingmemberroute__origin = origin, shippingmemberroute__destination = destination, offered_for_rent = True).distinct()

        #self.fields['origin_shipper'].queryset              = ShippingMember.objects.filter(country = origin, offered_for_rent = True)
        #self.fields['destination_shipper'].queryset         = ShippingMember.objects.filter(country = destination, offered_for_rent = True)

        self.fields['origin_distributor'].queryset          = LocalDistributionMember.objects.filter(country__name = origin, active=True)
        self.fields['destination_distributor'].queryset     = LocalDistributionMember.objects.filter(country__name = destination, active=True)
        
        self.fields['clearing_agent'].queryset              = CustomClearingAgent.objects.filter(clearingprice__country = destination, offered_for_rent = True).distinct()
        #self.fields['origin_clearing_agent'].queryset       = CustomClearingAgent.objects.filter(country = origin, offered_for_rent = True)
        #self.fields['destination_clearing_agent'].queryset  = CustomClearingAgent.objects.filter(country = destination, offered_for_rent = True)
        # for key in self.fields:
        #     if key in ['origin_warehouse','destination_warehouse', 'shipper', 'clearing_agent']:
        #         service = self.fields[key].queryset
        #         for i in service:
        #             if i.offered_by == subscriber:
        #                 self.fields[key].initial = i
        #                 print self.fields[key].initial
        #             else:
        #                 self.initial[key] = ''

# class RentDestinationWarehouseForm(forms.ModelForm):
#
#     class Meta:
#         model = WarehouseMember
#         fields = ('destination_warehouse',)
#
#     def __init__(self, *args, **kwargs):
#         country = kwargs.pop('country')
#         self.fields['destination_warehouse'].queryset = Warehouse.objects.filter(country = country, offered_for_rent = True)
'''End Rent Offer Services form'''

class BankAccountForm(forms.ModelForm):
    bank            = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Bank Name'}), required=True)
    account_name    = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Account Name'}), required=True)
    account_no      = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Account Number'}), required=True)

    class Meta:
        model = BankAccount
        fields = ('bank', 'account_name', 'account_no', 'currency',)

class ShippingRateForm(forms.ModelForm):
    #direction            = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Direction'}), required=True)
    #shipping_method      = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Shipping Method'}), required=True)
    weight_unit           = forms.CharField(widget=forms.TextInput(attrs={'value': 'lbs', 'style': 'width: 41%;', 'readonly': 'readonly'}))

    def __init__(self, *args, **kwargs):
        marketer = kwargs.pop('marketer')
        super(ShippingRateForm, self).__init__(*args, **kwargs)
        self.fields['shipping_chain'].queryset=marketer.get_shipping_chains()
        for key in self.fields:
            self.fields[key].widget.attrs['required'] = 'True'
            if key in ['shipping_chain', 'shipping_method']:
                self.fields[key].widget.attrs['class'] = 'route_sm'
            if key in ['shipping_chain', 'to_range', 'rate_D']:
                self.initial[key] = ''

        self.fields['from_range'].widget.attrs['readonly'] = 'readonly'


    class Meta:
        model = ShippingRate
        fields = ('shipping_chain', 'shipping_method', 'weight_unit', 'from_range', 'to_range', 'rate_D')
        
        
class CostCalcSettingsForm(forms.ModelForm):
    country                 = forms.ChoiceField(choices = MARKETER_COUNTRIES,label="Select Country")
    dollar_exchange_rate    = forms.CharField(widget=forms.TextInput(attrs=attrs4), label="Dollar Exchange Rate")
    vat_rate                = forms.CharField(widget=forms.TextInput(attrs=attrs4), label="VAT Rate(%)")
    insurance_rate          = forms.CharField(widget=forms.TextInput(attrs=attrs4), label="Insurance Rate(%)")
    handling_charge_fee     = forms.CharField(widget=forms.TextInput(attrs=attrs4), label="Handling Charge Fee($)")
    
    class Meta:
        model = CostCalcSettings
        fields = ('country', 'dollar_exchange_rate', 'vat_rate', 'insurance_rate', 'handling_charge_fee')

    # def __init__(self, *args, **kwargs):
    #     subscriber = kwargs.pop('subscriber')
    #     super(CostCalcSettingsForm, self).__init__(*args, **kwargs)
    #     self.fields['country'].queryset = ShippingChain.objects.filter(subscriber=subscriber)



