from models import ShippingPackage
from general.models import AddressBook
from general.modelfield_choices import WEIGHT_UNIT, LOCAL_DELIVERY_CHOICES, TITLE, STATE
from django import forms
from django.forms import ModelForm, TextInput, CharField, BooleanField
from shipping.models import *


class AddCustomPackageForm(forms.ModelForm):
    box_length          = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'inches', 'class': 'inp','required':'required', 'onblur':'return check_package_weight()'}), error_messages = {'required': 'Please provide length in inches.'})
    box_width           = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'inches', 'class': 'inp','required':'required','onblur':'return check_package_weight()' }), error_messages = {'required': 'Please provide width in inches.'})
    box_height          = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'inches', 'class': 'inp','required':'required','onblur':'return check_package_weight()' }), error_messages = {'required': 'Please provide height in inches.'})
    box_weight_Actual   = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'lbs or kg', 'class': 'inp','required':'required','onblur':'return check_package_weight()' }), error_messages = {'required': 'Please provide weight.'})
    # box_quantity      = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'integer', 'class': 'inp', }), error_messages = {'required': 'Please enter the quantity of your Box.'})
    weight_unit         = forms.ChoiceField(widget=forms.RadioSelect(attrs={'required':'required', 'onclick':'return check_package_weight()'}), choices = WEIGHT_UNIT, error_messages = {'required': 'Please select weight unit. lb or kg'})
    class Meta:
        model = ShippingPackage
        fields = ('box_length', 'box_width', 'box_height', 'box_weight_Actual','weight_unit',)


class BillMeLaterForm(forms.Form):
    do_later = forms.BooleanField(required=True)


class ShippingItemForm(forms.ModelForm):
    class Meta:
        model = ShippingItem
        fields = ['courier_tracking_number', 'description','amount_paid','description', 'status', 'status_2','balance', 'weight']


class AddressBookForm(forms.ModelForm):
    default_style       = {'class': 'form-control', 'style': 'border-color: #777 !important; background-color: white !important; color: black;', 'required': 'true'}
    title               = forms.ChoiceField(choices=TITLE, widget=forms.Select(attrs=default_style))
    first_name          = forms.CharField(widget=forms.TextInput(attrs=default_style))
    last_name           = forms.CharField(widget=forms.TextInput(attrs=default_style))
    address_line1       = forms.CharField(widget=forms.TextInput(attrs=default_style))
    address_line2       = forms.CharField(widget=forms.TextInput(attrs=default_style))
    city                = forms.CharField(widget=forms.TextInput(attrs=default_style))
    telephone           = forms.CharField(widget=forms.TextInput(attrs=default_style))
    zip_code            = forms.CharField(widget=forms.TextInput(attrs=default_style))
    # state             = forms.ChoiceField(choices=STATE, widget=forms.Select(attrs=default_style))
    # country           = forms.ChoiceField(choices=(('Nigeria', 'Nigeria'),), widget=forms.Select(attrs=default_style))
    state               = forms.ChoiceField(widget=forms.Select(attrs=default_style))
    country             = forms.ChoiceField(widget=forms.Select(attrs=default_style))

    def __init__(self, *args, **kwargs):
        #if kwargs.has_key('countries'):
        self.country    = kwargs.pop('country')
        self.states     = kwargs.pop('states')
        super(AddressBookForm, self).__init__(*args, **kwargs)
        self.fields['state'].choices = self.states
        self.fields['country'].choices = self.country

        # self.fields['state'].widget = forms.ModelChoiceField(
        #         choices  = self.states
        # )


    class Meta:
        model = AddressBook
        #exclude = ('user', 'cart_id', 'created_at', 'package_destination', 'shipment', 'postal_code',)
        fields = ('title', 'first_name', 'last_name', 'address_line1', 'address_line2', 'zip_code', 'city', 'state', 'country', 'telephone',)


class DeliveryMethodForm(forms.Form):
    delivery_method = forms.ChoiceField(widget=forms.RadioSelect, choices=LOCAL_DELIVERY_CHOICES)



class DockReceiptForm(forms.ModelForm):
    exporter_name_and_address = forms.CharField(help_text="Exporter Name and Address",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Exporter Name and Address', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    zip_code = forms.CharField(help_text = "Zip Code",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Zip Code', 'required':'required',  'style':'margin-left: 0px; margin-right: 0px; width: 460px;'}))
    consigned_to = forms.CharField(help_text="Consigned To",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Consigned To', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    notify_party_name_and_address = forms.CharField(help_text="Notify Party Name and Address",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Notify Party Name and Address', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    document_number = forms.CharField(help_text="Document Number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Document Number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    bl_or_awb_number = forms.CharField(help_text="Bill of Lading or AWB number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Bill of Lading or AWB number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    export_references = forms.CharField(help_text="Export References",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Export References', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    forwarding_agent_fmc_no = forms.CharField(help_text="Forwarding Agent FMC Number",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Forwarding Agent FMC Number', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    state_and_country_of_origin_or_ftz_number = forms.CharField(help_text="State and Country of Origin or FTZ number",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'State and Country of Origin or FTZ number', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    domestic_routing = forms.CharField(help_text="Domestic Routing / Export Instruction",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Domestic Routing / Export Instruction', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    loading_pier = forms.CharField(help_text="Loading Pier / Terminal",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Loading Pier / Terminal', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    type_of_move = forms.CharField(help_text="Type of Move",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Type of Move', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    containerized = forms.BooleanField(required=False, initial=False, label='Containerized')
    precarriage_by = forms.CharField(help_text="Pre-Carriage By",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Pre-Carriage By', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    place_of_receipt_by_precarrier = forms.CharField(help_text="Place of Receipt by Pre-Carrier",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Place of Receipt by Pre-Carrier', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    exporting_carrier = forms.CharField(help_text="Export Carrier",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Export Carrier', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    port_of_loading = forms.CharField(help_text="Port of Loading",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Port of Loading', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    foreign_port_of_unloading = forms.CharField(help_text="Foreign Port of Unloading",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Foreign Port of Unloading', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    place_of_delivery_by_oncarrier = forms.CharField(help_text="Place of Delivery by On-Carrier",widget=forms.TextInput(attrs={'class': "red", 'placeholder': 'Place of Delivery by On-Carrier', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    mks_nos = forms.CharField(help_text="MKS. & NOS./CONT. NOS.",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'MKS. & NOS./CONT. NOS.', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    no_of_pkgs = forms.CharField(help_text="Number of Packages",widget=forms.TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Number of Packages', 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    description_of_package_and_goods = forms.CharField(help_text="Description of Packages and Goods",widget=forms.Textarea(attrs={'class': "red", 'placeholder': 'Description of Packages and Goods', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    gross_weight = forms.CharField(help_text="Gross Weight",widget=forms.TextInput(attrs={'class': "red", 'type':'number', 'placeholder': 'Gross Weight', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    measurement = forms.CharField(help_text="Measurement",widget=forms.TextInput(attrs={'class': "red", 'type':'text', 'placeholder': 'Measurement', 'cols': 4, 'rows': 4, 'required':'required', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    lighter_truck = forms.CharField(help_text="Lighter Truck",widget=forms.TextInput(attrs={'placeholder': 'Lighter Truck', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # arrived_date = forms.DateField(help_text="Arrived Date",widget=forms.TextInput(attrs={'placeholder': 'Arrived Date', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # arrived_time = forms.TimeField(widget=widgets.AdminTimeWidget)
    # unloaded_date = forms.DateField(help_text="Unloaded Date",widget=forms.TextInput(attrs={'placeholder': 'Unloaded Date', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # unloaded_time =  forms.DateField(help_text="Unloaded Time",widget=forms.TextInput(attrs={'placeholder': 'Unloaded Time', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    checked_by = forms.CharField(help_text="Checked By",widget=forms.TextInput(attrs={'placeholder': 'Checked By', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    placed_location = forms.CharField(help_text="Placed Location",widget=forms.TextInput(attrs={'placeholder': 'Placed Location', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    receiving_clerk_name = forms.CharField(help_text="Receiving Clerk Name",widget=forms.TextInput(attrs={'placeholder': 'Receiving Clerk Name', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # date_from_receiving_clerk = forms.DateField(help_text="Arrived Date",widget=forms.TextInput(attrs={'placeholder': 'Lighter Truck', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))
    # created_on
    # created_by = forms.CharField(help_text="Created By",widget=forms.TextInput(attrs={'placeholder': 'Created By', 'style':'margin-left: 0px; margin-right: 0px; width: 460px; line-height: 20px; padding: 10px;'}))

    class Meta:
        model = DockReceipt
        fields = ('exporter_name_and_address','zip_code','consigned_to','notify_party_name_and_address','document_number','bl_or_awb_number','export_references','forwarding_agent_fmc_no','state_and_country_of_origin_or_ftz_number',
            'domestic_routing','loading_pier','type_of_move','containerized','precarriage_by','place_of_receipt_by_precarrier','exporting_carrier','port_of_loading','foreign_port_of_unloading','place_of_delivery_by_oncarrier','mks_nos',
            'no_of_pkgs','description_of_package_and_goods','gross_weight', 'measurement','lighter_truck','arrived_date','arrived_time','created_by','unloaded_date','unloaded_time','checked_by','placed_location','receiving_clerk_name','date_from_receiving_clerk')
        
        
        
        
 